from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    PartTypes, Processes, Steps, Companies, User, Orders, Parts,
    Documents, EquipmentType, Equipments, QualityErrorsList,
    ErrorReports, EquipmentUsage, ExternalAPIOrderIdentifier,
    ArchiveReason, StepTransitionLog, WorkOrder
)
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "parent_company", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "groups", "parent_company")


@admin.register(PartTypes)
class PartTypesAdmin(admin.ModelAdmin):
    list_display = ("name", "ID_prefix", "version", "created_at", "updated_at")
    search_fields = ("name", "ID_prefix")
    readonly_fields = ("version", "created_at", "updated_at")


@admin.register(Processes)
class ProcessesAdmin(admin.ModelAdmin):
    list_display = ("name", "part_type", "is_remanufactured", "num_steps", "version", "created_at")
    list_filter = ("is_remanufactured",)
    search_fields = ("name", "part_type__name")
    readonly_fields = ("version", "created_at", "updated_at")


@admin.register(Steps)
class StepsAdmin(admin.ModelAdmin):
    list_display = ("step", "part_type", "process", "is_last_step")
    list_filter = ("part_type", "process")
    search_fields = ("description",)


@admin.register(Companies)
class CompaniesAdmin(admin.ModelAdmin):
    list_display = ("name", "hubspot_api_id")
    search_fields = ("name",)


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "company", "status", "estimated_completion", "archived")
    list_filter = ("status", "archived", "company")
    search_fields = ("name", "customer__username", "company__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Parts)
class PartsAdmin(admin.ModelAdmin):
    list_display = ("ERP_id", "part_type", "step", "order", "status", "archived")
    list_filter = ("status", "archived", "part_type", "order")
    search_fields = ("ERP_id", "order__name", "part_type__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Documents)
class PartDocsAdmin(admin.ModelAdmin):
    list_display = ("file_name", "upload_date", "uploaded_by", "is_image", "related_object_display")
    list_filter = ("is_image", "upload_date")
    search_fields = ("file_name",)

    def related_object_display(self, obj):
        if obj.related_object:
            # Try to create a link to the admin change page of the related object
            try:
                app_label = obj.content_type.app_label
                model_name = obj.content_type.model
                admin_url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', admin_url, str(obj.related_object))
            except Exception:
                return str(obj.related_object)
        return "-"

    related_object_display.short_description = "Related Object"
    related_object_display.admin_order_field = "content_type"


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Equipments)
class EquipmentsAdmin(admin.ModelAdmin):
    list_display = ("name", "equipment_type")
    list_filter = ("equipment_type",)


@admin.register(QualityErrorsList)
class QualityErrorsListAdmin(admin.ModelAdmin):
    list_display = ("error_name", "part_type")
    search_fields = ("error_name",)


@admin.register(ErrorReports)
class ErrorReportsAdmin(admin.ModelAdmin):
    list_display = ("part", "created_at", "operator", "description")
    list_filter = ("created_at",)
    search_fields = ("description",)


@admin.register(EquipmentUsage)
class EquipmentUsageAdmin(admin.ModelAdmin):
    list_display = ("equipment", "step", "part", "operator", "used_at")
    search_fields = ("notes",)


@admin.register(ExternalAPIOrderIdentifier)
class ExternalAPIOrderIdentifierAdmin(admin.ModelAdmin):
    list_display = ("stage_name", "API_id")


@admin.register(ArchiveReason)
class ArchiveReasonAdmin(admin.ModelAdmin):
    list_display = ("content_object", "reason", "user", "archived_at")
    search_fields = ("notes",)
    list_filter = ("reason",)


@admin.register(StepTransitionLog)
class StepTransitionLogAdmin(admin.ModelAdmin):
    list_display = ("step", "part", "operator", "timestamp")
    list_filter = ("timestamp",)


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("status", "ERP_id", "created_at", "updated_at", "expected_completion", "expected_duration",
                    "true_completion", "true_duration", "related_order_id", "operator_id")
    list_filter = ("status", "ERP_id", "created_at", "updated_at", "expected_completion", "expected_duration",
                   "true_completion", "true_duration", "related_order_id", "operator_id")