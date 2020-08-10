"""The models witch are displayed in the Admin Panel"""

from django.contrib import admin
from .models import SpatialMosRun, SpatialMosStep, SpatialMosPoint

# Delete without asking confirmation
def delete_selected_2(SpatialMosRunAdmin, request, queryset):
    """With this function the model runs are deleted without confirmation."""
    for element in queryset:
        element.delete()
delete_selected_2.short_description = "delete SpatialMosStep"

class SpatialMosRunAdmin(admin.ModelAdmin):
    """Class for SpatialMos Runs in the Admin panel"""
    def get_actions(self, request):
        """The standard function is replaced by delete_selected_2."""
        actions = super().get_actions(request)
        actions["delete_selected"] = (delete_selected_2, "delete_selected", "delete SpatialMosStep")
        return actions


# Registered models for the Predictions panel
admin.site.register(SpatialMosPoint)
admin.site.register(SpatialMosStep)
admin.site.register(SpatialMosRun, SpatialMosRunAdmin)
