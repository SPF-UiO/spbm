from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from spbm.apps.accounts.models import SpfUser


class SpfUserInline(admin.StackedInline):
    model = SpfUser
    can_delete = False


class SPFUserAdmin(UserAdmin):
    inlines = (SpfUserInline,)


admin.site.unregister(User)
admin.site.register(User, SPFUserAdmin)
