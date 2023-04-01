from django.urls import re_path
from fin.views import FuelTanktList, FuelTankCreate, FuelTankUpdate, FuelTankDelete
from fin.views import FuelTankInfo, FuelTankDeliveries, FuelTankTransfers, FuelTankCorrections
from fin.views import FuelTankFuelings, FuelTankPDTFuelings
from fin.views import DeliveryDetails, DeliveryCreate, DeliveryUpdate, DeliveryDelete
from fin.views import TransferDetails, TransferCreate, TransferUpdate, TransferDelete
from fin.views import CorrectionDetails, CorrectionCreate, CorrectionUpdate, CorrectionDelete
from fin.views import FuelingDetails, FuelingCreate, FuelingUpdate, FuelingDelete
from fin.views import PDTFuelingDetails, PDTFuelingUpdate, PDTFuelingDelete
from fin.views import VoucherList, VoucherDetails, VoucherCreate, VoucherUpdate, VoucherDelete, VoucherDoneList
from fin.views import RentPackageList, RentPackageDetails, RentPackageCreate, RentPackageUpdate, RentPackageDelete
from fin.views import RentPriceList, RentPriceUpdate
from fin.views import PackageBuy, PackageSell
from fin.views import ContactorList, ContractorInfo, ContractorCreate, ContractorUpdate, ContractorDelete
from fin.views import ContractorOperations, ContractorPackages, ContractorFlights, ContractorFuelings
from fin.views import RemoteFuelingDetails, RemoteFuelingUpdate, RemoteFuelingDelete
from fin.views import BalanceOperationDetails, BalanceOperationCreate, BalanceOperationUpdate, BalanceOperationDelete
from fin.views import PriceCreate, PriceUpdate, PriceDelete
from fin.views import FuelReport, FuelExport
from fin.views import PDTList, PDT_feed
from fin.loaders import update_contr

app_name = "fin"

