from django.urls import re_path
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

   re_path(r'^$', PanelHome, name='panel-home'),

   re_path(r'^pilot/info/(?P<pk>\d+)/$', PilotInfo.as_view(), name='pilot-info'),
   re_path(r'^pilot/ratings/(?P<pk>\d+)/$', PilotRatings.as_view(), name='pilot-ratings'),
   re_path(r'^pilot/aircraft/(?P<pk>\d+)/$', PilotAircraftList.as_view(), name='pilot-aircraft'),
   re_path(r'^pilot/aircraft/auth/(?P<pilot_id>\d+)/$', PilotAircraftAuth, name='pilot-aircraft-auth'),
   re_path(r'^pilot/types/(?P<pk>\d+)/$', PilotTypesList.as_view(), name='pilot-types'),
   re_path(r'^pilot/types/auth/(?P<pilot_id>\d+)/$', PilotTypesAuth, name='pilot-types-auth'),
   re_path(r'^pilot/flights/(?P<type>\w+)/(?P<pk>\d+)/$', PilotFlights.as_view(), name='pilot-flights'),
   re_path(r'^pilot/duties/(?P<pk>\d+)/$', PilotDuties.as_view(), name='pilot-duties'),
   re_path(r'^pilot/update/(?P<pk>\d+)/$', PilotUpdate.as_view(), name='pilot-update'),

   re_path(r'^duty/info/(?P<pk>\d+)/$', DutyDetails.as_view(), name='duty-details'),
   re_path(r'^duty/create/(?P<pilot_id>\d+)/$', DutyCreate.as_view(), name='duty-create'),
   re_path(r'^duty/update/(?P<pk>\d+)/$', DutyUpdate.as_view(), name='duty-update'),
   re_path(r'^duty/delete/(?P<pk>\d+)/$', DutyDelete.as_view(), name='duty-delete'),
   re_path(r'^duty/report/(?P<pilot_id>\d+)/$', PilotDutyReport, name='duty-report'),
   re_path(r'^duty/export/(?P<pilot_id>\d+)/(?P<ym>\d+)/(?P<type>\d+)/$', PilotDutyExport, name='duty-export'),
   re_path(r'^plan/report/(?P<pilot_id>\d+)/$', PilotPlanReport, name='plan-report'),
   re_path(r'^plan/export/(?P<pilot_id>\d+)/(?P<date_from>\d+)/(?P<date_to>\d+)/(?P<type>\d+)/$', PilotPlanExport, name='plan-export'),

   re_path(r'^rating/details/(?P<pk>\d+)/$', RatingDetails.as_view(), name='rating-details'),
   re_path(r'^rating/create/(?P<pilot_id>\d+)/$', RatingCreate.as_view(), name='rating-create'),
   re_path(r'^rating/update/(?P<pk>\d+)/$', RatingUpdate.as_view(), name='rating-update'),
   re_path(r'^rating/delete/(?P<pk>\d+)/$', RatingDelete.as_view(), name='rating-delete'),

   re_path(r'^pdt/active/$', PDTActive.as_view(), name='pdt-active'),
   re_path(r'^pdt/feed/$', PDTActive_feed.as_view(), name='pdt-active-feed'),
   re_path(r'^pdt/info/(?P<pk>\d+)/$', PDTInfo.as_view(), name='pdt-info'),
   re_path(r'^pdt/aoc/(?P<pk>\d+)/$', PDTAOC.as_view(), name='pdt-aoc'),
   re_path(r'^pdt/view/(?P<pk>\d+)/$', PDTView.as_view(), name='pdt-view'),
   re_path(r'^pdt/intro/(?P<pk>\d+)/$', PDTIntro.as_view(), name='pdt-intro'),
   re_path(r'^pdt/spo/(?P<pk>\d+)/$', PDTSPO.as_view(), name='pdt-spo'),
   re_path(r'^pdt/ato/(?P<pk>\d+)/$', PDTTraining.as_view(), name='pdt-ato'),
   re_path(r'^pdt/exam/(?P<pk>\d+)/$', PDTExam.as_view(), name='pdt-exam'),
   re_path(r'^pdt/rent/(?P<pk>\d+)/$', PDTRent.as_view(), name='pdt-rent'),
   re_path(r'^pdt/fuel/(?P<pk>\d+)/$', PDTFuel.as_view(), name='pdt-fuel'),
   re_path(r'^pdt/duties/(?P<pk>\d+)/$', PDTDuties.as_view(), name='pdt-duties'),
   re_path(r'^pdt/form/(?P<pk>\d+)/$', PDTForm.as_view(), name='pdt-form'),
   re_path(r'^pdt/open/$', PDTOpen, name='pdt-open'),
   re_path(r'^pdt/update/(?P<pk>\d+)/$', PDTUpdate, name='pdt-update'),
   re_path(r'^pdt/delete/(?P<pk>\d+)/$', PDTDelete.as_view(), name='pdt-delete'),

   re_path(r'^operation/open/(?P<pdt_id>\d+)/$', OperationOpen, name='operation-open'),
   re_path(r'^operation/update/(?P<pk>\d+)/$', OperationUpdate, name='operation-update'),
   re_path(r'^operation/delete/(?P<pk>\d+)/$', OperationDelete.as_view(), name='operation-delete'),

   re_path(r'^mpdt/open0/$', MobilePDTOpen0, name='mpdt-open0'),
   re_path(r'^mpdt/open1/$', MobilePDTOpen1, name='mpdt-open1'),
   re_path(r'^mpdt/open2/$', MobilePDTOpen2, name='mpdt-open2'),
   re_path(r'^mpdt/open3/$', MobilePDTOpen3, name='mpdt-open3'),
   re_path(r'^mpdt/close/(?P<pdt_id>\d+)/$', MobilePDTClose, name='mpdt-close'),

   re_path(r'^moperation/open/(?P<pdt_id>\d+)/$', MobileOperationOpen, name='moperation-open'),
   re_path(r'^moperation/close/(?P<operation_id>\d+)/$', MobileOperationClose, name='moperation-close'),

   re_path(r'^fueling/create/$', PanelFuelingCreate, name='fueling-create'),
   re_path(r'^remotefueling/update/(?P<pk>\d+)/$', RemoteFuelingUpdate.as_view(), name='remote-fueling-update'),
   re_path(r'^remotefueling/details/(?P<pk>\d+)/$', RemoteFuelingDetails.as_view(), name='remote-fueling-details'),
   re_path(r'^remotefueling/delete/(?P<pk>\d+)/$', RemoteFuelingDelete.as_view(), name='remote-fueling-delete'),

   re_path(r'^smsreport/create/$', PanelSMSReportCreate, name='smsreport-create'),
   re_path(r'^smsreport/list/(?P<pk>\d+)/$', PanelSMSReportList.as_view(), name='smsreport-list'),
   re_path(r'^smsreport/update/(?P<pk>\d+)/$', PanelSMSReportUpdate.as_view(), name='smsreport-update'),
   re_path(r'^smsreport/details/(?P<pk>\d+)/$', PanelSMSReportDetails.as_view(), name='smsreport-details'),

   re_path(r'^smsevent/create/$', PanelSMSEventCreate, name='smsevent-create'),
   re_path(r'^smsevent/list/(?P<pk>\d+)/$', PanelSMSEventList.as_view(), name='smsevent-list'),
   re_path(r'^smsevent/update/(?P<pk>\d+)/$', PanelSMSEventUpdate.as_view(), name='smsevent-update'),
   re_path(r'^smsevent/details/(?P<pk>\d+)/$', PanelSMSEventDetails.as_view(), name='smsevent-details'),
   re_path(r'^smsevent/pkbwl/$', Report_PKBWL, name='smsevent-pkbwl'),

   re_path(r'^_duties/$', change_duties, name='change_duties'),

]