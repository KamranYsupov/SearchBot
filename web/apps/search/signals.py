import asyncio

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Match
from .tasks import forward_match_message_and_send_match_info

@receiver(post_save, sender=Match)
def order_post_save(sender, instance: Match, created, **kwargs):
    if not created:
        return

    forward_match_message_and_send_match_info.delay(instance.id)



