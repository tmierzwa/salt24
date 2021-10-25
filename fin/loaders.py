from datetime import date
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from fin.models import Contractor, RentPackage, SoldPackage


def update_contr(request):

    packages = [(2524,3,43.09,440.00,''),
                (2072,9,18.59,2000.00,'Cena indywidualna'),
                (2112,9,30.00,1500.00,'Cena indywidualna'),
                (2577,9,7.47,1735.00,''),
                (2582,8,5.00,1734.96,'Cena indywidualna'),
                (2631,8,5.00,1800.00,'Cena indywidualna')]

    for pack_data in packages:
        package = SoldPackage()
        contr = Contractor.objects.get(contractor_id=str(pack_data[0]))
        rp = RentPackage.objects.get(pk=pack_data[1])

        package.contractor = contr
        package.date = date(day=1, month=1, year=2017)
        package.package_id = rp.package_id
        package.name = rp.name
        package.ac_type = rp.ac_type
        package.hours = rp.hours
        package.left_hours = Decimal(str(pack_data[2]))
        package.hour_price = Decimal(str(pack_data[3]))
        package.remarks = pack_data[4]

        package.full_clean()
        package.save()

    return HttpResponseRedirect(reverse('dispatcher'))


