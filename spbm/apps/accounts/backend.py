from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class SPFBackend(object):
    def authenticate(self, username=None, password=None):
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
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
