from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login


class LoginAndPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Custom mixin to merge login and permission required.
    """

    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(), self.get_redirect_field_name(),
                                     )
        if not self.has_permission():
            # We could also use "return self.handle_no_permission()" here
            # raise PermissionDenied(self.get_permission_denied_message())
            return self.handle_no_permission()
        return super(LoginAndPermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
