from django.contrib import admin

from spf_web.apps.society.models import Society
from spf_web.apps.workers.models import Worker


class WorkersModelAdmin(admin.ModelAdmin):
	list_filter = ('society', )

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "society":
			if not request.user.is_superuser:
				kwargs['queryset'] = Society.objects.filter(id=request.user.spfuser.society.id if hasattr(request.user, "spfuser") else None)
		return super(WorkersModelAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

	def has_add_permission(self,req):
		if req.user.is_superuser:
			return True
		if hasattr(req.user,'spfuser'):
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
#admin.site.register(Worker)
