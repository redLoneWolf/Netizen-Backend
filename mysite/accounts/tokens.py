from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            user.pk + timestamp + user.email_confirmed
        )

account_activation_token = AccountActivationTokenGenerator()