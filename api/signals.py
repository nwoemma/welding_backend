# api/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from accounts.models import User
import logging
import threading

logger = logging.getLogger(__name__)

def send_welcome_email_async(user_email, user_name):
    """Send welcome email in background thread"""
    try:
        subject = "Welcome to Our Platform"
        message = render_to_string('emails/welcome_email.html', {
            'user': {'email': user_email, 'full_name': user_name}
        })
        send_mail(
            subject,
            message,
            'noreply@yourdomain.com',
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user_email}")
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to perform actions after a User is saved
    """
    if created:
        try:
            # Send welcome email in background thread
            if instance.email:
                email_thread = threading.Thread(
                    target=send_welcome_email_async,
                    args=(instance.email, instance.full_name)
                )
                email_thread.daemon = True
                email_thread.start()
                logger.info(f"Started email thread for {instance.email}")
            
            # Set default values
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
    # Ensure email is lowercase
    if instance.email:
        instance.email = instance.email.lower()
    
    # Generate username if missing
    if not instance.username and instance.email:
        instance.username = instance.email.split('@')[0]