urlpatterns = [

    re_path(r'^fueltank/list/$', FuelTanktList.as_view(), name='tank-list'),
    re_path(r'^fueltank/info/(?P<pk>\d+)/$', FuelTankInfo.as_view(), name='tank-info'),
    re_path(r'^fueltank/deliveries/(?P<pk>\d+)/$', FuelTankDeliveries.as_view(), name='tank-deliveries'),
    re_path(r'^fueltank/transfers/(?P<type>\w+)/(?P<pk>\d+)/$', FuelTankTransfers.as_view(), name='tank-transfers'),
    re_path(r'^fueltank/corrections/(?P<pk>\d+)/$', FuelTankCorrections.as_view(), name='tank-corrections'),
    re_path(r'^fueltank/fuelings/(?P<pk>\d+)/$', FuelTankFuelings.as_view(), name='tank-fuelings'),
    re_path(r'^fueltank/pdtfuelings/(?P<pk>\d+)/$', FuelTankPDTFuelings.as_view(), name='tank-pdt-fuelings'),
    re_path(r'^fueltank/create/$', FuelTankCreate.as_view(), name='tank-create'),
    re_path(r'^fueltank/update/(?P<pk>\d+)/$', FuelTankUpdate.as_view(), name='tank-update'),
    re_path(r'^fueltank/delete/(?P<pk>\d+)/$', FuelTankDelete.as_view(), name='tank-delete'),

    re_path(r'^pdt/list/$', PDTList.as_view(), name='pdt-list'),
    re_path(r'^pdt/feed/$', PDT_feed.as_view(), name='pdt-feed'),

    re_path(r'^delivery/details/(?P<pk>\d+)/$', DeliveryDetails.as_view(), name='delivery-details'),
    re_path(r'^delivery/create/(?P<fueltank_id>\d+)/$', DeliveryCreate.as_view(), name='delivery-create'),
    re_path(r'^delivery/update/(?P<pk>\d+)/$', DeliveryUpdate.as_view(), name='delivery-update'),
    re_path(r'^delivery/delete/(?P<pk>\d+)/$', DeliveryDelete.as_view(), name='delivery-delete'),

    re_path(r'^transfer/details/(?P<type>\w+)/(?P<pk>\d+)/$', TransferDetails.as_view(), name='transfer-details'),
    re_path(r'^transfer/create/(?P<type>\w+)/(?P<fueltank_id>\d+)/$', TransferCreate.as_view(), name='transfer-create'),
    re_path(r'^transfer/update/(?P<type>\w+)/(?P<pk>\d+)/$', TransferUpdate.as_view(), name='transfer-update'),
    re_path(r'^transfer/delete/(?P<type>\w+)/(?P<pk>\d+)/$', TransferDelete.as_view(), name='transfer-delete'),

    re_path(r'^correction/details/(?P<pk>\d+)/$', CorrectionDetails.as_view(), name='correction-details'),
    re_path(r'^correction/create/(?P<fueltank_id>\d+)/$', CorrectionCreate.as_view(), name='correction-create'),
    re_path(r'^correction/update/(?P<pk>\d+)/$', CorrectionUpdate.as_view(), name='correction-update'),
    re_path(r'^correction/delete/(?P<pk>\d+)/$', CorrectionDelete.as_view(), name='correction-delete'),

    re_path(r'^fueling/details/(?P<pk>\d+)/$', FuelingDetails.as_view(), name='fueling-details'),
    re_path(r'^fueling/create/(?P<fueltank_id>\d+)/$', FuelingCreate.as_view(), name='fueling-create'),
    re_path(r'^fueling/update/(?P<pk>\d+)/$', FuelingUpdate.as_view(), name='fueling-update'),
    re_path(r'^fueling/delete/(?P<pk>\d+)/$', FuelingDelete.as_view(), name='fueling-delete'),

    re_path(r'^remotefueling/details/(?P<pk>\d+)/$', RemoteFuelingDetails.as_view(), name='remote-fueling-details'),
    re_path(r'^remotefueling/update/(?P<pk>\d+)/$', RemoteFuelingUpdate.as_view(), name='remote-fueling-update'),
    re_path(r'^remotefueling/delete/(?P<pk>\d+)/$', RemoteFuelingDelete.as_view(), name='remote-fueling-delete'),

    re_path(r'^pdtfueling/details/(?P<pk>\d+)/$', PDTFuelingDetails.as_view(), name='pdtfueling-details'),
    re_path(r'^pdtfueling/update/(?P<pk>\d+)/$', PDTFuelingUpdate.as_view(), name='pdtfueling-update'),
    re_path(r'^pdtfueling/delete/(?P<pk>\d+)/$', PDTFuelingDelete.as_view(), name='pdtfueling-delete'),

    re_path(r'^voucher/list/$', VoucherList.as_view(), name='voucher-list'),
    re_path(r'^voucher/done/$', VoucherDoneList.as_view(), name='voucher-done'),
    re_path(r'^voucher/details/(?P<pk>\d+)/$', VoucherDetails.as_view(), name='voucher-details'),
    re_path(r'^voucher/create/$', VoucherCreate.as_view(), name='voucher-create'),
    re_path(r'^voucher/update/(?P<pk>\d+)/$', VoucherUpdate.as_view(), name='voucher-update'),
    re_path(r'^voucher/delete/(?P<pk>\d+)/$', VoucherDelete.as_view(), name='voucher-delete'),

    re_path(r'^$', ContactorList.as_view(), name='contr-list'),
    re_path(r'^contractor/info/(?P<pk>\d+)/$', ContractorInfo.as_view(), name='contr-info'),
    re_path(r'^contractor/operations/(?P<pk>\d+)/$', ContractorOperations.as_view(), name='contr-operations'),
    re_path(r'^contractor/packages/(?P<pk>\d+)/$', ContractorPackages.as_view(), name='contr-packages'),
    re_path(r'^contractor/flights/(?P<type>\w+)/(?P<pk>\d+)/$', ContractorFlights.as_view(), name='contr-flights'),
    re_path(r'^contractor/fuelings/(?P<pk>\d+)/$', ContractorFuelings.as_view(), name='contr-fuelings'),
    re_path(r'^contractor/create/$', ContractorCreate.as_view(), name='contr-create'),
    re_path(r'^contractor/update/(?P<pk>\d+)/$', ContractorUpdate.as_view(), name='contr-update'),
    re_path(r'^contractor/delete/(?P<pk>\d+)/$', ContractorDelete.as_view(), name='contr-delete'),

    re_path(r'^package/list/$', RentPackageList.as_view(), name='package-list'),
    re_path(r'^package/details/(?P<pk>\d+)/$', RentPackageDetails.as_view(), name='package-details'),
    re_path(r'^package/create/$', RentPackageCreate.as_view(), name='package-create'),
    re_path(r'^package/update/(?P<pk>\d+)/$', RentPackageUpdate.as_view(), name='package-update'),
    re_path(r'^package/delete/(?P<pk>\d+)/$', RentPackageDelete.as_view(), name='package-delete'),
    re_path(r'^package/buy/(?P<contractor_id>\d+)/$', PackageBuy, name='package-buy'),
    re_path(r'^package/sell/(?P<pk>\d+)/$', PackageSell.as_view(), name='package-sell'),

    re_path(r'^operation/details/(?P<pk>\d+)/$', BalanceOperationDetails.as_view(), name='operation-details'),
    re_path(r'^operation/create/(?P<contractor_id>\d+)/$', BalanceOperationCreate.as_view(), name='operation-create'),
    re_path(r'^operation/update/(?P<pk>\d+)/$', BalanceOperationUpdate.as_view(), name='operation-update'),
    re_path(r'^operation/delete/(?P<pk>\d+)/$', BalanceOperationDelete.as_view(), name='operation-delete'),

    re_path(r'^rentprice/list/$', RentPriceList.as_view(), name='rentprice-list'),
    re_path(r'^rentprice/update/(?P<pk>\d+)/$', RentPriceUpdate.as_view(), name='rentprice-update'),

    re_path(r'^price/create/(?P<contractor_id>\d+)/$', PriceCreate.as_view(), name='price-create'),
    re_path(r'^price/update/(?P<pk>\d+)/$', PriceUpdate.as_view(), name='price-update'),
    re_path(r'^price/delete/(?P<pk>\d+)/$', PriceDelete.as_view(), name='price-delete'),

    re_path(r'^fuel/report/$', FuelReport, name='fuel-report'),
    re_path(r'^fuel/export/(?P<type>\d+)/(?P<report_start>\d{4}-\d{2}-\d{2})/(?P<report_end>\d{4}-\d{2}-\d{2})/$', FuelExport, name='fuel-export'),

    re_path(r'^_contr/$', update_contr, name='update_contr'),

]
