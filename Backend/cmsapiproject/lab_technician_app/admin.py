from django.contrib import admin
from .models import LabTest, TestOrder, TestResult


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'low_range', 'high_range', 'unit', 'price', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['test_name', 'description']


@admin.register(TestOrder)
class TestOrderAdmin(admin.ModelAdmin):
    list_display = ['lab_test', 'patient', 'status', 'priority', 'ordered_date']
    list_filter = ['status', 'priority', 'ordered_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'lab_test__test_name']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_order', 'result_value', 'is_normal', 'performed_by', 'result_date']
    list_filter = ['is_normal', 'result_date']
    search_fields = ['test_order__patient__first_name', 'test_order__lab_test__test_name']
