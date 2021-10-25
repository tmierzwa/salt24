from django.conf.urls import url
from panel.views import PanelHome
from panel.views import DutyDetails, DutyCreate, DutyUpdate, DutyDelete
from panel.views import RatingDetails, RatingCreate, RatingUpdate, RatingDelete
from panel.views import OperationOpen, OperationUpdate, OperationDelete
from panel.views import PDTAOC, PDTView, PDTIntro, PDTSPO, PDTTraining, PDTExam, PDTRent, PDTFuel, PDTDuties
from panel.views import PDTActive, PDTActive_feed, PDTInfo, PDTForm
from panel.views import PDTOpen, PDTUpdate, PDTDelete
from panel.views import MobilePDTOpen0, MobilePDTOpen1, MobilePDTOpen2, MobilePDTOpen3, MobilePDTClose
from panel.views import MobileOperationOpen, MobileOperationClose
from panel.views import RemoteFuelingDetails, RemoteFuelingUpdate, RemoteFuelingDelete
from panel.views import PanelFuelingCreate
from panel.views import PanelSMSEventCreate, PanelSMSEventList, PanelSMSEventUpdate, PanelSMSEventDetails
from panel.views import PanelSMSReportCreate, PanelSMSReportList, PanelSMSReportUpdate, PanelSMSReportDetails
from panel.views import PilotFlights, PilotDuties, PilotUpdate
from panel.views import PilotInfo, PilotRatings, PilotAircraftList, PilotAircraftAuth, PilotTypesList, PilotTypesAuth
from panel.views import PilotDutyReport, PilotDutyExport, PilotPlanReport, PilotPlanExport
from panel.views import Report_PKBWL
from panel.loaders import change_duties


