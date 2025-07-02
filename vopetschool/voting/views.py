from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.db.models import Q
from django.utils.decorators import method_decorator
from .models import Vote, VoteOption, VoteAnswer
from .forms import VoteForm


class VoteListView(ListView):
    model = Vote
    template_name = "votes/vote_list.html"
    context_object_name = "votes"

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        return Vote.objects.filter(
            Q(level=Vote.Level.SCHOOL) |
            Q(level=Vote.Level.CLASS, creator__student__school_class=user.student.school_class if hasattr(user, 'student') else None) |
            Q(level=Vote.Level.TEACHERS, creator__role="teacher") |
            Q(level=Vote.Level.SELECTED, participants=user)
        ).distinct().filter(start_date__lte=now).order_by("-start_date")
        
@login_required
def vote_detail_view(request, pk):
    vote = get_object_or_404(Vote, pk=pk)

    # 🔒 Перевірка доступу
    if vote.level == Vote.Level.SELECTED and request.user not in vote.participants.all():
        return render(request, "votes/access_denied.html")

    # 📅 Чи активне
    if not vote.is_active():
        return render(request, "votes/vote_closed.html", {"vote": vote})

    # ❌ Перевірка чи вже голосував
    voted = VoteAnswer.objects.filter(
        voter=request.user,
        option__vote=vote
    ).exists()
    if voted:
        return render(request, "votes/already_voted.html", {"vote": vote})

    # ✅ Голосування
    if request.method == "POST":
        form = VoteForm(vote, request.POST)
        if form.is_valid():
            selected_ids = form.cleaned_data["options"]
            if not isinstance(selected_ids, list):
                selected_ids = [selected_ids]

            for option_id in selected_ids:
                option = get_object_or_404(VoteOption, id=option_id, vote=vote)
                VoteAnswer.objects.create(voter=request.user, option=option)

            return render(request, "votes/vote_success.html", {"vote": vote})
    else:
        form = VoteForm(vote)

    return render(request, "votes/vote_detail.html", {"vote": vote, "form": form})


@method_decorator(login_required, name="dispatch")
class VoteCreateView(View):
    def get(self, request):
        vote_form = VoteCreateForm()
        formset = VoteOptionFormSet()
        return render(request, "votes/vote_create.html", {
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

        return render(request, "votes/vote_create.html", {
            "vote_form": vote_form,
            "formset": formset
        })