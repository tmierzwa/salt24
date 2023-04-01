from django.urls import re_path
from sms.views import HazardList, HazardHistory, HazardDetails, HazardCreate, HazardUpdate, HazardDelete
from sms.views import RiskDetails, RiskHistory, RiskCreate, RiskUpdate, RiskDelete
from sms.views import SMSEventList, SMSEventDetails, SMSEventCreate, SMSEventUpdate, SMSEventDelete
from sms.views import FailureList, FailureDetails, FailureCreate, FailureUpdate, FailureDelete
from sms.views import SMSReportList, SMSReportDetails, SMSReportCreate, SMSReportUpdate, SMSReportDelete
from sms.views import NCRList, NCRDetails, NCRCreate, NCRUpdate, NCRDelete, NCRReport, NCRExport
from sms.views import SMSHazardsExport, SMSEventsExport, SMSReportsExport, SMSFlightsExport
from sms.views import NCRWarnings


app_name = "sms"

urlpatterns = [
   re_path(r'^$', HazardList.as_view(), name='hazard-list'),

   re_path(r'^hazard/details/(?P<pk>\d+)/$', HazardDetails.as_view(), name='hazard-details'),
   re_path(r'^hazard/history/(?P<pk>\d+)/$', HazardHistory.as_view(), name='hazard-history'),
   re_path(r'^hazard/create/$', HazardCreate.as_view(), name='hazard-create'),
   re_path(r'^hazard/update/(?P<pk>\d+)/$', HazardUpdate.as_view(), name='hazard-update'),
   re_path(r'^hazard/delete/(?P<pk>\d+)/$', HazardDelete.as_view(), name='hazard-delete'),
   re_path(r'^hazard/export/$', SMSHazardsExport, name='sms-hazards-export'),

   re_path(r'^risk/details/(?P<pk>\d+)/$', RiskDetails.as_view(), name='risk-details'),
   re_path(r'^risk/history/(?P<pk>\d+)/$', RiskHistory.as_view(), name='risk-history'),
   re_path(r'^risk/create/(?P<hazard_id>\d+)/$', RiskCreate.as_view(), name='risk-create'),
   re_path(r'^risk/update/(?P<pk>\d+)/$', RiskUpdate.as_view(), name='risk-update'),
   re_path(r'^risk/delete/(?P<pk>\d+)/$', RiskDelete.as_view(), name='risk-delete'),

   re_path(r'^smsevent/list/$', SMSEventList.as_view(), name='smsevent-list'),
   re_path(r'^smsevent/details/(?P<pk>\d+)/$', SMSEventDetails.as_view(), name='smsevent-details'),
   re_path(r'^smsevent/create/$', SMSEventCreate.as_view(), name='smsevent-create'),
   re_path(r'^smsevent/update/(?P<pk>\d+)/$', SMSEventUpdate.as_view(), name='smsevent-update'),
   re_path(r'^smsevent/delete/(?P<pk>\d+)/$', SMSEventDelete.as_view(), name='smsevent-delete'),
   re_path(r'^smsevent/export/$', SMSEventsExport, name='sms-events-export'),

   re_path(r'^failure/list/$', FailureList.as_view(), name='failure-list'),
   re_path(r'^failure/details/(?P<pk>\d+)/$', FailureDetails.as_view(), name='failure-details'),
   re_path(r'^failure/create/(?P<pdt_id>\d+)/$', FailureCreate.as_view(), name='failure-create'),
   re_path(r'^failure/create/$', FailureCreate.as_view(), name='failure-create-free'),
   re_path(r'^failure/update/(?P<pk>\d+)/$', FailureUpdate.as_view(), name='failure-update'),
   re_path(r'^failure/delete/(?P<pk>\d+)/$', FailureDelete.as_view(), name='failure-delete'),

   re_path(r'^smsreport/list/$', SMSReportList.as_view(), name='smsreport-list'),
   re_path(r'^smsreport/details/(?P<pk>\d+)/$', SMSReportDetails.as_view(), name='smsreport-details'),
   re_path(r'^smsreport/create/$', SMSReportCreate.as_view(), name='smsreport-create'),
   re_path(r'^smsreport/update/(?P<pk>\d+)/$', SMSReportUpdate.as_view(), name='smsreport-update'),
   re_path(r'^smsreport/delete/(?P<pk>\d+)/$', SMSReportDelete.as_view(), name='smsreport-delete'),
   re_path(r'^smsreport/export/$', SMSReportsExport, name='sms-reports-export'),

   re_path(r'^ncr/list/$', NCRList.as_view(), name='ncr-list'),
   re_path(r'^ncr/details/(?P<pk>\d+)/$', NCRDetails.as_view(), name='ncr-details'),
   re_path(r'^ncr/create/$', NCRCreate.as_view(), name='ncr-create'),
   re_path(r'^ncr/update/(?P<pk>\d+)/$', NCRUpdate.as_view(), name='ncr-update'),
   re_path(r'^ncr/delete/(?P<pk>\d+)/$', NCRDelete.as_view(), name='ncr-delete'),
   re_path(r'^ncr/report/$', NCRReport, name='ncr-report'),
   re_path(r'^ncr/export/(?P<scope>\d+)/(?P<type>\d+)$', NCRExport, name='ncr-export'),

   re_path(r'^_flights/$', SMSFlightsExport, name='sms-flights'),

   # re_path(r'^_warnings/$', NCRWarnings, name='ncr_warnings'),

]
