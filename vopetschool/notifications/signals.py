from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from voting.models import Vote
from petitions.models import Petition 
from accounts.models import Student
from .models import Notification


User = get_user_model()



def get_users_with_access(petition):
    if petition.level == Petition.Level.SCHOOL:
        # Всі активні студенти
        return User.objects.filter(role=User.Role.STUDENT, is_active=True)
    elif petition.level == Petition.Level.CLASS and petition.class_group:
        # Активні користувачі, що є студентами групи
        return User.objects.filter(student__in=petition.class_group.students.all(), is_active=True)
    return User.objects.none()


@receiver(post_save, sender=Petition)
def notify_about_petition_creation_or_status_change(sender, instance, created, **kwargs):
    if created:
        if instance.status != Petition.Status.PENDING:
            users = get_users_with_access(instance)
            notifications = [
                Notification(
                    user=user,
                    message=f"Створена нова петиція: {instance.title}",
                    link=f"/petitions/{instance.pk}/"
                )
                for user in users
            ]
            Notification.objects.bulk_create(notifications)
    else:
        if instance.status in {Petition.Status.PENDING, Petition.Status.APPROVED, Petition.Status.REJECTED}:
            users = get_users_with_access(instance).exclude(role="director")
            status_display = dict(Petition.Status.choices).get(instance.status, instance.status)
            notifications = [
                Notification(
                    user=user,
                    message=f"Петиція '{instance.title}' тепер має статус: {status_display}",
                    link=f"/petitions/{instance.pk}/"
                )
                for user in users
            ]
            Notification.objects.bulk_create(notifications)


@receiver(pre_save, sender=Petition)
def petition_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return 

    try:
        old_instance = Petition.objects.get(pk=instance.pk)
    except Petition.DoesNotExist:
        return

    if old_instance.status != instance.status:
        if instance.status in {Petition.Status.PENDING, Petition.Status.APPROVED, Petition.Status.REJECTED}:
            users = get_users_with_access(instance).exclude(role="director")
            status_display = dict(Petition.Status.choices).get(instance.status, instance.status)
            notifications = [
                Notification(
                    user=user,
                    message=f"Петиція '{instance.title}' тепер має статус: {status_display}",
                    link=f"/petitions/{instance.pk}/"
                )
                for user in users
            ]
            Notification.objects.bulk_create(notifications)