urlpatterns = [

   url(r'^$', PanelHome, name='panel-home'),

   url(r'^pilot/info/(?P<pk>\d+)/$', PilotInfo.as_view(), name='pilot-info'),
   url(r'^pilot/ratings/(?P<pk>\d+)/$', PilotRatings.as_view(), name='pilot-ratings'),
   url(r'^pilot/aircraft/(?P<pk>\d+)/$', PilotAircraftList.as_view(), name='pilot-aircraft'),
   url(r'^pilot/aircraft/auth/(?P<pilot_id>\d+)/$', PilotAircraftAuth, name='pilot-aircraft-auth'),
   url(r'^pilot/types/(?P<pk>\d+)/$', PilotTypesList.as_view(), name='pilot-types'),
   url(r'^pilot/types/auth/(?P<pilot_id>\d+)/$', PilotTypesAuth, name='pilot-types-auth'),
   url(r'^pilot/flights/(?P<type>\w+)/(?P<pk>\d+)/$', PilotFlights.as_view(), name='pilot-flights'),
   url(r'^pilot/duties/(?P<pk>\d+)/$', PilotDuties.as_view(), name='pilot-duties'),
   url(r'^pilot/update/(?P<pk>\d+)/$', PilotUpdate.as_view(), name='pilot-update'),

   url(r'^duty/info/(?P<pk>\d+)/$', DutyDetails.as_view(), name='duty-details'),
   url(r'^duty/create/(?P<pilot_id>\d+)/$', DutyCreate.as_view(), name='duty-create'),
   url(r'^duty/update/(?P<pk>\d+)/$', DutyUpdate.as_view(), name='duty-update'),
   url(r'^duty/delete/(?P<pk>\d+)/$', DutyDelete.as_view(), name='duty-delete'),
   url(r'^duty/report/(?P<pilot_id>\d+)/$', PilotDutyReport, name='duty-report'),
   url(r'^duty/export/(?P<pilot_id>\d+)/(?P<ym>\d+)/(?P<type>\d+)/$', PilotDutyExport, name='duty-export'),
   url(r'^plan/report/(?P<pilot_id>\d+)/$', PilotPlanReport, name='plan-report'),
   url(r'^plan/export/(?P<pilot_id>\d+)/(?P<date_from>\d+)/(?P<date_to>\d+)/(?P<type>\d+)/$', PilotPlanExport, name='plan-export'),

   url(r'^rating/details/(?P<pk>\d+)/$', RatingDetails.as_view(), name='rating-details'),
   url(r'^rating/create/(?P<pilot_id>\d+)/$', RatingCreate.as_view(), name='rating-create'),
   url(r'^rating/update/(?P<pk>\d+)/$', RatingUpdate.as_view(), name='rating-update'),
   url(r'^rating/delete/(?P<pk>\d+)/$', RatingDelete.as_view(), name='rating-delete'),

   url(r'^pdt/active/$', PDTActive.as_view(), name='pdt-active'),
   url(r'^pdt/feed/$', PDTActive_feed.as_view(), name='pdt-active-feed'),
   url(r'^pdt/info/(?P<pk>\d+)/$', PDTInfo.as_view(), name='pdt-info'),
   url(r'^pdt/aoc/(?P<pk>\d+)/$', PDTAOC.as_view(), name='pdt-aoc'),
   url(r'^pdt/view/(?P<pk>\d+)/$', PDTView.as_view(), name='pdt-view'),
   url(r'^pdt/intro/(?P<pk>\d+)/$', PDTIntro.as_view(), name='pdt-intro'),
   url(r'^pdt/spo/(?P<pk>\d+)/$', PDTSPO.as_view(), name='pdt-spo'),
   url(r'^pdt/ato/(?P<pk>\d+)/$', PDTTraining.as_view(), name='pdt-ato'),
   url(r'^pdt/exam/(?P<pk>\d+)/$', PDTExam.as_view(), name='pdt-exam'),
   url(r'^pdt/rent/(?P<pk>\d+)/$', PDTRent.as_view(), name='pdt-rent'),
   url(r'^pdt/fuel/(?P<pk>\d+)/$', PDTFuel.as_view(), name='pdt-fuel'),
   url(r'^pdt/duties/(?P<pk>\d+)/$', PDTDuties.as_view(), name='pdt-duties'),
   url(r'^pdt/form/(?P<pk>\d+)/$', PDTForm.as_view(), name='pdt-form'),
   url(r'^pdt/open/$', PDTOpen, name='pdt-open'),
   url(r'^pdt/update/(?P<pk>\d+)/$', PDTUpdate, name='pdt-update'),
   url(r'^pdt/delete/(?P<pk>\d+)/$', PDTDelete.as_view(), name='pdt-delete'),

   url(r'^operation/open/(?P<pdt_id>\d+)/$', OperationOpen, name='operation-open'),
   url(r'^operation/update/(?P<pk>\d+)/$', OperationUpdate, name='operation-update'),
   url(r'^operation/delete/(?P<pk>\d+)/$', OperationDelete.as_view(), name='operation-delete'),

   url(r'^mpdt/open0/$', MobilePDTOpen0, name='mpdt-open0'),
   url(r'^mpdt/open1/$', MobilePDTOpen1, name='mpdt-open1'),
   url(r'^mpdt/open2/$', MobilePDTOpen2, name='mpdt-open2'),
   url(r'^mpdt/open3/$', MobilePDTOpen3, name='mpdt-open3'),
   url(r'^mpdt/close/(?P<pdt_id>\d+)/$', MobilePDTClose, name='mpdt-close'),

   url(r'^moperation/open/(?P<pdt_id>\d+)/$', MobileOperationOpen, name='moperation-open'),
   url(r'^moperation/close/(?P<operation_id>\d+)/$', MobileOperationClose, name='moperation-close'),

   url(r'^fueling/create/$', PanelFuelingCreate, name='fueling-create'),
   url(r'^remotefueling/update/(?P<pk>\d+)/$', RemoteFuelingUpdate.as_view(), name='remote-fueling-update'),
   url(r'^remotefueling/details/(?P<pk>\d+)/$', RemoteFuelingDetails.as_view(), name='remote-fueling-details'),
   url(r'^remotefueling/delete/(?P<pk>\d+)/$', RemoteFuelingDelete.as_view(), name='remote-fueling-delete'),

   url(r'^smsreport/create/$', PanelSMSReportCreate, name='smsreport-create'),
   url(r'^smsreport/list/(?P<pk>\d+)/$', PanelSMSReportList.as_view(), name='smsreport-list'),
   url(r'^smsreport/update/(?P<pk>\d+)/$', PanelSMSReportUpdate.as_view(), name='smsreport-update'),
   url(r'^smsreport/details/(?P<pk>\d+)/$', PanelSMSReportDetails.as_view(), name='smsreport-details'),

   url(r'^smsevent/create/$', PanelSMSEventCreate, name='smsevent-create'),
   url(r'^smsevent/list/(?P<pk>\d+)/$', PanelSMSEventList.as_view(), name='smsevent-list'),
   url(r'^smsevent/update/(?P<pk>\d+)/$', PanelSMSEventUpdate.as_view(), name='smsevent-update'),
   url(r'^smsevent/details/(?P<pk>\d+)/$', PanelSMSEventDetails.as_view(), name='smsevent-details'),
   url(r'^smsevent/pkbwl/$', Report_PKBWL, name='smsevent-pkbwl'),

   url(r'^_duties/$', change_duties, name='change_duties'),

]