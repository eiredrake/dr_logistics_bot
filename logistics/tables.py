import django_tables2 as tables
from django_tables2 import BooleanColumn

from .models import TradeTransaction, ActionRecord


class ActionRecordTable(tables.Table):
    flagged = BooleanColumn(yesno='✔,')

    class Meta:
        model = ActionRecord
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('actor_display_name', 'action_type', 'action_start', 'items', 'mind_cost', 'time_cost', 'resolve_cost', 'commentary')
        exclude = ('id', 'actor_discord_id', 'action_completed', 'interrupted', 'quantity', 'processed', 'flag_reason' )


class TransactionTable(tables.Table):
    flagged = BooleanColumn(yesno='✔,')

    class Meta:
        model = TradeTransaction
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('id', 'transaction_date', 'player_a_display_name', 'player_b_display_name', 'items', 'comments')
        exclude = ('player_a_discord_id', 'player_b_discord_id', 'transaction_completed', 'flag_reason')
        country = tables.Column(footer='Pending Transactions:')



