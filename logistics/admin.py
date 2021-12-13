import csv

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import Textarea, TextInput, CheckboxInput
from django.db import models
from django.http import HttpResponse
from django.contrib.auth.models import User

from src.tools.TimeConverter import TimeConverter
from .models import TradeTransaction, ActionRecord
from datetime import datetime


# https://data-flair.training/blogs/django-admin-customization/
# https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
def set_form_widget_size(form, field_name: str, rows: int, cols: int):
    skill_name_field_widget_attrs = form.base_fields[field_name].widget.attrs
    skill_name_field_widget_attrs['rows'] = rows
    skill_name_field_widget_attrs['cols'] = cols


def set_research_completed(self, request, queryset):
    print('-----------------> set completed called')
    queryset.update(research_completed=TimeConverter.now())


def set_transaction_completed(self, request, queryset):
    print('-----------------> set completed called')
    queryset.update(transaction_completed=TimeConverter.now())


def set_action_processed(self, request, queryset):
    print('-----------------> set processed called')
    queryset.update(processed=True)


def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    if len(self.list_display) > 0:
        export_field_names = self.list_display
    else:
        export_field_names = field_names

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(export_field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in export_field_names])

    return response


export_as_csv.short_description = "Export selected to csv"
set_transaction_completed.short_description = 'Mark selected items completed'
set_action_processed.short_description = 'Mark selected items completed'


@admin.register(TradeTransaction)
class TradeTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'player_a_display_name', 'player_b_display_name', 'items', 'transaction_completed', 'comments', 'flag_reason')
    readonly_fields = ('flagged_by',)
    actions = [set_transaction_completed, export_as_csv]
    list_display_links = list_display

    def save_model(self, request, obj, form, change):
        pk = obj.pk
        if pk is not None:
            old_model = TradeTransaction.objects.filter(pk=pk).first()
            if old_model is not None:
                if old_model.flagged != obj.flagged:
                    if obj.flagged:
                        obj.flagged_by = request.user
                    else:
                        obj.flagged_by = None
            else:
                if obj.flagged:
                    obj.flagged_by = request.user

        obj.save()
    #
    # class Meta:
    #     export_fields = 'transaction_date', 'player_a_display_name', 'player_b_display_name', 'items', 'transaction_completed', 'comments', 'flag_reason'


@admin.register(ActionRecord)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('flagged', 'flagged_by', 'processed', 'action_type', 'actor_display_name', 'action_start', 'items', 'action_completed', 'interrupted', 'quantity', 'mind_cost', 'time_cost', 'resolve_cost', 'materials', 'commentary', 'flag_reason')
    actions = [set_action_processed, export_as_csv]
    readonly_fields = ('flagged_by',)
    list_display_links = list_display

    def save_model(self, request, obj, form, change):
        pk = obj.pk
        if pk is not None:
            old_model = ActionRecord.objects.filter(pk=pk).first()
            if old_model is not None:
                if old_model.flagged != obj.flagged:
                    if obj.flagged:
                        obj.flagged_by = request.user
                    else:
                        obj.flagged_by = None
            else:
                if obj.flagged:
                    obj.flagged_by = request.user

        obj.save()
    #
    # class Meta:
    #     export_fields = 'flagged', 'flagged_by', 'processed', 'action_type', 'actor_display_name', 'action_start', 'items', 'action_completed', 'interrupted', 'quantity', 'mind_cost', 'time_cost', 'resolve_cost', 'materials', 'commentary', 'flag_reason'

# admin.site.register(ActionRecord, ActionAdmin)
# admin.site.register(TradeTransaction, TradeTransactionAdmin)
admin.site.site_header = "DRKY Logistics Administrator"
