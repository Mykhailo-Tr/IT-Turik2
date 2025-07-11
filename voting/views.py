from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .forms import VoteForm, VoteCreateForm, VoteOptionFormSet
from .models import Vote, VoteOption, VoteAnswer
from accounts.models import User, Student
from notifications.models import Notification
from notifications.utils import trigger_user_notification, notify_vote_creation


def send_vote_update(vote_id: int):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"vote_{vote_id}",
        {
            "type": "vote_update"
        }
    )

class VoteListView(ListView):
    model = Vote
    template_name = "voting/vote_list.html"
    context_object_name = "votes"

    def get_queryset(self):
        user = self.request.user
        filter_option = self.request.GET.get("filter")
        now = timezone.now()

        class_group_ids = user.student.class_groups.values_list("id", flat=True) if hasattr(user, 'student') else []

        base_qs = Vote.objects.all() if user.role in ["director", "admin"] else Vote.objects.filter(
            Q(level=Vote.Level.SCHOOL) |
            Q(level=Vote.Level.CLASS, class_groups__in=class_group_ids) |
            Q(level=Vote.Level.TEACHERS, creator__role="teacher") |
            Q(level=Vote.Level.SELECTED, participants=user)
        ).distinct()

        if filter_option == "active":
            base_qs = base_qs.filter(
                Q(start_date__isnull=True, end_date__isnull=True) |
                Q(start_date__lte=now, end_date__isnull=True) |
                Q(start_date__isnull=True, end_date__gte=now) |
                Q(start_date__lte=now, end_date__gte=now)
            )
        elif filter_option == "voted":
            base_qs = base_qs.filter(options__answers__voter=user).distinct()
        elif filter_option == "finished":
            base_qs = base_qs.filter(end_date__lt=now)

        return base_qs.order_by("-start_date", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voted_ids = VoteAnswer.objects.filter(voter=self.request.user).values_list("option__vote_id", flat=True)
        context["voted_ids"] = set(voted_ids)
        context["current_filter"] = self.request.GET.get("filter", "")
        return context


@login_required
def vote_detail_view(request, pk):
    vote = get_object_or_404(Vote, pk=pk)
    user = request.user

    if vote.level == Vote.Level.SELECTED and user not in vote.participants.all():
        messages.error(request, "Ви не можете голосувати в цьому голосуванні.")
        return redirect("vote_list")

    already_voted = VoteAnswer.objects.filter(voter=user, option__vote=vote).exists()
    can_vote = vote.is_active() and not already_voted
    form = VoteForm(vote, request.POST) if request.method == "POST" and can_vote else VoteForm(vote) if can_vote else None

    if request.method == "POST" and can_vote:
        if form.is_valid():
            selected_ids = form.cleaned_data["options"]
            selected_ids = [selected_ids] if not isinstance(selected_ids, list) else selected_ids

            for option_id in selected_ids:
                option = get_object_or_404(VoteOption, id=option_id, vote=vote)
                VoteAnswer.objects.create(voter=user, option=option)
            send_vote_update(vote.pk)
            
            messages.success(request, "Ваш голос успішно враховано.")
            return redirect("vote_detail", pk=vote.pk)
        else:
            messages.error(request, "Помилка при обробці голосу. Спробуйте ще раз.")

    eligible_users = _get_eligible_users(vote)
    voted_users = User.objects.filter(vote_answers__option__vote=vote).distinct()

    user_can_see_votes = user == vote.creator or user.role in ["director", "admin"] or already_voted or not vote.is_active()

    options = vote.options.annotate(vote_count=Count("answers")).select_related("vote")
    for option in options:
        option.voted_users = User.objects.filter(vote_answers__option=option) if user_can_see_votes else []

    option_voted_users_dict = {
        option.id: list(User.objects.filter(vote_answers__option=option))
        for option in vote.options.all()
    } if user_can_see_votes else {}

    return render(request, "voting/vote_detail.html", {
        "vote": vote,
        "form": form,
        "can_vote": can_vote,
        "already_voted": already_voted,
        "options": options,
        "eligible_users": eligible_users,
        "voted_users": voted_users,
        "user_can_see_votes": user_can_see_votes,
        "option_voted_users_dict": option_voted_users_dict,
    })


def _get_eligible_users(vote):
    if vote.level == Vote.Level.SELECTED:
        return vote.participants.all()
    elif vote.level == Vote.Level.TEACHERS:
        return User.objects.filter(role="teacher", teacher__groups__in=vote.teacher_groups.all()).distinct()
    elif vote.level == Vote.Level.CLASS:
        students = Student.objects.filter(class_groups__in=vote.class_groups.all())
        return User.objects.filter(student__in=students)
    return User.objects.all()


@method_decorator(login_required, name="dispatch")
class VoteCreateView(View):

    def get(self, request):
        vote_form = VoteCreateForm(user=request.user)
        formset = VoteOptionFormSet(initial=[
            {"text": "Так"},
            {"text": "Ні"},
            {"text": "Утримуюсь"}
        ])
        return render(request, "voting/create.html", {
            "vote_form": vote_form,
            "formset": formset
        })

    def post(self, request):
        vote_form = VoteCreateForm(request.POST, user=request.user)
        formset = VoteOptionFormSet(request.POST)

        if vote_form.is_valid() and formset.is_valid():
            vote = vote_form.save(commit=False)
            vote.creator = request.user
            vote.save()
            vote_form.save_m2m()

            if vote.level == Vote.Level.SELECTED:
                vote.participants.add(request.user)

            for form in formset:
                text = form.cleaned_data.get("text")
                is_correct = form.cleaned_data.get("is_correct", False)
                if text:
                    VoteOption.objects.create(vote=vote, text=text, is_correct=is_correct)

            notify_vote_creation(vote)
                         
            messages.success(request, "Голосування успішно створено!")
            return redirect("vote_detail", pk=vote.pk)

        messages.error(request, "Помилка при створенні голосування. Перевірте форму.")
        return render(request, "voting/create.html", {
            "vote_form": vote_form,
            "formset": formset
        })


@require_POST
@login_required
def vote_delete_view(request, pk):
    vote = get_object_or_404(Vote, pk=pk)
    if vote.creator != request.user and request.user.role not in ["director", "admin"]:
        return HttpResponseForbidden("У вас немає прав на видалення цього голосування.")

    vote.delete()
    messages.success(request, "Голосування успішно видалено.")
    return redirect("vote_list")

