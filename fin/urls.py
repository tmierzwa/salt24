from django.conf.urls import url
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

urlpatterns = [

    url(r'^fueltank/list/$', FuelTanktList.as_view(), name='tank-list'),
    url(r'^fueltank/info/(?P<pk>\d+)/$', FuelTankInfo.as_view(), name='tank-info'),
    url(r'^fueltank/deliveries/(?P<pk>\d+)/$', FuelTankDeliveries.as_view(), name='tank-deliveries'),
    url(r'^fueltank/transfers/(?P<type>\w+)/(?P<pk>\d+)/$', FuelTankTransfers.as_view(), name='tank-transfers'),
    url(r'^fueltank/corrections/(?P<pk>\d+)/$', FuelTankCorrections.as_view(), name='tank-corrections'),
    url(r'^fueltank/fuelings/(?P<pk>\d+)/$', FuelTankFuelings.as_view(), name='tank-fuelings'),
    url(r'^fueltank/pdtfuelings/(?P<pk>\d+)/$', FuelTankPDTFuelings.as_view(), name='tank-pdt-fuelings'),
    url(r'^fueltank/create/$', FuelTankCreate.as_view(), name='tank-create'),
    url(r'^fueltank/update/(?P<pk>\d+)/$', FuelTankUpdate.as_view(), name='tank-update'),
    url(r'^fueltank/delete/(?P<pk>\d+)/$', FuelTankDelete.as_view(), name='tank-delete'),

    url(r'^pdt/list/$', PDTList.as_view(), name='pdt-list'),
    url(r'^pdt/feed/$', PDT_feed.as_view(), name='pdt-feed'),

    url(r'^delivery/details/(?P<pk>\d+)/$', DeliveryDetails.as_view(), name='delivery-details'),
    url(r'^delivery/create/(?P<fueltank_id>\d+)/$', DeliveryCreate.as_view(), name='delivery-create'),
    url(r'^delivery/update/(?P<pk>\d+)/$', DeliveryUpdate.as_view(), name='delivery-update'),
    url(r'^delivery/delete/(?P<pk>\d+)/$', DeliveryDelete.as_view(), name='delivery-delete'),

    url(r'^transfer/details/(?P<type>\w+)/(?P<pk>\d+)/$', TransferDetails.as_view(), name='transfer-details'),
    url(r'^transfer/create/(?P<type>\w+)/(?P<fueltank_id>\d+)/$', TransferCreate.as_view(), name='transfer-create'),
    url(r'^transfer/update/(?P<type>\w+)/(?P<pk>\d+)/$', TransferUpdate.as_view(), name='transfer-update'),
    url(r'^transfer/delete/(?P<type>\w+)/(?P<pk>\d+)/$', TransferDelete.as_view(), name='transfer-delete'),

    url(r'^correction/details/(?P<pk>\d+)/$', CorrectionDetails.as_view(), name='correction-details'),
    url(r'^correction/create/(?P<fueltank_id>\d+)/$', CorrectionCreate.as_view(), name='correction-create'),
    url(r'^correction/update/(?P<pk>\d+)/$', CorrectionUpdate.as_view(), name='correction-update'),
    url(r'^correction/delete/(?P<pk>\d+)/$', CorrectionDelete.as_view(), name='correction-delete'),

    url(r'^fueling/details/(?P<pk>\d+)/$', FuelingDetails.as_view(), name='fueling-details'),
    url(r'^fueling/create/(?P<fueltank_id>\d+)/$', FuelingCreate.as_view(), name='fueling-create'),
    url(r'^fueling/update/(?P<pk>\d+)/$', FuelingUpdate.as_view(), name='fueling-update'),
    url(r'^fueling/delete/(?P<pk>\d+)/$', FuelingDelete.as_view(), name='fueling-delete'),

    url(r'^remotefueling/details/(?P<pk>\d+)/$', RemoteFuelingDetails.as_view(), name='remote-fueling-details'),
    url(r'^remotefueling/update/(?P<pk>\d+)/$', RemoteFuelingUpdate.as_view(), name='remote-fueling-update'),
    url(r'^remotefueling/delete/(?P<pk>\d+)/$', RemoteFuelingDelete.as_view(), name='remote-fueling-delete'),

    url(r'^pdtfueling/details/(?P<pk>\d+)/$', PDTFuelingDetails.as_view(), name='pdtfueling-details'),
    url(r'^pdtfueling/update/(?P<pk>\d+)/$', PDTFuelingUpdate.as_view(), name='pdtfueling-update'),
    url(r'^pdtfueling/delete/(?P<pk>\d+)/$', PDTFuelingDelete.as_view(), name='pdtfueling-delete'),

    url(r'^voucher/list/$', VoucherList.as_view(), name='voucher-list'),
    url(r'^voucher/done/$', VoucherDoneList.as_view(), name='voucher-done'),
    url(r'^voucher/details/(?P<pk>\d+)/$', VoucherDetails.as_view(), name='voucher-details'),
    url(r'^voucher/create/$', VoucherCreate.as_view(), name='voucher-create'),
    url(r'^voucher/update/(?P<pk>\d+)/$', VoucherUpdate.as_view(), name='voucher-update'),
    url(r'^voucher/delete/(?P<pk>\d+)/$', VoucherDelete.as_view(), name='voucher-delete'),

    url(r'^$', ContactorList.as_view(), name='contr-list'),
    url(r'^contractor/info/(?P<pk>\d+)/$', ContractorInfo.as_view(), name='contr-info'),
    url(r'^contractor/operations/(?P<pk>\d+)/$', ContractorOperations.as_view(), name='contr-operations'),
    url(r'^contractor/packages/(?P<pk>\d+)/$', ContractorPackages.as_view(), name='contr-packages'),
    url(r'^contractor/flights/(?P<type>\w+)/(?P<pk>\d+)/$', ContractorFlights.as_view(), name='contr-flights'),
    url(r'^contractor/fuelings/(?P<pk>\d+)/$', ContractorFuelings.as_view(), name='contr-fuelings'),
    url(r'^contractor/create/$', ContractorCreate.as_view(), name='contr-create'),
    url(r'^contractor/update/(?P<pk>\d+)/$', ContractorUpdate.as_view(), name='contr-update'),
    url(r'^contractor/delete/(?P<pk>\d+)/$', ContractorDelete.as_view(), name='contr-delete'),

    url(r'^package/list/$', RentPackageList.as_view(), name='package-list'),
    url(r'^package/details/(?P<pk>\d+)/$', RentPackageDetails.as_view(), name='package-details'),
    url(r'^package/create/$', RentPackageCreate.as_view(), name='package-create'),
    url(r'^package/update/(?P<pk>\d+)/$', RentPackageUpdate.as_view(), name='package-update'),
    url(r'^package/delete/(?P<pk>\d+)/$', RentPackageDelete.as_view(), name='package-delete'),
    url(r'^package/buy/(?P<contractor_id>\d+)/$', PackageBuy, name='package-buy'),
    url(r'^package/sell/(?P<pk>\d+)/$', PackageSell.as_view(), name='package-sell'),

    url(r'^operation/details/(?P<pk>\d+)/$', BalanceOperationDetails.as_view(), name='operation-details'),
    url(r'^operation/create/(?P<contractor_id>\d+)/$', BalanceOperationCreate.as_view(), name='operation-create'),
    url(r'^operation/update/(?P<pk>\d+)/$', BalanceOperationUpdate.as_view(), name='operation-update'),
    url(r'^operation/delete/(?P<pk>\d+)/$', BalanceOperationDelete.as_view(), name='operation-delete'),

    url(r'^rentprice/list/$', RentPriceList.as_view(), name='rentprice-list'),
    url(r'^rentprice/update/(?P<pk>\d+)/$', RentPriceUpdate.as_view(), name='rentprice-update'),

    url(r'^price/create/(?P<contractor_id>\d+)/$', PriceCreate.as_view(), name='price-create'),
    url(r'^price/update/(?P<pk>\d+)/$', PriceUpdate.as_view(), name='price-update'),
    url(r'^price/delete/(?P<pk>\d+)/$', PriceDelete.as_view(), name='price-delete'),

    url(r'^fuel/report/$', FuelReport, name='fuel-report'),
    url(r'^fuel/export/(?P<type>\d+)/(?P<report_start>\d{4}-\d{2}-\d{2})/(?P<report_end>\d{4}-\d{2}-\d{2})/$', FuelExport, name='fuel-export'),

    url(r'^_contr/$', update_contr, name='update_contr'),

]
