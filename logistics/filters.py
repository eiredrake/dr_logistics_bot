import django_filters
from .models import TradeTransaction, ActionRecord


# class PendingActionRecordFilter(django_filters.FilterSet):
#     action_completed = django_filters.DateTimeFilter(field_name='action_completed', lookup_expr='isnull')
#
#     class Meta:
#         model = ActionRecord
#         fields = ['action_start', 'items', ]

#
# class PendingTradeTransactionFilter(django_filters.FilterSet):
#     transaction_completed = django_filters.DateTimeFilter(field_name='transaction_completed', lookup_expr='isnull')
#
#     class Meta:
#         model = TradeTransaction
#         fields = ['transaction_date', 'player_a_display_name', 'player_b_display_name', 'items', 'transaction_completed', 'comments', ]
