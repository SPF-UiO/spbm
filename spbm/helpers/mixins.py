from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


class LoggedInPermissionsMixin(PermissionRequiredMixin):
    """
    Custom mixin to merge login and permission required.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(), self.get_redirect_field_name(),
                                     )
        if not self.has_permission():
            # We could also use "return self.handle_no_permission()" here
            raise PermissionDenied(self.get_permission_denied_message())
        return super(LoggedInPermissionsMixin, self).dispatch(request, *args, **kwargs)
