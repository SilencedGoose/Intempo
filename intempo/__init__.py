from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages

@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    messages.success(request, f"Login Successful")

@receiver(user_logged_out)
def on_logout(sender, user, request, **kwargs):
    messages.success(request, f"you have been logged out")