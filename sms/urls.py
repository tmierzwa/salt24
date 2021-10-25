from django.conf.urls import url
from sms.views import HazardList, HazardHistory, HazardDetails, HazardCreate, HazardUpdate, HazardDelete
from sms.views import RiskDetails, RiskHistory, RiskCreate, RiskUpdate, RiskDelete
from sms.views import SMSEventList, SMSEventDetails, SMSEventCreate, SMSEventUpdate, SMSEventDelete
from sms.views import FailureList, FailureDetails, FailureCreate, FailureUpdate, FailureDelete
from sms.views import SMSReportList, SMSReportDetails, SMSReportCreate, SMSReportUpdate, SMSReportDelete
from sms.views import NCRList, NCRDetails, NCRCreate, NCRUpdate, NCRDelete, NCRReport, NCRExport
from sms.views import SMSHazardsExport, SMSEventsExport, SMSReportsExport, SMSFlightsExport
from sms.views import NCRWarnings

urlpatterns = [
   url(r'^$', HazardList.as_view(), name='hazard-list'),

   url(r'^hazard/details/(?P<pk>\d+)/$', HazardDetails.as_view(), name='hazard-details'),
   url(r'^hazard/history/(?P<pk>\d+)/$', HazardHistory.as_view(), name='hazard-history'),
   url(r'^hazard/create/$', HazardCreate.as_view(), name='hazard-create'),
   url(r'^hazard/update/(?P<pk>\d+)/$', HazardUpdate.as_view(), name='hazard-update'),
   url(r'^hazard/delete/(?P<pk>\d+)/$', HazardDelete.as_view(), name='hazard-delete'),
   url(r'^hazard/export/$', SMSHazardsExport, name='sms-hazards-export'),

   url(r'^risk/details/(?P<pk>\d+)/$', RiskDetails.as_view(), name='risk-details'),
   url(r'^risk/history/(?P<pk>\d+)/$', RiskHistory.as_view(), name='risk-history'),
   url(r'^risk/create/(?P<hazard_id>\d+)/$', RiskCreate.as_view(), name='risk-create'),
   url(r'^risk/update/(?P<pk>\d+)/$', RiskUpdate.as_view(), name='risk-update'),
   url(r'^risk/delete/(?P<pk>\d+)/$', RiskDelete.as_view(), name='risk-delete'),

   url(r'^smsevent/list/$', SMSEventList.as_view(), name='smsevent-list'),
   url(r'^smsevent/details/(?P<pk>\d+)/$', SMSEventDetails.as_view(), name='smsevent-details'),
   url(r'^smsevent/create/$', SMSEventCreate.as_view(), name='smsevent-create'),
   url(r'^smsevent/update/(?P<pk>\d+)/$', SMSEventUpdate.as_view(), name='smsevent-update'),
   url(r'^smsevent/delete/(?P<pk>\d+)/$', SMSEventDelete.as_view(), name='smsevent-delete'),
   url(r'^smsevent/export/$', SMSEventsExport, name='sms-events-export'),

   url(r'^failure/list/$', FailureList.as_view(), name='failure-list'),
   url(r'^failure/details/(?P<pk>\d+)/$', FailureDetails.as_view(), name='failure-details'),
   url(r'^failure/create/(?P<pdt_id>\d+)/$', FailureCreate.as_view(), name='failure-create'),
   url(r'^failure/create/$', FailureCreate.as_view(), name='failure-create-free'),
   url(r'^failure/update/(?P<pk>\d+)/$', FailureUpdate.as_view(), name='failure-update'),
   url(r'^failure/delete/(?P<pk>\d+)/$', FailureDelete.as_view(), name='failure-delete'),

   url(r'^smsreport/list/$', SMSReportList.as_view(), name='smsreport-list'),
   url(r'^smsreport/details/(?P<pk>\d+)/$', SMSReportDetails.as_view(), name='smsreport-details'),
   url(r'^smsreport/create/$', SMSReportCreate.as_view(), name='smsreport-create'),
   url(r'^smsreport/update/(?P<pk>\d+)/$', SMSReportUpdate.as_view(), name='smsreport-update'),
   url(r'^smsreport/delete/(?P<pk>\d+)/$', SMSReportDelete.as_view(), name='smsreport-delete'),
   url(r'^smsreport/export/$', SMSReportsExport, name='sms-reports-export'),

   url(r'^ncr/list/$', NCRList.as_view(), name='ncr-list'),
   url(r'^ncr/details/(?P<pk>\d+)/$', NCRDetails.as_view(), name='ncr-details'),
   url(r'^ncr/create/$', NCRCreate.as_view(), name='ncr-create'),
   url(r'^ncr/update/(?P<pk>\d+)/$', NCRUpdate.as_view(), name='ncr-update'),
   url(r'^ncr/delete/(?P<pk>\d+)/$', NCRDelete.as_view(), name='ncr-delete'),
   url(r'^ncr/report/$', NCRReport, name='ncr-report'),
   url(r'^ncr/export/(?P<scope>\d+)/(?P<type>\d+)$', NCRExport, name='ncr-export'),

   url(r'^_flights/$', SMSFlightsExport, name='sms-flights'),

   # url(r'^_warnings/$', NCRWarnings, name='ncr_warnings'),

]
