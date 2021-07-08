import sys

from django.contrib.auth.models import User
from django.db.models import CASCADE

from src.constants.Constants import ActionType

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()

DATE_FORMAT = '%m/%d/%Y'
TWELVE_HOUR_TIME_FORMAT = '%I:%M:%S %p'
DATE_WITH_TWELVE_HOUR_TIME_FORMAT = DATE_FORMAT + " " + TWELVE_HOUR_TIME_FORMAT


class ActionRecord(models.Model):
    action_start = models.DateTimeField(verbose_name='start', auto_created=True)
    action_completed = models.DateTimeField(blank=True, null=True)
    interrupted = models.BooleanField(blank=True, null=True)
    actor_discord_id = models.BigIntegerField(blank=False, null=False)
    actor_display_name = models.CharField(verbose_name='actor', max_length=255, blank=False, null=False)
    action_type = models.SmallIntegerField(blank=True, null=True,  choices=[(choice.value, choice.name) for choice in ActionType])
    items = models.CharField(max_length=255, blank=False, null=False)
    quantity = models.SmallIntegerField(blank=True, null=True)
    mind_cost = models.SmallIntegerField(blank=True, null=True)
    time_cost = models.IntegerField(blank=True, null=True)
    resolve_cost = models.SmallIntegerField(blank=True, null=True)
    materials = models.TextField(max_length=500, blank=True, null=True)
    commentary = models.TextField(max_length=500, blank=True, null=True)
    processed = models.BooleanField(default=False, blank=False, null=False)
    flagged = models.BooleanField(default=False, blank=False, null=False)
    flagged_by = models.ForeignKey(User, on_delete=CASCADE, default=None, blank=True, null=True)
    flag_reason = models.TextField(max_length=255, blank=True, null=True)

    class Meta:
        db_table ='logistics_actionrecord'

    def __str__(self):
        return 'Action %s by %s at %s' % \
               (ActionType(self.action_type).__str__, self.actor_display_name, self.action_start.strftime(DATE_WITH_TWELVE_HOUR_TIME_FORMAT))


# Create your models here.
class TradeTransaction(models.Model):
    transaction_date = models.DateTimeField(auto_created=True)
    player_a_discord_id = models.BigIntegerField()
    player_a_display_name = models.CharField(verbose_name='trader', max_length=255)
    player_b_discord_id = models.BigIntegerField()
    player_b_display_name = models.CharField(verbose_name='recipient', max_length=255)
    items = models.CharField(max_length=500)
    transaction_completed = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(max_length=501, blank=True, null=True)
    flagged = models.BooleanField(default=False, blank=False, null=False)
    flagged_by = models.ForeignKey(User, on_delete=CASCADE, default=None, blank=True, null=True)
    flag_reason = models.TextField(max_length=255, blank=True, null=True)

    class Meta:
        db_table ='logistics_tradetransaction'

    def __str__(self):
        return "Traction between %s and %s for %s on %s" % \
               (self.player_a_display_name, self.player_b_display_name, self.items,
                self.transaction_date.strftime(DATE_WITH_TWELVE_HOUR_TIME_FORMAT))
