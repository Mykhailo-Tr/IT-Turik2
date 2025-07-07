from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Petition
from .forms import PetitionForm, CommentForm
from accounts.models import User, ClassGroup
from notifications.utils import notify_petition_creation


class PetitionListView(ListView):
    model = Petition
    template_name = "petitions/petition_list.html"
    context_object_name = "petitions"

    def get_queryset(self):
        queryset = Petition.objects.all()

        if self.request.user.role == "director":
            queryset = queryset.exclude(status=Petition.Status.NEW)

        status = self.request.GET.get("status")
        level = self.request.GET.get("level")
        creator = self.request.GET.get("creator")
        needs_support = self.request.GET.get("needs_support")

        if status:
            queryset = queryset.filter(status=status)
        if level:
            queryset = queryset.filter(level=level)
        if creator:
            queryset = queryset.filter(creator__id=creator)

        if needs_support == "1":
            queryset = queryset.filter(deadline__gte=timezone.now())
            queryset = [p for p in queryset if p.remaining_supporters_needed() > 0]
            queryset.sort(key=lambda p: p.created_at, reverse=True)
            return queryset

        # Якщо без фільтра — повертаємо стандартний QuerySet із сортуванням
        return queryset.order_by("-created_at")



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "statuses": Petition.Status.choices,
            "levels": Petition.Level.choices,
            "students": User.objects.filter(role="student"),
            "selected_status": self.request.GET.get("status", ""),
            "selected_level": self.request.GET.get("level", ""),
            "selected_creator": self.request.GET.get("creator", ""),
            "selected_needs_support": self.request.GET.get("needs_support", ""),
        })
        return context
    
@login_required
def petition_detail_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user
    supported = petition.supporters.filter(id=user.id).exists()

    if request.user.role != "director":
        if request.user.role == "student":
            if petition.level == Petition.Level.CLASS and not user.is_in_classgroup(petition.class_group):
                messages.error(request, "❌ Ця петиція не для вашого класу.")
                return redirect("petition_list")

    eligible_voters = petition.get_eligible_voters_count()
    supporters_count = petition.supporters.count()
    support_percent = int((supporters_count / eligible_voters) * 100) if eligible_voters > 0 else 0
    
    return render(request, "petitions/petition_detail.html", {
        "petition": petition,
        "supported": supported,
        "can_support": user.role == "student" and not supported and timezone.now() <= petition.deadline and petition.status == Petition.Status.NEW,
        "supporters_count": supporters_count,
        "eligible_voters": eligible_voters,
        "remaining_supporters": petition.remaining_supporters_needed(),
        "required_supporters": petition.total_needed_supporters(),
        "support_percent": support_percent,
        "comment_form": CommentForm(),
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
        messages.success(request, "✅ Коментар додано успішно.")
    else:
        messages.error(request, "❌ Помилка при додаванні коментаря.")

    return redirect("petition_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def edit_comment_view(request, petition_pk, comment_pk):
    petition = get_object_or_404(Petition, pk=petition_pk)
    comment = get_object_or_404(petition.comments, pk=comment_pk)

    if request.user != comment.author:
        messages.error(request, "❌ Ви не можете редагувати цей коментар.")
        return redirect("petition_detail", pk=petition_pk)

    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        form.instance.updated_at = timezone.now()
        form.save()
        messages.success(request, "✅ Коментар оновлено успішно.")
        return redirect("petition_detail", pk=petition_pk)
    else:
        messages.error(request, "❌ Помилка при оновленні коментаря.")
    


@login_required
@require_POST
def delete_comment_view(request, petition_pk, comment_pk):
    petition = get_object_or_404(Petition, pk=petition_pk)
    comment = get_object_or_404(petition.comments, pk=comment_pk)

    if request.user != comment.author:
        messages.error(request, "❌ Ви не можете видалити цей коментар.")
        return redirect("petition_detail", pk=petition_pk)

    comment.delete()
    messages.success(request, "🗑️ Коментар видалено успішно.")
    return redirect("petition_detail", pk=petition_pk)


def calculate_petition_support(petition):
    if petition.level == Petition.Level.CLASS:
        eligible_voters = petition.class_group.students.count()
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
        "required_supporters": petition.total_needed_supporters(),
        "remaining_supporters": petition.remaining_supporters_needed(),
    }


@login_required
@require_http_methods(["GET", "POST"])
def support_petition_view(request, pk):
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if request.method == "POST":
        if petition.status != Petition.Status.NEW:
            return HttpResponseForbidden("Петиція вже закрита або розглядається.")

    if request.method == "GET" and request.GET.get("refresh") == "1":
        return JsonResponse(calculate_petition_support(petition))

    if user.role != "student":
        return HttpResponseForbidden("Тільки учні можуть підтримувати петиції.")

    if petition.deadline and timezone.now() > petition.deadline:
        return HttpResponseForbidden("Петиція завершена.")

    if petition.level == Petition.Level.CLASS and not user.is_in_classgroup(petition.class_group):
        return HttpResponseForbidden("Ця петиція не для вашого класу.")

    if petition.supporters.filter(id=user.id).exists():
        petition.supporters.remove(user)
        supported = False
    else:
        petition.supporters.add(user)
        supported = True

    if petition.status == Petition.Status.NEW and petition.is_ready_for_review():
        petition.status = Petition.Status.PENDING
        petition.save()

    data = calculate_petition_support(petition)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "petitions",
        {
            "type": "petition_support_updated",
            "petition_id": petition.id,
            "supporters_count": data["supporters_count"],
            "support_percent": data["support_percent"],
        }
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"petition_{petition.pk}",
        {
            "type": "petition_support_update",
            "data": data
        }
)
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
                class_group_id = request.POST.get("class_group")
                petition.class_group = ClassGroup.objects.get(pk=class_group_id)

            petition.save()
            form.save_m2m()
            
            notify_petition_creation(petition)

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


@login_required
def set_petition_status(request, pk):
    petition = get_object_or_404(Petition, pk=pk)

    if request.user.role != 'director' or petition.status != Petition.Status.PENDING:
        messages.error(request, "⛔ Недостатньо прав або петиція вже оброблена.")
        return redirect('petition_detail', pk=pk)

    if request.method == "POST":
        status = request.POST.get("status")
        if status in [Petition.Status.APPROVED, Petition.Status.REJECTED]:
            petition.status = status
            petition.reviewed_by = request.user
            petition.reviewed_at = timezone.now()
            petition.save()
            messages.success(request, f"✅ Статус петиції оновлено: {status}")
        else:
            messages.error(request, "⛔ Невідомий статус.")
    return redirect('petition_detail', pk=pk)
