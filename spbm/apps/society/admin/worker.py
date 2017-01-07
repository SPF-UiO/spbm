from django.contrib import admin

from .events import ShiftInline
from ..models import Society, Worker
from ..forms.worker import WorkerForm


class WorkersModelAdmin(admin.ModelAdmin):
    # We have a customized widget form that we should use here, see ../forms/worker.py
    form = WorkerForm
    inlines = [ShiftInline]
    list_filter = ('society',)
    list_display = ('__str__', 'address', 'person_id', 'account_no', 'norlonn_number')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "society":
            if not request.user.is_superuser:
                kwargs['queryset'] = Society.objects.filter(
                    id=request.user.spfuser.society.id if hasattr(request.user, "spfuser") else None)
        return super(WorkersModelAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

    def has_add_permission(self, req):
        if req.user.is_superuser:
            return True
        if hasattr(req.user, 'spfuser'):
            return True
        return False

    def has_change_permission(self, req, obj=None):
        if req.user.is_superuser:
            return True

        if not hasattr(req.user, 'spfuser'):
            return False

        if obj is None or req.user.spfuser.society == obj.society:
            return True

        return False

    def has_delete_permission(self, req, obj=None):
        if not super(WorkersModelAdmin, self).has_delete_permission:
            return False
        return self.has_change_permission(req, obj)

    def get_queryset(self, request):
        qs = super(WorkersModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'spfuser'):
            return qs.filter(society=request.user.spfuser.society)
        else:
            return qs.none()


admin.site.register(Worker, WorkersModelAdmin)
