from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class SPFBackend:
    """
    Custom authentication backend for some SPF requirements, so to speak.

    Per conversation with Aleksi, Jan 7th 2017, over the DARPANET, the following two aspects were the
    reason for the custom authentication backend, and is as such what it does. Mainly.

        1. Allows for case-insensitive usernames.
            - Whether or not a custom backend is necessary with Django 1.10 for this, I haven't checked.
        2. Mitigates username timing attacks.
            - Same applies as above. By always computing a hash-function, you mitigate (somewhat?) against
              timing attacks to brute-force a correct and valid username.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            pwd_valid = user.check_password(password)
        except User.DoesNotExist:
            user = False
            pwd_valid = check_password(password, "sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051tt")
        if user and pwd_valid and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            # Without select_related() we will have the n+1 query problem.
            return User.objects.select_related('spfuser__society').get(pk=user_id)
        except User.DoesNotExist:
            return None
