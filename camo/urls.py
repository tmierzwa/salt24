from django.urls import re_path

from camo.views import AircraftList, AircraftCreate, AircraftUpdate, AircraftDelete, AircraftClone, AircraftARC
from camo.views import AircraftFuel, AircraftFuelUpdate, AircraftMsg, AircraftMsgUpdate
from camo.views import AircraftInfo, AircraftPOTs, AircraftParts, AircraftOrders, AircraftOpers, AircraftMods, AircraftWBs
from camo.views import AircraftStatements, MSDetails, MSCreate, MSUpdate, MSDelete
from camo.views import PartList, PartCreate, PartUpdate, PartDelete, PartPurge
from camo.views import PartInfo, PartHistory, PartPOTs, PartDirs, PartSBs, PartLLP, PartOvhs
from camo.views import AssignExistingPartCreate, AssignNewPartCreate, AssignmentUpdate, AssignmentDelete
from camo.views import POTGroupCreate, POTGroupClone, POTGroupUpdate, POTGroupDelete
from camo.views import POTGroupInfo, POTGroupEvents
from camo.views import POTEventDetails, POTEventCreate, POTEventUpdate, POTEventDelete
from camo.views import ATAList, ATADetails, ATACreate, ATAUpdate, ATADelete
from camo.views import WorkOrderCreate, WorkOrderList, WorkOrderDetails, WorkOrderClose, CRSCreate
from camo.views import ModificationDetails, ModificationCreate, ModificationDelete, ModificationUpdate
from camo.views import WBDetails, WBCreate, WBUpdate, WBDelete
from camo.views import OperDetails, OperCreate, OperUpdate, OperDelete
from camo.views import PDTControlList, PDTControlInfo, PDTControlUpdate, PDTControlDelete, PDTCheck
from camo.views import PDTControlOperations, PDTOperCreate, PDTOperUpdate, PDTOperDelete

from panel.views import MobilePDTClose

from camo.loaders import POTGroupUpload, POTGroupImport
from camo.loaders import POTEventUpload, POTEventImport

from camo.loaders import update, check_history

from camo.reports import ReportParts, ReportARC

app_name = "camo"

