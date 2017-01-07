from django.contrib import admin

from spbm.apps.society.models import Society, Worker, Event, Shift, Invoice


def is_readonly(obj: object) -> bool:
    """
    Tells whether a given object, such Event, Invoice, should be read-only or not.

    Can also be used to check this for inlines, such as Invoice listing multiple read-only of Event.
    Simple helper for whether or not a given event, or shift,
    is now supposed to be changed or deleted, or similarly.

    :param obj: Event or Shift object in question.
    :return: True if allowed to edit, False if not.
    """
    if type(obj) is Worker:
        # If we're looking from the Worker admin, everything is read-only.
        return True
    elif type(obj) is Invoice:
        # If we're looking from an Invoice, we exist, thus it's read-only.
        return True
    else:
        return obj is not None and obj.processed


class ReadOnlyProtection:
    """
    Helper class for a protected inline object display in the admin console.
    Overrides the has_*_permission functions for you.
    """

    @staticmethod
    def has_add_permission(request, obj=None):
        return not is_readonly(obj)

    @staticmethod
    def has_change_permission(request, obj=None):
        return not is_readonly(obj)

    @staticmethod
    def has_delete_permission(request, obj=None):
        return not is_readonly(obj)


class ShiftInline(ReadOnlyProtection, admin.TabularInline):
    model = Shift
    extra = 0

    exclude = ('norlonn_report',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "worker":
            if not request.user.is_superuser:
                kwargs['queryset'] = Worker.objects.filter(society=request.user.spfuser.society)
        return super(ShiftInline, self).formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if is_readonly(obj):
            return 'event', 'worker', 'wage', 'hours', 'norlonn_report',
        else:
            return 'norlonn_report',


class EventInline(ReadOnlyProtection, admin.TabularInline):
    model = Event
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if is_readonly(obj):
            return [f.name if not f.one_to_many else None for f in self.model._meta.fields]
        else:
            super().get_readonly_fields(request, obj)


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    inlines = [ShiftInline]
    list_filter = ('society', 'invoice',)
    list_display = ('__str__', 'get_cost', 'registered', 'date', 'processed',)
    exclude = ('invoice',)

    def get_readonly_fields(self, request, obj=None):
        """
        Provide read-only fields for events.

        1. Objects that are processed are fully read-only.
        2. Objects which haven't been processed yet can still be changed, except for the society attached.
        3. New objects are all good, except for whether they're processed and which invoice is attached.

        Could be reused elsewhere for some sort of ReadOnlyModelAdmin.
        See https://docs.djangoproject.com/en/1.8/ref/models/meta/#django.db.models.options.Options.get_fields
        :param request: See super.
        :param obj: See super.
        :return: Read-only fields.
        """
        if is_readonly(obj):
            return [f.name if not f.one_to_many else None for f in self.model._meta.fields]
            # return [f.name for f in self.model._meta.get_fields()]
            # return self.fields or [f.name for f in self.model._meta.fields]
        elif obj is not None and obj.processed is None:
            return 'processed', 'society', 'invoice'
        else:
            return 'processed', 'invoice',

    def has_delete_permission(self, request, obj=None):
        return not is_readonly(obj)

    def has_change_permission(self, request, obj=None):
        # You can look, but you can't change if it's read-only.
        return request.method in ['GET', 'HEAD'] or not is_readonly(obj)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "society":
            if not request.user.is_superuser:
                kwargs['queryset'] = Society.objects.filter(id=request.user.spfuser.society.id)
        return super(EventAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'spfuser'):
            return qs.filter(society=request.user.spfuser.society)
        else:
            return qs.none()


admin.site.register(Event, EventAdmin)
