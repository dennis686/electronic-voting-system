# signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Voter

@receiver(pre_save, sender=Voter)
def validate_region_hierarchy(sender, instance, **kwargs):
    if instance.constituency and instance.constituency.county != instance.county:
        raise ValueError("Constituency does not belong to the selected County.")

    if instance.ward and instance.ward.constituency != instance.constituency:
        raise ValueError("Ward does not belong to the selected Constituency.")