urlpatterns = [
    re_path(r'^$', AircraftList.as_view(), name='aircraft-list'),
    re_path(r'^aircraft/create/$', AircraftCreate, name='aircraft-create'),
    re_path(r'^aircraft/update/(?P<pk>\d+)/$', AircraftUpdate.as_view(), name='aircraft-update'),
    re_path(r'^aircraft/fuelupdate/(?P<pk>\d+)/$', AircraftFuelUpdate.as_view(), name='aircraft-fuel-update'),
    re_path(r'^aircraft/msgupdate/(?P<pk>\d+)/$', AircraftMsgUpdate.as_view(), name='aircraft-msg-update'),
    re_path(r'^aircraft/delete/(?P<pk>\d+)/$', AircraftDelete.as_view(), name='aircraft-delete'),
    re_path(r'^aircraft/clone/$', AircraftClone, name='aircraft-clone'),
    re_path(r'^aircraft/info/(?P<pk>\d+)/$', AircraftInfo.as_view(), name='aircraft-info'),
    re_path(r'^aircraft/parts/(?P<pk>\d+)/$', AircraftParts.as_view(), name='aircraft-parts'),
    re_path(r'^aircraft/pots/(?P<pk>\d+)/$', AircraftPOTs.as_view(), name='aircraft-pots'),
    re_path(r'^aircraft/orders/(?P<pk>\d+)/$', AircraftOrders.as_view(), name='aircraft-orders'),
    re_path(r'^aircraft/opers/(?P<pk>\d+)/$', AircraftOpers.as_view(), name='aircraft-opers'),
    re_path(r'^aircraft/mods/(?P<pk>\d+)/$', AircraftMods.as_view(), name='aircraft-mods'),
    re_path(r'^aircraft/wbs/(?P<pk>\d+)/$', AircraftWBs.as_view(), name='aircraft-wbs'),
    re_path(r'^aircraft/ms/(?P<pk>\d+)/$', AircraftStatements.as_view(), name='aircraft-ms'),
    re_path(r'^aircraft/arc/(?P<pk>\d+)/$', AircraftARC.as_view(), name='aircraft-arc'),
    re_path(r'^aircraft/fuel/(?P<pk>\d+)/$', AircraftFuel.as_view(), name='aircraft-fuel'),
    re_path(r'^aircraft/msg/(?P<pk>\d+)/$', AircraftMsg.as_view(), name='aircraft-msg'),

    re_path(r'^part/list/$', PartList.as_view(), name='part-list'),
    re_path(r'^part/create/$', PartCreate.as_view(), name='part-create'),
    re_path(r'^part/update/(?P<pk>\d+)/$', PartUpdate.as_view(), name='part-update'),
    re_path(r'^part/delete/(?P<pk>\d+)/$', PartDelete.as_view(), name='part-delete'),
    re_path(r'^part/info/(?P<pk>\d+)/$', PartInfo.as_view(), name='part-info'),
    re_path(r'^part/history/(?P<pk>\d+)/$', PartHistory.as_view(), name='part-history'),
    re_path(r'^part/pots/(?P<pk>\d+)/$', PartPOTs.as_view(), name='part-pots'),
    re_path(r'^part/dirs/(?P<pk>\d+)/$', PartDirs.as_view(), name='part-dirs'),
    re_path(r'^part/sbs/(?P<pk>\d+)/$', PartSBs.as_view(), name='part-sbs'),
    re_path(r'^part/llp/(?P<pk>\d+)/$', PartLLP.as_view(), name='part-llp'),
    re_path(r'^part/ovhs/(?P<pk>\d+)/$', PartOvhs.as_view(), name='part-ovhs'),
    re_path(r'^part/purge/(?P<type>\w+)/(?P<part_id>\d+)/$', PartPurge, name='part-purge'),

    re_path(r'^assignpart/create/(?P<aircraft_id>\d+)/$', AssignExistingPartCreate, name='assign-existing-part-create'),
    re_path(r'^assignpart/new/(?P<aircraft_id>\d+)/$', AssignNewPartCreate, name='assign-new-part-create'),
    re_path(r'^assignpart/update/(?P<assignment_id>\d+)/$', AssignmentUpdate, name='assign-part-update'),
    re_path(r'^assignpart/delete/(?P<assignment_id>\d+)/$', AssignmentDelete, name='assign-part-delete'),

    re_path(r'^potgroup/create/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupCreate.as_view(), name='pot-group-create'),
    re_path(r'^potgroup/upload/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupUpload, name='pot-group-upload'),
    re_path(r'^potgroup/import/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupImport, name='pot-group-import'),
    re_path(r'^potgroup/clone/(?P<potgroup_id>\d+)/$', POTGroupClone, name='pot-group-clone'),
    re_path(r'^potgroup/update/(?P<type>\w+)/(?P<pk>\d+)/$', POTGroupUpdate.as_view(), name='pot-group-update'),
    re_path(r'^potgroup/delete/(?P<pk>\d+)/$', POTGroupDelete.as_view(), name='pot-group-delete'),
    re_path(r'^potgroup/info/(?P<pk>\d+)/$', POTGroupInfo.as_view(), name='pot-group-info'),
    re_path(r'^potgroup/events/(?P<pk>\d+)/$', POTGroupEvents.as_view(), name='pot-group-events'),

    re_path(r'^potevent/details/(?P<pk>\d+)/$', POTEventDetails.as_view(), name='pot-event-details'),
    re_path(r'^potevent/create/(?P<pot_group_id>\d+)/$', POTEventCreate.as_view(), name='pot-event-create'),
    re_path(r'^potevent/upload/(?P<pot_group_id>\d+)/$', POTEventUpload, name='pot-event-upload'),
    re_path(r'^potevent/import/(?P<pot_group_id>\d+)/$', POTEventImport, name='pot-event-import'),
    re_path(r'^potevent/update/(?P<pk>\d+)/$', POTEventUpdate.as_view(), name='pot-event-update'),
    re_path(r'^potevent/delete/(?P<pk>\d+)/$', POTEventDelete.as_view(), name='pot-event-delete'),

    re_path(r'^ata/list/$', ATAList.as_view(), name='ata-list'),
    re_path(r'^ata/details/(?P<pk>\d+)/$', ATADetails.as_view(), name='ata-details'),
    re_path(r'^ata/create/$', ATACreate.as_view(), name='ata-create'),
    re_path(r'^ata/update/(?P<pk>\d+)/$', ATAUpdate.as_view(), name='ata-update'),
    re_path(r'^ata/delete/(?P<pk>\d+)/$', ATADelete.as_view(), name='ata-delete'),

    re_path(r'^order/list/$', WorkOrderList.as_view(), name='order-list'),
    re_path(r'^order/details/(?P<pk>\d+)/$', WorkOrderDetails.as_view(), name='order-details'),
    re_path(r'^order/close/(?P<work_order_id>\d+)/$', WorkOrderClose, name='order-close'),
    re_path(r'^order/create/(?P<aircraft_id>\d+)/$', WorkOrderCreate, name='order-create'),

    re_path(r'^crs/create/(?P<work_order_id>\d+)/$', CRSCreate, name='crs-create'),

    re_path(r'^modification/details/(?P<pk>\d+)/$', ModificationDetails.as_view(), name='modification-details'),
    re_path(r'^modification/create/(?P<aircraft_id>\d+)/$', ModificationCreate.as_view(), name='modification-create'),
    re_path(r'^modification/update/(?P<pk>\d+)/$', ModificationUpdate.as_view(), name='modification-update'),
    re_path(r'^modification/delete/(?P<pk>\d+)/$', ModificationDelete.as_view(), name='modification-delete'),

    re_path(r'^wb/details/(?P<pk>\d+)/$', WBDetails.as_view(), name='wb-details'),
    re_path(r'^wb/create/(?P<aircraft_id>\d+)/$', WBCreate.as_view(), name='wb-create'),
    re_path(r'^wb/update/(?P<pk>\d+)/$', WBUpdate.as_view(), name='wb-update'),
    re_path(r'^wb/delete/(?P<pk>\d+)/$', WBDelete.as_view(), name='wb-delete'),

    re_path(r'^ms/details/(?P<pk>\d+)/$', MSDetails.as_view(), name='ms-details'),
    re_path(r'^ms/create/(?P<aircraft_id>\d+)/$', MSCreate.as_view(), name='ms-create'),
    re_path(r'^ms/update/(?P<pk>\d+)/$', MSUpdate.as_view(), name='ms-update'),
    re_path(r'^ms/delete/(?P<pk>\d+)/$', MSDelete.as_view(), name='ms-delete'),

    re_path(r'^oper/details/(?P<pk>\d+)/$', OperDetails.as_view(), name='oper-details'),
    re_path(r'^oper/create/(?P<aircraft_id>\d+)/$', OperCreate.as_view(), name='oper-create'),
    re_path(r'^oper/update/(?P<pk>\d+)/$', OperUpdate.as_view(), name='oper-update'),
    re_path(r'^oper/delete/(?P<pk>\d+)/$', OperDelete.as_view(), name='oper-delete'),

    re_path(r'^pdt/list/$', PDTControlList.as_view(), name='pdt-list'),
    re_path(r'^pdt/info/(?P<pk>\d+)/$', PDTControlInfo.as_view(), name='pdt-info'),
    re_path(r'^pdt/oper/(?P<pk>\d+)/$', PDTControlOperations.as_view(), name='pdt-oper'),
    re_path(r'^pdt/update/(?P<pk>\d+)/$', PDTControlUpdate.as_view(), name='pdt-update'),
    re_path(r'^pdt/delete/(?P<pk>\d+)/$', PDTControlDelete.as_view(), name='pdt-delete'),
    re_path(r'^pdt/close/(?P<pdt_id>\d+)/$', MobilePDTClose, name='pdt-close'),
    re_path(r'^pdt/check/(?P<pdt_id>\d+)/$', PDTCheck, name='pdt-check'),

    re_path(r'^pdtoper/create/(?P<pdt_id>\d+)/$', PDTOperCreate.as_view(), name='pdt-oper-create'),
    re_path(r'^pdtoper/update/(?P<pk>\d+)/$', PDTOperUpdate.as_view(), name='pdt-oper-update'),
    re_path(r'^pdtoper/delete/(?P<pk>\d+)/$', PDTOperDelete.as_view(), name='pdt-oper-delete'),

    re_path(r'^report/parts/(?P<aircraft_id>\d+)/$', ReportParts, name='report-parts'),
    re_path(r'^report/arc/(?P<aircraft_id>\d+)/$', ReportARC, name='report-arc'),

    re_path(r'^_update/$', update, name='update-aircraft'),
    re_path(r'^_check/$', check_history, name='check-pdts'),

]
