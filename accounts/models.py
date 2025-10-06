from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает профиль пользователя при создании User"""
    if created:
        from chat.models import UserProfile
        UserProfile.objects.create(user=instance)
