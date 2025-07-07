from accounts.models import User
from notifications.models import Notification
from voting.models import Vote
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def trigger_user_notification(user_id: int):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "notify"}
    )

def notify_vote_creation(vote: Vote):
    users = set()

    if vote.level == Vote.Level.SCHOOL:
        users = User.objects.filter(is_active=True, role="student")

    elif vote.level == Vote.Level.CLASS:
        for group in vote.class_groups.all():
            users.update([s.user for s in group.students.all()])

    elif vote.level == Vote.Level.TEACHERS:
        for group in vote.teacher_groups.all():
            users.update([t.user for t in group.teachers.all()])

    elif vote.level == Vote.Level.SELECTED:
        users = vote.participants.all()

    for user in users:
        Notification.objects.create(
            user=user,
            message=f"Нове голосування: {vote.title}",
            link=f"/votes/{vote.pk}/"
        )
        trigger_user_notification(user.id)


def notify_petition_creation(petition):
    users = set()

    if petition.level == petition.Level.SCHOOL:
        users = User.objects.filter(is_active=True, role="student")

    elif petition.level == petition.Level.CLASS and petition.class_group:
        users.update([s.user for s in petition.class_group.students.all()])

    for user in users:
        Notification.objects.create(
            user=user,
            message=f"Нова петиція: {petition.title}",
            link=f"/petitions/{petition.pk}/"
        )
        trigger_user_notification(user.id)