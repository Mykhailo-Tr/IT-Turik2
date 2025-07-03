from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count, Q

from .models import Petition
from .forms import PetitionForm
from accounts.models import Student, User, ClassGroup


class PetitionListView(ListView):
    model = Petition
    template_name = "petitions/petition_list.html"
    context_object_name = "petitions"

    def get_queryset(self):
        user = self.request.user

        base_qs = Petition.objects.filter(deadline__gte=timezone.now())

        if user.role == "student":
            return base_qs.filter(
                Q(level=Petition.Level.SCHOOL) |
                Q(level=Petition.Level.CLASS, class_group__name=user.student.school_class)
            ).annotate(support_count=Count("supporters")).order_by("-created_at")

        elif user.role in ["director", "admin"]:
            return base_qs.annotate(support_count=Count("supporters")).order_by("-created_at")

        return Petition.objects.none()


@login_required
def petition_detail_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user
    supported = petition.supporters.filter(id=user.id).exists()
    
    if petition.level == Petition.Level.CLASS and user.role == "student":
        if user.student.school_class != petition.class_group:
            return HttpResponseForbidden("Ця петиція не для вашого класу.")

    if petition.level == Petition.Level.CLASS:
        eligible_voters = User.objects.filter(role="student", student__school_class=petition.class_group).count()
    elif petition.level == Petition.Level.SCHOOL:
        eligible_voters = User.objects.filter(role="student").count()
    else:
        eligible_voters = 0  # fallback

    supporters_count = petition.supporters.count()
    support_percent = int((supporters_count / eligible_voters) * 100) if eligible_voters > 0 else 0

    return render(request, "petitions/petition_detail.html", {
        "petition": petition,
        "supported": supported,
        "can_support": user.role == "student" and not supported and timezone.now() <= petition.deadline,
        "supporters_count": supporters_count,
        "eligible_voters": eligible_voters,
        "support_percent": support_percent,
    })



@login_required
@require_POST
def support_petition_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if user.role != "student":
        return HttpResponseForbidden("Тільки учні можуть підтримувати петиції.")

    if timezone.now() > petition.deadline:
        return HttpResponseForbidden("Петиція завершена.")

    if petition.level == Petition.Level.CLASS and user.student.school_class != petition.class_group:
        return HttpResponseForbidden("Ця петиція не для вашого класу.")

    # Перемикаємо підтримку
    if petition.supporters.filter(id=user.id).exists():
        petition.supporters.remove(user)
        supported = False
    else:
        petition.supporters.add(user)
        supported = True

    if petition.level == Petition.Level.CLASS:
        eligible_voters = User.objects.filter(role="student", student__school_class=petition.class_group).count()
    elif petition.level == Petition.Level.SCHOOL:
        eligible_voters = User.objects.filter(role="student").count()
    else:
        eligible_voters = 0

    supporters_count = petition.supporters.count()
    support_percent = int((supporters_count / eligible_voters) * 100) if eligible_voters > 0 else 0

    return JsonResponse({
        "success": True,
        "supporters_count": supporters_count,
        "support_percent": support_percent,
        "supported": supported,
    })

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
                petition.class_group = request.user.student.school_class

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