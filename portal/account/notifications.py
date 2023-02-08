from urllib.parse import urlencode

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from ..core.url import prepare_url


def send_password_reset_notification(user, redirect_url):
    token = default_token_generator.make_token(user)
    params = urlencode({"email": user.email, "token": token})
    password_set_url = prepare_url(params, redirect_url)
    send_mail(
        "Password Recovery",
        password_set_url,
        "contato@cidadetransparente.com.br",
        [user.email],
        fail_silently=False,
    )
