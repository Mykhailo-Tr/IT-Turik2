from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from calendarapp.models import CalendarEvent
from calendarapp.google_calendar import create_google_event
from petitions.models import Petition
from voting.models import Vote

@receiver(post_save, sender=Petition)
def create_petition_event(sender, instance, **kwargs):
    event, created = CalendarEvent.objects.get_or_create(
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
    if created and event.start and event.end:
        create_google_event(instance.creator.id, event.title, event.description, event.start, event.end)

@receiver(post_save, sender=Vote)
def create_vote_event(sender, instance, **kwargs):
    event, created = CalendarEvent.objects.get_or_create(
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
    if created and event.start and event.end:
        create_google_event(instance.creator.id, event.title, event.description, event.start, event.end)
