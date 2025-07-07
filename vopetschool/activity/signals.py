from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
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
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(m2m_changed, sender=Petition.supporters.through)
def log_supported_petition(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            UserActivity.objects.get_or_create(
                user_id=user_id,
                type=UserActivity.ActivityType.SUPPORTED_PETITION,
                related_object_title=instance.title,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Vote)
def log_created_vote(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.creator,
            type=UserActivity.ActivityType.CREATED_VOTE,
            related_object_title=instance.title,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=VoteAnswer)
def log_answered_vote(sender, instance, created, **kwargs):
    if created:
        vote = instance.option.vote
        obj, created = UserActivity.objects.get_or_create(
            user=instance.voter,
            type=UserActivity.ActivityType.ANSWERED_VOTE,
            related_object_title=vote.title,
            content_type=ContentType.objects.get_for_model(vote),
            object_id=vote.id,
        )
        existing_options = obj.extra_info.get("selected_options", []) if obj.extra_info else []
        if instance.option.text not in existing_options:
            existing_options.append(instance.option.text)
            obj.extra_info = {"selected_options": existing_options}
            obj.save()