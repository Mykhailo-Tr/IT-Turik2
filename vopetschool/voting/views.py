from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST   
from .models import Vote, VoteOption, VoteAnswer
from .forms import VoteForm, VoteCreateForm, VoteOptionFormSet



class VoteListView(ListView):
    model = Vote
    template_name = "voting/vote_list.html"
    context_object_name = "votes"

    def get_queryset(self):
        user = self.request.user

        base_qs = Vote.objects.filter(
            Q(level=Vote.Level.SCHOOL) |
            Q(level=Vote.Level.CLASS, creator__student__school_class=user.student.school_class if hasattr(user, 'student') else None) |
            Q(level=Vote.Level.TEACHERS, creator__role="teacher") |
            Q(level=Vote.Level.SELECTED, participants=user)
        ).distinct()

        return base_qs.order_by("-start_date", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voted_ids = VoteAnswer.objects.filter(voter=self.request.user).values_list("option__vote_id", flat=True)
        context["voted_ids"] = set(voted_ids)
        return context



@login_required
def vote_detail_view(request, pk):
    vote = get_object_or_404(Vote, pk=pk)

    if vote.level == Vote.Level.SELECTED and request.user not in vote.participants.all():
        return render(request, "voting/access_denied.html")

    already_voted = VoteAnswer.objects.filter(
        voter=request.user,
        option__vote=vote
    ).exists()

    options = vote.options.annotate(vote_count=Count("voteanswer"))

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

            # Перенаправити назад на сторінку, щоб побачити результат
            return redirect("vote_detail", pk=vote.pk)
    else:
        form = VoteForm(vote) if can_vote else None

    return render(request, "voting/vote_detail.html", {
        "vote": vote,
        "form": form,
        "can_vote": can_vote,
        "already_voted": already_voted,
        "options": options,
    })



@method_decorator(login_required, name="dispatch")
class VoteCreateView(View):
    def get(self, request):
        vote_form = VoteCreateForm()
        formset = VoteOptionFormSet()
        return render(request, "voting/forms/create.html", {
            "vote_form": vote_form,
            "formset": formset
        })

    def post(self, request):
        vote_form = VoteCreateForm(request.POST)
        formset = VoteOptionFormSet(request.POST)

        if vote_form.is_valid() and formset.is_valid():
            vote = vote_form.save(commit=False)
            vote.creator = request.user
            vote.save()
            vote_form.save_m2m()

            for form in formset:
                text = form.cleaned_data.get("text")
                is_correct = form.cleaned_data.get("is_correct", False)
                if text:
                    VoteOption.objects.create(
                        vote=vote,
                        text=text,
                        is_correct=is_correct
                    )
            return redirect("vote_detail", pk=vote.pk)

        return render(request, "voting/forms/create.html", {
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
    return redirect("vote_list")