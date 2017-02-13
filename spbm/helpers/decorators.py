from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import six


def permission_required(perm, login_url=None, raise_exception=False, message=None):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm, )
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            if type(message) is str:
                raise PermissionDenied(message)
            else:
                raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)
