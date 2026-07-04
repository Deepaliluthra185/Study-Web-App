from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Paper
from .services import process_pdf


@receiver(post_save, sender=Paper)
def process_new_pdf(sender, instance, created, **kwargs):

    if created:
        transaction.on_commit(
            lambda: process_pdf(instance)
        )