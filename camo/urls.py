from django.conf.urls import url

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

urlpatterns = [
    url(r'^$', AircraftList.as_view(), name='aircraft-list'),
    url(r'^aircraft/create/$', AircraftCreate, name='aircraft-create'),
    url(r'^aircraft/update/(?P<pk>\d+)/$', AircraftUpdate.as_view(), name='aircraft-update'),
    url(r'^aircraft/fuelupdate/(?P<pk>\d+)/$', AircraftFuelUpdate.as_view(), name='aircraft-fuel-update'),
    url(r'^aircraft/msgupdate/(?P<pk>\d+)/$', AircraftMsgUpdate.as_view(), name='aircraft-msg-update'),
    url(r'^aircraft/delete/(?P<pk>\d+)/$', AircraftDelete.as_view(), name='aircraft-delete'),
    url(r'^aircraft/clone/$', AircraftClone, name='aircraft-clone'),
    url(r'^aircraft/info/(?P<pk>\d+)/$', AircraftInfo.as_view(), name='aircraft-info'),
    url(r'^aircraft/parts/(?P<pk>\d+)/$', AircraftParts.as_view(), name='aircraft-parts'),
    url(r'^aircraft/pots/(?P<pk>\d+)/$', AircraftPOTs.as_view(), name='aircraft-pots'),
    url(r'^aircraft/orders/(?P<pk>\d+)/$', AircraftOrders.as_view(), name='aircraft-orders'),
    url(r'^aircraft/opers/(?P<pk>\d+)/$', AircraftOpers.as_view(), name='aircraft-opers'),
    url(r'^aircraft/mods/(?P<pk>\d+)/$', AircraftMods.as_view(), name='aircraft-mods'),
    url(r'^aircraft/wbs/(?P<pk>\d+)/$', AircraftWBs.as_view(), name='aircraft-wbs'),
    url(r'^aircraft/ms/(?P<pk>\d+)/$', AircraftStatements.as_view(), name='aircraft-ms'),
    url(r'^aircraft/arc/(?P<pk>\d+)/$', AircraftARC.as_view(), name='aircraft-arc'),
    url(r'^aircraft/fuel/(?P<pk>\d+)/$', AircraftFuel.as_view(), name='aircraft-fuel'),
    url(r'^aircraft/msg/(?P<pk>\d+)/$', AircraftMsg.as_view(), name='aircraft-msg'),

    url(r'^part/list/$', PartList.as_view(), name='part-list'),
    url(r'^part/create/$', PartCreate.as_view(), name='part-create'),
    url(r'^part/update/(?P<pk>\d+)/$', PartUpdate.as_view(), name='part-update'),
    url(r'^part/delete/(?P<pk>\d+)/$', PartDelete.as_view(), name='part-delete'),
    url(r'^part/info/(?P<pk>\d+)/$', PartInfo.as_view(), name='part-info'),
    url(r'^part/history/(?P<pk>\d+)/$', PartHistory.as_view(), name='part-history'),
    url(r'^part/pots/(?P<pk>\d+)/$', PartPOTs.as_view(), name='part-pots'),
    url(r'^part/dirs/(?P<pk>\d+)/$', PartDirs.as_view(), name='part-dirs'),
    url(r'^part/sbs/(?P<pk>\d+)/$', PartSBs.as_view(), name='part-sbs'),
    url(r'^part/llp/(?P<pk>\d+)/$', PartLLP.as_view(), name='part-llp'),
    url(r'^part/ovhs/(?P<pk>\d+)/$', PartOvhs.as_view(), name='part-ovhs'),
    url(r'^part/purge/(?P<type>\w+)/(?P<part_id>\d+)/$', PartPurge, name='part-purge'),

    url(r'^assignpart/create/(?P<aircraft_id>\d+)/$', AssignExistingPartCreate, name='assign-existing-part-create'),
    url(r'^assignpart/new/(?P<aircraft_id>\d+)/$', AssignNewPartCreate, name='assign-new-part-create'),
    url(r'^assignpart/update/(?P<assignment_id>\d+)/$', AssignmentUpdate, name='assign-part-update'),
    url(r'^assignpart/delete/(?P<assignment_id>\d+)/$', AssignmentDelete, name='assign-part-delete'),

    url(r'^potgroup/create/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupCreate.as_view(), name='pot-group-create'),
    url(r'^potgroup/upload/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupUpload, name='pot-group-upload'),
    url(r'^potgroup/import/(?P<type>\w+)/(?P<part_id>\d+)/$', POTGroupImport, name='pot-group-import'),
    url(r'^potgroup/clone/(?P<potgroup_id>\d+)/$', POTGroupClone, name='pot-group-clone'),
    url(r'^potgroup/update/(?P<type>\w+)/(?P<pk>\d+)/$', POTGroupUpdate.as_view(), name='pot-group-update'),
    url(r'^potgroup/delete/(?P<pk>\d+)/$', POTGroupDelete.as_view(), name='pot-group-delete'),
    url(r'^potgroup/info/(?P<pk>\d+)/$', POTGroupInfo.as_view(), name='pot-group-info'),
    url(r'^potgroup/events/(?P<pk>\d+)/$', POTGroupEvents.as_view(), name='pot-group-events'),

    url(r'^potevent/details/(?P<pk>\d+)/$', POTEventDetails.as_view(), name='pot-event-details'),
    url(r'^potevent/create/(?P<pot_group_id>\d+)/$', POTEventCreate.as_view(), name='pot-event-create'),
    url(r'^potevent/upload/(?P<pot_group_id>\d+)/$', POTEventUpload, name='pot-event-upload'),
    url(r'^potevent/import/(?P<pot_group_id>\d+)/$', POTEventImport, name='pot-event-import'),
    url(r'^potevent/update/(?P<pk>\d+)/$', POTEventUpdate.as_view(), name='pot-event-update'),
    url(r'^potevent/delete/(?P<pk>\d+)/$', POTEventDelete.as_view(), name='pot-event-delete'),

    url(r'^ata/list/$', ATAList.as_view(), name='ata-list'),
    url(r'^ata/details/(?P<pk>\d+)/$', ATADetails.as_view(), name='ata-details'),
    url(r'^ata/create/$', ATACreate.as_view(), name='ata-create'),
    url(r'^ata/update/(?P<pk>\d+)/$', ATAUpdate.as_view(), name='ata-update'),
    url(r'^ata/delete/(?P<pk>\d+)/$', ATADelete.as_view(), name='ata-delete'),

    url(r'^order/list/$', WorkOrderList.as_view(), name='order-list'),
    url(r'^order/details/(?P<pk>\d+)/$', WorkOrderDetails.as_view(), name='order-details'),
    url(r'^order/close/(?P<work_order_id>\d+)/$', WorkOrderClose, name='order-close'),
    url(r'^order/create/(?P<aircraft_id>\d+)/$', WorkOrderCreate, name='order-create'),

    url(r'^crs/create/(?P<work_order_id>\d+)/$', CRSCreate, name='crs-create'),

    url(r'^modification/details/(?P<pk>\d+)/$', ModificationDetails.as_view(), name='modification-details'),
    url(r'^modification/create/(?P<aircraft_id>\d+)/$', ModificationCreate.as_view(), name='modification-create'),
    url(r'^modification/update/(?P<pk>\d+)/$', ModificationUpdate.as_view(), name='modification-update'),
    url(r'^modification/delete/(?P<pk>\d+)/$', ModificationDelete.as_view(), name='modification-delete'),

    url(r'^wb/details/(?P<pk>\d+)/$', WBDetails.as_view(), name='wb-details'),
    url(r'^wb/create/(?P<aircraft_id>\d+)/$', WBCreate.as_view(), name='wb-create'),
    url(r'^wb/update/(?P<pk>\d+)/$', WBUpdate.as_view(), name='wb-update'),
    url(r'^wb/delete/(?P<pk>\d+)/$', WBDelete.as_view(), name='wb-delete'),

    url(r'^ms/details/(?P<pk>\d+)/$', MSDetails.as_view(), name='ms-details'),
    url(r'^ms/create/(?P<aircraft_id>\d+)/$', MSCreate.as_view(), name='ms-create'),
    url(r'^ms/update/(?P<pk>\d+)/$', MSUpdate.as_view(), name='ms-update'),
    url(r'^ms/delete/(?P<pk>\d+)/$', MSDelete.as_view(), name='ms-delete'),

    url(r'^oper/details/(?P<pk>\d+)/$', OperDetails.as_view(), name='oper-details'),
    url(r'^oper/create/(?P<aircraft_id>\d+)/$', OperCreate.as_view(), name='oper-create'),
    url(r'^oper/update/(?P<pk>\d+)/$', OperUpdate.as_view(), name='oper-update'),
    url(r'^oper/delete/(?P<pk>\d+)/$', OperDelete.as_view(), name='oper-delete'),

    url(r'^pdt/list/$', PDTControlList.as_view(), name='pdt-list'),
    url(r'^pdt/info/(?P<pk>\d+)/$', PDTControlInfo.as_view(), name='pdt-info'),
    url(r'^pdt/oper/(?P<pk>\d+)/$', PDTControlOperations.as_view(), name='pdt-oper'),
    url(r'^pdt/update/(?P<pk>\d+)/$', PDTControlUpdate.as_view(), name='pdt-update'),
    url(r'^pdt/delete/(?P<pk>\d+)/$', PDTControlDelete.as_view(), name='pdt-delete'),
    url(r'^pdt/close/(?P<pdt_id>\d+)/$', MobilePDTClose, name='pdt-close'),
    url(r'^pdt/check/(?P<pdt_id>\d+)/$', PDTCheck, name='pdt-check'),

    url(r'^pdtoper/create/(?P<pdt_id>\d+)/$', PDTOperCreate.as_view(), name='pdt-oper-create'),
    url(r'^pdtoper/update/(?P<pk>\d+)/$', PDTOperUpdate.as_view(), name='pdt-oper-update'),
    url(r'^pdtoper/delete/(?P<pk>\d+)/$', PDTOperDelete.as_view(), name='pdt-oper-delete'),

    url(r'^report/parts/(?P<aircraft_id>\d+)/$', ReportParts, name='report-parts'),
    url(r'^report/arc/(?P<aircraft_id>\d+)/$', ReportARC, name='report-arc'),

    url(r'^_update/$', update, name='update-aircraft'),
    url(r'^_check/$', check_history, name='check-pdts'),

]
