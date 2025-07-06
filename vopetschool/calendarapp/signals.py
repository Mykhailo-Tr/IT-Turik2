from django.db.models.signals import post_save
from django.dispatch import receiver
from calendarapp.models import CalendarEvent
from petitions.models import Petition
from voting.models import Vote
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=Petition)
def create_petition_event(sender, instance, **kwargs):
    CalendarEvent.objects.get_or_create(
        user=instance.creator,
        content_type=ContentType.objects.get_for_model(Petition),
        object_id=instance.id,
        defaults={
            'title': f"Дедлайн петиції: {instance.title}",
            'description': f"Завершення петиції",
            'start': instance.deadline,
            'end': instance.deadline,
            'is_deadline': True,
        }
    )

@receiver(post_save, sender=Vote)
def create_vote_event(sender, instance, **kwargs):
    CalendarEvent.objects.get_or_create(
        user=instance.creator,
        content_type=ContentType.objects.get_for_model(Vote),
        object_id=instance.id,
        defaults={
            'title': f"Завершення голосування: {instance.title}",
            'description': f"Останній день для голосування",
            'start': instance.end_date,
            'end': instance.end_date,
            'is_deadline': True,
        }
    )
