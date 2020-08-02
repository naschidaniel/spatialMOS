from django.contrib import admin
from .models import SpatialMosRun, SpatialMosStep, SpatialMosPoint

# Delete without asking about premession
def delete_selected_2(SpatialMosRunAdmin, request, queryset):
    for element in queryset:
        element.delete()
delete_selected_2.short_description = "delete SpatialMosStep"


class SpatialMosRunAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)

        actions["delete_selected"] = (delete_selected_2, "delete_selected", "delete SpatialMosStep")

        return actions

# Register your models here.
admin.site.register(SpatialMosPoint)
admin.site.register(SpatialMosStep)
admin.site.register(SpatialMosRun, SpatialMosRunAdmin)
