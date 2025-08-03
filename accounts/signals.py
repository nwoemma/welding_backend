# api/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import User
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to perform actions after a User is saved
    """
    if created:
        try:
            # Example: Send welcome email
            if instance.email:
                subject = "Welcome to Our Platform"
                message = render_to_string('emails/welcome_email.html', {
                    'user': instance
                })
                send_mail(
                    subject,
                    message,
                    'noreply@yourdomain.com',
                    [instance.email],
                    fail_silently=False,
                )
            
            # Example: Set default values
            if not instance.role:
                instance.role = 'client'
                instance.save()
                
            logger.info(f"Created profile for {instance.email}")
            
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")

@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    """
    Signal to perform actions before a User is saved
    """
    # Example: Ensure email is lowercase
    if instance.email:
        instance.email = instance.email.lower()
    
    # Example: Generate username if missing
    if not instance.username:
        instance.username = instance.email.split('@')[0]