from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account import app_settings
from allauth.account.utils import user_pk_to_url_str

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from dj_rest_auth.forms import AllAuthPasswordResetForm


class CustomAllAuthPasswordResetForm(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        """Adapted from dj_rest_auth's own password reset form, but with URL
        configuration set via Django's configuration.

        """
        referrer = request.META.get("HTTP_ORIGIN")
        token_generator = kwargs.get("token_generator", default_token_generator)
        email = self.cleaned_data["email"]
        for user in self.users:
            token = token_generator.make_token(user)
            user_id = user_pk_to_url_str(user)
            url = f"{referrer}/reset/{user_id}/{token}"
            # We don't specify a username because authentication is based
            # on email.
            context = {
                # TODO: Change the template since the default template expects
                # a Site object.
                "current_site": referrer,
                "user": user,
                "password_reset_url": url,
                "request": request,
            }
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )
        return self.cleaned_data["email"]
