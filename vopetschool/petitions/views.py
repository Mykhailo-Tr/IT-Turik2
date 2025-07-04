from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count

from .models import Petition
from .forms import PetitionForm, CommentForm
from accounts.models import User, ClassGroup


class PetitionListView(ListView):
    model = Petition
    template_name = "petitions/petition_list.html"
    context_object_name = "petitions"

    def get_queryset(self):
        queryset = Petition.objects.annotate(support_count=Count("supporters", distinct=True))
        for petition in queryset:
            total = petition.get_eligible_voters_count()
            support = petition.support_count
            petition.support_percent = round((support / total * 100), 0) if total > 0 else 0
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["petitions"] = list(self.get_queryset())
        return context


@login_required
def petition_detail_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user
    supported = petition.supporters.filter(id=user.id).exists()

    # Перевірка доступу для класових петицій
    if petition.level == Petition.Level.CLASS and user.role == "student":
        if user.student.school_class != petition.class_group:
            print(f"User {user} from class {user.student.school_class.pk} tried to access petition {petition} for class {petition.class_group.pk}")
            return HttpResponseForbidden("Ця петиція не для вашого класу.")

    eligible_voters = petition.get_eligible_voters_count()
    supporters_count = petition.supporters.count()
    support_percent = int((supporters_count / eligible_voters) * 100) if eligible_voters > 0 else 0

    comment_form = CommentForm()

    return render(request, "petitions/petition_detail.html", {
        "petition": petition,
        "supported": supported,
        "can_support": user.role == "student" and not supported and timezone.now() <= petition.deadline,
        "supporters_count": supporters_count,
        "eligible_voters": eligible_voters,
        "support_percent": support_percent,
        "comment_form": comment_form,
        "comments": petition.comments.all(),
    })


@login_required
@require_POST
def add_comment_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.petition = petition
        comment.author = request.user
        comment.save()
    return redirect("petition_detail", pk=pk)


def calculate_petition_support(petition):
    if petition.level == Petition.Level.CLASS:
        eligible_voters = User.objects.filter(role="student", student__school_class=petition.class_group).count()
    elif petition.level == Petition.Level.SCHOOL:
        eligible_voters = User.objects.filter(role="student").count()
    else:
        eligible_voters = 0

    supporters_count = petition.supporters.count()
    support_percent = int((supporters_count / eligible_voters) * 100) if eligible_voters > 0 else 0

    return {
        "supporters_count": supporters_count,
        "support_percent": support_percent,
        "eligible_voters": eligible_voters,
    }


@login_required
@require_http_methods(["GET", "POST"])
def support_petition_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if request.method == "GET" and request.GET.get("refresh") == "1":
        data = calculate_petition_support(petition)
        return JsonResponse(data)

    if user.role != "student":
        return HttpResponseForbidden("Тільки учні можуть підтримувати петиції.")

    if petition.deadline and timezone.now() > petition.deadline:
        return HttpResponseForbidden("Петиція завершена.")

    if petition.level == Petition.Level.CLASS and user.student.school_class != petition.class_group:
        return HttpResponseForbidden("Ця петиція не для вашого класу.")

    if petition.supporters.filter(id=user.id).exists():
        petition.supporters.remove(user)
        supported = False
    else:
        petition.supporters.add(user)
        supported = True

    data = calculate_petition_support(petition)
    data["success"] = True
    data["supported"] = supported
    return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
class PetitionCreateView(View):
    def get(self, request):
        if request.user.role != "student":
            messages.warning(request, "Тільки учні можуть створювати петиції.")
            return redirect("petition_list")

        form = PetitionForm()
        return render(request, "petitions/create.html", {"form": form})

    def post(self, request):
        if request.user.role != "student":
            messages.warning(request, "Тільки учні можуть створювати петиції.")
            return redirect("petition_list")
        
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.creator = request.user

            if petition.level == Petition.Level.CLASS:
                class_group = request.POST.get("class_group")
                petition.class_group = ClassGroup.objects.get(pk=class_group)

            petition.save()
            form.save_m2m()
            messages.success(request, "Петиція створена успішно!")
            return redirect("petition_detail", pk=petition.pk)

        messages.error(request, "Помилка при створенні петиції.")
        return render(request, "petitions/create.html", {"form": form})


@login_required
def delete_petition_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)

    if request.user != petition.creator:
        messages.error(request, "Тільки автор петиції може її видалити.")
        return redirect("petition_detail", pk=pk)

    petition.delete()
    messages.success(request, "Петиція успішно видалена.")
    return redirect("petition_list")
