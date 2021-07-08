from django.contrib import admin
from .models import TradeTransaction, ActionRecord
from datetime import datetime

# https://data-flair.training/blogs/django-admin-customization/


def set_transaction_completed(modeladmin, request, queryset):
    print('-----------------> set completed called')
    queryset.update(transaction_completed=datetime.now())


def set_action_processed(modeladmin, request, queryset):
    print('-----------------> set completed called')
    queryset.update(processed=True)


set_transaction_completed.short_description = 'Mark selected items completed'
set_action_processed.short_description = 'Mark selected items completed'


@admin.register(TradeTransaction)
class TradeTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'player_a_display_name', 'player_b_display_name', 'items', 'transaction_completed', 'comments', 'flag_reason')
    readonly_fields = ('flagged_by',)
    actions = [set_transaction_completed]
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


@admin.register(ActionRecord)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('flagged', 'flagged_by', 'processed', 'action_type', 'actor_display_name', 'action_start', 'items', 'action_completed', 'interrupted', 'quantity', 'mind_cost', 'time_cost', 'resolve_cost', 'materials', 'commentary', 'flag_reason')
    action = [set_action_processed]
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


# admin.site.register(ActionRecord, ActionAdmin)
# admin.site.register(TradeTransaction, TradeTransactionAdmin)
admin.site.site_header = "DRKY Logistics Administrator"
