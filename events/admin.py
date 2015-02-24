from django.contrib import admin
from events.models import Event,Shift

class ShiftInline(admin.TabularInline):
	model = Shift
	extra = 3

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "worker":
			if not request.user.is_superuser:
				kwargs['queryset'] = Worker.objects.filter(society=request.user.spfuser.society)
		return super(ShiftInline,self).formfield_for_choice_field(db_field, request, **kwargs)
	

class EventAdmin(admin.ModelAdmin):
	inlines = [ShiftInline]
	
	def get_queryset(self, request):
		qs = super(EventAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		
		if hasattr(request.user, 'spfuser'):
			return qs.filter(society=request.user.spfuser.society)
		else:
			return qs.none()

admin.site.register(Event, EventAdmin)
