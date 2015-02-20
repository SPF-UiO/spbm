from django.contrib import admin
from events.models import Event,Shift

class ShiftInline(admin.TabularInline):
	model = Shift
	extra = 3

class EventAdmin(admin.ModelAdmin):
	inlines = [ShiftInline]

admin.site.register(Event, EventAdmin)
