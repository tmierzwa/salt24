from django.contrib import admin
from sms.models import SMSHazard, SMSHazardRev

admin.site.register(SMSHazard)
admin.site.register(SMSHazardRev)