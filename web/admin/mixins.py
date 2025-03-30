from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse


class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                "admin:%s_%s_change" % (
                    self.model._meta.app_label,
                    self.model._meta.model_name
                ),
                args=(obj.pk,)
            )
        )


class CreateNotPermittedModelAdminMixin:
    def has_add_permission(self, request):
        return False


class DeleteNotPermittedModelAdminMixin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False