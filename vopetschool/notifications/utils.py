from accounts.models import User
from notifications.models import Notification

def notify_users_about_vote(sender, vote):
    users = set()

    if vote.level == vote.Level.SCHOOL:
        users = User.objects.filter(is_active=True, role="student")
    elif vote.level == vote.Level.CLASS:
        for group in vote.class_groups.all():
            users.update([s.user for s in group.students.all()])
    elif vote.level == vote.Level.TEACHERS:
        for group in vote.teacher_groups.all():
            users.update([t.user for t in group.teachers.all()])
    elif vote.level == vote.Level.SELECTED:
        users = vote.participants.all()

    for user in users:
        Notification.objects.create(
            user=user,
            message=f"Нове голосування: {vote.title}",
            link=f"/votes/{vote.pk}/"
        )
