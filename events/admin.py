from django.contrib import admin
from events.models import Event,Shift
from workers.models import Worker
from society.models import Society
from django.contrib.admin.util import flatten_fieldsets

class ShiftInline(admin.TabularInline):
	model = Shift
	extra = 0

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "worker":
			if not request.user.is_superuser:
				kwargs['queryset'] = Worker.objects.filter(society=request.user.spfuser.society)
		return super(ShiftInline,self).formfield_for_choice_field(db_field, request, **kwargs)

	def get_readonly_fields(self, request, obj=None):
		if obj is not None and obj.processed is not None:
			return ('worker', 'wage', 'hours')
		return list()

	def has_delete_permission(self, request, obj=None):
		if obj is None or obj.processed is None:
			return True
		return False
	
class EventAdmin(admin.ModelAdmin):
	inlines = [ShiftInline]
	list_filter = ('society',)
	list_display = ('__str__', 'date', 'processed',)
	readonly_fields = ('processed', 'society', )
	exclude = ('invoice', )

	def get_readonly_fields(self, request, obj=None):
		if obj is None or obj.processed is None:
			return self.readonly_fields	
		
		if self.declared_fieldsets:
			return flatten_fieldsets(self.declared_fieldsets)
		else:
			return list(set(
				[field.name for field in self.opts.local_fields] +
				[field.name for field in self.opts.local_many_to_many]
			))

	def has_delete_permission(self, request, obj=None):
		if obj is None or obj.processed is None:
			return True
		return False

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "society":
			if not request.user.is_superuser:
				kwargs['queryset'] = Society.objects.filter(id=request.user.spfuser.society.id)
		return super(EventAdmin,self).formfield_for_choice_field(db_field, request, **kwargs)
	
	
	def get_queryset(self, request):
		qs = super(EventAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		
		if hasattr(request.user, 'spfuser'):
			return qs.filter(society=request.user.spfuser.society)
		else:
			return qs.none()

admin.site.register(Event, EventAdmin)
