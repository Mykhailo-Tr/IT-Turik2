from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.contrib import messages

from .models import Vote, VoteOption, VoteAnswer
from .forms import VoteForm, VoteCreateForm, VoteOptionFormSet
from accounts.models import User, TeacherGroup, ClassGroup, Student


class VoteListView(ListView):
    model = Vote
    template_name = "voting/vote_list.html"
    context_object_name = "votes"

    def get_queryset(self):
        user = self.request.user
        filter_option = self.request.GET.get("filter")

        class_group_ids = []
        if hasattr(user, 'student'):
            class_group_ids = user.student.class_groups.values_list("id", flat=True)

        if user.role in ["director", "admin"]:
            base_qs = Vote.objects.all()
        else:
            base_qs = Vote.objects.filter(
                Q(level=Vote.Level.SCHOOL) |
                Q(level=Vote.Level.CLASS, class_groups__in=class_group_ids) |
                Q(level=Vote.Level.TEACHERS, creator__role="teacher") |
                Q(level=Vote.Level.SELECTED, participants=user)
            ).distinct()

        now = timezone.now()

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

    if vote.level == Vote.Level.SELECTED and request.user not in vote.participants.all():
        messages.error(request, "Ви не можете голосувати в цьому голосуванні.")
        return redirect("vote_list")

    already_voted = VoteAnswer.objects.filter(voter=request.user, option__vote=vote).exists()
    can_vote = vote.is_active() and not already_voted

    if request.method == "POST" and can_vote:
        form = VoteForm(vote, request.POST)
        if form.is_valid():
            selected_ids = form.cleaned_data["options"]
            if not isinstance(selected_ids, list):
                selected_ids = [selected_ids]

            for option_id in selected_ids:
                option = get_object_or_404(VoteOption, id=option_id, vote=vote)
                VoteAnswer.objects.create(voter=request.user, option=option)

            messages.success(request, "Ваш голос успішно враховано.")
            return redirect("vote_detail", pk=vote.pk)
        else:
            messages.error(request, "Помилка при обробці голосу. Спробуйте ще раз.")

    else:
        form = VoteForm(vote) if can_vote else None

    if vote.level == Vote.Level.SELECTED:
        eligible_users = vote.participants.all()
    elif vote.level == Vote.Level.TEACHERS:
        eligible_users = User.objects.filter(role="teacher", teacher__groups__in=vote.teacher_groups.all()).distinct()
    elif vote.level == Vote.Level.CLASS:
        eligible_students = Student.objects.filter(class_groups__in=vote.class_groups.all()).distinct()
        eligible_users = User.objects.filter(student__in=eligible_students)
    else:
        eligible_users = User.objects.all()

    voted_users = User.objects.filter(vote_answers__option__vote=vote).distinct()

    user_can_see_votes = (
        request.user == vote.creator
        or request.user.role in ["director", "admin"]
        or already_voted
        or not vote.is_active()
    )

    options = []
    raw_options = vote.options.annotate(vote_count=Count("answers")).select_related("vote")
    for option in raw_options:
        option.voted_users = User.objects.filter(vote_answers__option=option) if user_can_see_votes else []
        options.append(option)

    option_voted_users_dict = {}
    if user_can_see_votes:
        for option in vote.options.all():
            option_voted_users_dict[option.id] = list(User.objects.filter(vote_answers__option=option))

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

            # Додай автора в учасники, якщо рівень SELECTED
            if vote.level == Vote.Level.SELECTED:
                vote.participants.add(request.user)

            for form in formset:
                text = form.cleaned_data.get("text")
                is_correct = form.cleaned_data.get("is_correct", False)
                if text:
                    VoteOption.objects.create(vote=vote, text=text, is_correct=is_correct)

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


@never_cache
@login_required
def vote_stats_api(request, pk):
    vote = get_object_or_404(Vote, pk=pk)

    if vote.level == Vote.Level.SELECTED and request.user not in vote.participants.all():
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Перевірка дозволу бачити голоси
    user_can_see_votes = (
        request.user == vote.creator or
        request.user.role in ["director", "admin"] or
        VoteAnswer.objects.filter(voter=request.user, option__vote=vote).exists() or
        not vote.is_active()
    )

    if not user_can_see_votes:
        return JsonResponse({"error": "Access denied"}, status=403)

    options = vote.options.annotate(vote_count=Count("voteanswer"))
    total_votes = sum(option.vote_count for option in options)

    return JsonResponse({
        "total_votes": total_votes,
        "options": [
            {
                "id": option.id,
                "text": option.text,
                "count": option.vote_count,
                "percent": round((option.vote_count / total_votes) * 100) if total_votes else 0
            }
            for option in options
        ]
    })