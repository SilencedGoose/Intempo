from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib import messages
from django.dispatch import receiver

@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    # only add the message if it's not testing the views
    if hasattr(request, '_messages'): 
        messages.success(request, f"Login Successful")

@receiver(user_logged_out)
def on_logout(sender, user, request, **kwargs):
    # only add the message if it's not testing the views
    if hasattr(request, '_messages'): 
        messages.success(request, f"You have been logged out")