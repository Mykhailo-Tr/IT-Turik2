from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from petitions.models import Petition
from voting.models import Vote, VoteAnswer
from activity.models import UserActivity

@receiver(post_save, sender=Petition)
def log_created_petition(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.creator,
            type=UserActivity.ActivityType.CREATED_PETITION,
            related_object_title=instance.title,
            related_object_id=instance.id
        )

@receiver(m2m_changed, sender=Petition.supporters.through)
def log_supported_petition(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            UserActivity.objects.get_or_create(
                user_id=user_id,
                type=UserActivity.ActivityType.SUPPORTED_PETITION,
                related_object_title=instance.title,
                related_object_id=instance.id
            )

@receiver(post_save, sender=Vote)
def log_created_vote(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.creator,
            type=UserActivity.ActivityType.CREATED_VOTE,
            related_object_title=instance.title,
            related_object_id=instance.id
        )

@receiver(post_save, sender=VoteAnswer)
def log_answered_vote(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.get_or_create(
            user=instance.voter,
            type=UserActivity.ActivityType.ANSWERED_VOTE,
            related_object_title=instance.option.vote.title,
            related_object_id=instance.option.vote.id,
            extra_info={"selected_option": instance.option.text}
        )
