from datetime import datetime, timedelta
from collections import OrderedDict
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission

from salt.models import MyDurationField

from camo.models import Aircraft, CAMO_operation, MS_report
from fin.models import Voucher, Contractor, FuelTank
from ato.models import Training_inst, Instructor

class FastManager(models.Manager):
    def get_queryset(self):
        return super(FastManager, self).get_queryset().select_related()

# Funkcja określająca porządek PDT
def pdt_order(pdt1, pdt2, order):

    if pdt1 and pdt2:
        if pdt1.date < pdt2.date:
            comp = 'lt'
        elif pdt1.date > pdt2.date:
            comp = 'gt'
        else:
            if pdt1.tth_start < pdt2.tth_start:
                comp = 'lt'
            elif pdt1.tth_start > pdt2.tth_start:
                comp = 'gt'
            else:
                if pdt1.pdt_ref < pdt2.pdt_ref:
                    comp = 'lt'
                elif pdt1.pdt_ref > pdt2.pdt_ref:
                    comp = 'gt'
                else:
                    if pdt1.open_time < pdt2.open_time:
                        comp = 'lt'
                    elif pdt1.open_time > pdt2.open_time:
                        comp = 'gt'
                    else:
                        comp = 'eq'
    else:
        comp = ''

    # trzeci argument może przyjmować wartości lt, lte, gt, gte, eq, neq
    if order == 'lt':
        res = (comp == 'lt')
    elif order == 'lte':
        res = (comp in ('lt', 'eq'))
    elif order == 'gt':
        res = (comp == 'gt')
    elif order == 'gte':
        res = (comp in ('gt', 'eq'))
    elif order == 'eq':
        res = (comp == 'eq')
    elif order == 'neq':
        res = (comp != 'eq')
    else:
        res = False

    return res


# Rozszerzony profil użytkownika systemu
class FBOUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Login')
    contractor = models.ForeignKey('fin.Contractor', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Kontrahent')
    active = models.BooleanField(default=True, verbose_name='Aktywny')
    first_name = models.CharField(max_length=100, verbose_name='Imię')
    second_name = models.CharField(max_length=100, verbose_name='Nazwisko')
    email = models.EmailField(blank=True, null=True, verbose_name='Adres email')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon kontaktowy')
    address1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='Adres linia 1')
    address2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='Adres linia 2')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Data urodzenia')
    pesel = models.CharField(max_length=11, blank=True, null=True, verbose_name='Numer PESEL')
    id_number = models.CharField(max_length=11, blank=True, null=True, verbose_name='Numer dowodu')
    infos = models.BooleanField(default=False, verbose_name='Dostęp do INFOS')
    mechanic = models.BooleanField(default=False, verbose_name='Mechanik')
    ncr_user = models.BooleanField(default=False, verbose_name='Odpowiedzialny w NCR')
    module_ato = models.IntegerField(choices= [(0, 'Brak dostępu'),
                                               (1, 'Tylko odczyt'),
                                               (2, 'Pełen dostęp')], default=0, verbose_name='Moduł ATO')
    module_camo = models.IntegerField(choices=[(0, 'Brak dostępu'),
                                               (1, 'Tylko odczyt'),
                                               (2, 'Pełen dostęp')], default=0, verbose_name='Moduł CAMO')
    module_sms = models.IntegerField(choices= [(0, 'Brak dostępu'),
                                               (1, 'Tylko odczyt'),
                                               (2, 'Pełen dostęp'),
                                               (3, 'Dostęp NCR')], default=0, verbose_name='Moduł SMS')
    module_fin = models.IntegerField(choices= [(0, 'Brak dostępu'),
                                               (1, 'Tylko odczyt'),
                                               (2, 'Pełny dostęp')], default=0, verbose_name='Moduł FIN')
    module_res = models.IntegerField(choices= [(0, 'Brak dostępu'),
                                               (1, 'Tworzenie'),
                                               (2, 'Zarządzanie')], default=1, verbose_name='Moduł RES')

    objects = FastManager()

    def save(self, *args, **kwargs):
        res = super(FBOUser, self).save(*args, **kwargs)

        # usuń wszystkie uprawnienia
        for permission in ['ato_admin', 'ato_reader', 'camo_admin', 'camo_reader', 'fin_admin', 'fin_reader',
                           'sms_admin', 'sms_reader', 'sms_ncr', 'res_user', 'res_admin']:
            self.user.user_permissions.remove(Permission.objects.get(codename=permission))

        # ustaw uprawnienia zgodnie z wyborem
        if self.module_ato == 2:
            self.user.user_permissions.add(Permission.objects.get(codename='ato_admin'))
        if self.module_ato >= 1:
            self.user.user_permissions.add(Permission.objects.get(codename='ato_reader'))

        if self.module_camo == 2:
            self.user.user_permissions.add(Permission.objects.get(codename='camo_admin'))
        if self.module_camo >= 1:
            self.user.user_permissions.add(Permission.objects.get(codename='camo_reader'))

        if self.module_fin == 2:
            self.user.user_permissions.add(Permission.objects.get(codename='fin_admin'))
        if self.module_fin >= 1:
            self.user.user_permissions.add(Permission.objects.get(codename='fin_reader'))

        if self.module_sms == 3:
            self.user.user_permissions.add(Permission.objects.get(codename='sms_ncr'))
        if self.module_sms == 2:
            self.user.user_permissions.add(Permission.objects.get(codename='sms_admin'))
            self.user.user_permissions.add(Permission.objects.get(codename='sms_ncr'))
            self.user.user_permissions.add(Permission.objects.get(codename='sms_reader'))
        if self.module_sms == 1:
            self.user.user_permissions.add(Permission.objects.get(codename='sms_reader'))

        if self.module_res == 2:
            self.user.user_permissions.add(Permission.objects.get(codename='res_admin'))
        if self.module_res >= 1:
            self.user.user_permissions.add(Permission.objects.get(codename='res_user'))

        # odśwież uprawnienia w cache
        self.user.refresh_from_db()

        return res


    def __str__(self):
        return ' '.join([self.second_name, self.first_name])

    def open_pdt(self):
        return self.pdt_open_by_set.filter(status='open').first()

    def open_operation(self):
        open_pdt = self.open_pdt()
        if open_pdt:
            return open_pdt.operation_set.filter(status='open').first()
        else:
            return None


# Profil pilota
class Pilot(models.Model):
    fbouser = models.OneToOneField(FBOUser, on_delete=models.CASCADE, verbose_name='Użytkownik')
    licence = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numer licencji')
    licence_date = models.DateField(blank=True, null=True, verbose_name='Ważność licencji')
    medical = models.CharField(max_length=50, blank=True, null=True, verbose_name='Badania lotnicze')
    medical_date = models.DateField(blank=True, null=True, verbose_name='Ważność badań')
    clearance = models.CharField(max_length=100, blank=True, null=True, verbose_name='Upoważnienie SALT')
    employee = models.BooleanField(default=False, verbose_name='Kontrola czasu pracy')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def __str__(self):
        return self.fbouser.__str__()


# Ratingi pilota
class Rating(models.Model):
    pilot = models.ForeignKey(Pilot, verbose_name='Pilot', on_delete=models.CASCADE)
    rating = models.CharField(max_length=50, verbose_name='Nazwa uprawnienia')
    valid_date = models.DateField(blank=True, null=True, verbose_name='Ważność uprawnienia')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def __str__(self):
        return self.rating


# Rodzaje lotów
def FlightTypes():
    flight_types = {'01' : '01 - Przewóz lotniczy',
                    '01A': '01A - Lot widokowy',
                    '02' : '02 - Operacje specjal.',
                    '02H': '02H - Operacje specjal. HR',
                    '03A': '03A - Szkolenie AOC',
                    '03B': '03B - Szkolenie ATO',
                    '03C': '03C - Szkolenie SPO',
                    '03D': '03D - Lot zapoznawczy',
                    '03E': '03E - Lot egzaminacyjny',
                    '04' : '04 - Wynajem SP',
                    '05' : '05 - Loty niepłatne',
                    '06' : '06 - Oblot techniczny',
                    '06A': '06A - Sprawdzenie SP',
                    '07' : '07 - Lot prywatny'}
    return OrderedDict(sorted(flight_types.items(), key=lambda item: item[0]))


# Pokładowy dziennik techniczny
class PDT(models.Model):
    pdt_ref = models.IntegerField(verbose_name='Numer PDT')
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    flight_type = models.CharField(max_length=3, verbose_name='Rodzaj lotu')
    date = models.DateField(verbose_name='Data PDT')
    pic = models.ForeignKey(Pilot, related_name='pdt_pic_set', verbose_name='Pierwszy pilot', on_delete=models.CASCADE)
    sic = models.ForeignKey(Pilot, blank=True, null=True, on_delete=models.SET_NULL, related_name='pdt_sic_set', verbose_name='Drugi pilot')
    instructor = models.ForeignKey(Pilot, blank=True, null=True, on_delete=models.SET_NULL, related_name='pdt_instr_set', verbose_name='Instruktor nadzorujący')
    voucher = models.ForeignKey(Voucher, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Voucher')
    ext_voucher = models.CharField(max_length=100, blank=True, null=True, verbose_name='Voucher obcy')
    training = models.ForeignKey(Training_inst, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Szkolenie')
    contractor = models.ForeignKey(Contractor, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Kontrahent')
    service_remarks = models.TextField(blank=True, null=True, verbose_name='Opis usługi')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    tth_start = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Licznik początkowy')
    fuel_after = models.IntegerField(blank=True, null=True, verbose_name='Tankowanie po locie')
    fuel_after_source = models.CharField(max_length=10, default='unknown', verbose_name='Źródło paliwa po locie')
    prev_tth = models.DecimalField(max_digits=7, decimal_places=2, default=0, blank=True, null=True, verbose_name='Suma TTH z przeniesienia')
    prev_landings = models.IntegerField(default=0, blank=True, null=True, verbose_name='Suma lądowań z przeniesienia')
    pre_cycles = models.IntegerField(default=0, blank=True, null=True, verbose_name='Suma cykli z przeniesienia')
    ms_report = models.ForeignKey(MS_report, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Na podstawie MS')
    failure_desc = models.TextField(blank=True, null=True, verbose_name='Opis usterki')
    repair_desc = models.TextField(blank=True, null=True, verbose_name='Sposób usunięcia')
    repair_time = models.DateTimeField(blank=True, null=True, verbose_name='Czas usunięcia')
    reapair_user = models.ForeignKey(FBOUser, related_name='pdt_repaired_by_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Usunięta przez')
    reservation = models.ForeignKey('res.Reservation', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Na podstawie rezerwacji')
    status = models.CharField(max_length=10,
                              choices=[('open', 'Otwarty'), ('closed', 'Zamknięty'), ('checked', 'Sprawdzony')],
                              default='open',
                              verbose_name='Status')
    open_user = models.ForeignKey(FBOUser, related_name='pdt_open_by_set', verbose_name='Otwarty przez', null=True, on_delete=models.SET_NULL)
    open_time = models.DateTimeField(auto_now_add=True, verbose_name='Czas otwarcia')
    close_user = models.ForeignKey(FBOUser, related_name='pdt_closed_by_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zamknięty przez')
    close_time = models.DateTimeField(blank=True, null=True, verbose_name='Czas zamknięcia')
    check_user = models.ForeignKey(FBOUser, related_name='pdt_checked_by_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Sprawdzony przez')
    check_time = models.DateTimeField(blank=True, null=True, verbose_name='Czas sprawdzenia')
    next_pdt = models.OneToOneField('PDT', blank=True, null=True, on_delete=models.SET_NULL, related_name='prev_pdt', verbose_name='Następny PDT dla SP')

    objects = FastManager()

    def save(self, *args, **kwargs):

        # jeśli nowy PDT to trzeba zmienić kolejność
        reorder = (self.pk is None)

        # sprawdź czy PDT jest obecnie na właściwej pozycji względem następnego
        if not reorder and self.next_pdt:
            reorder = not pdt_order(self, self.next_pdt, 'lte')

        # sprawdź czy PDT jest obecnie na właściwej pozycji względem poprzedniego
        if not reorder and hasattr(self, 'prev_pdt'):
            reorder = not pdt_order(self.prev_pdt, self, 'lte')

        # jeśli zmiana kolejności to ustal miejsce w łańcuchu następstw PDT
        if reorder:

            # zapamiętaj, który PDT był następny
            prev_next_pdt = self.next_pdt

            try:
                # weź ostatniego PDT jeśli istnieje, pomijając samego siebie
                prev_pdt = self.aircraft.pdt_set.filter(next_pdt=None).last()
            except:
                prev_pdt = None

            # cofaj się tak długo, aż wstawisz we właściwe miejsce
            while prev_pdt:

                # pomiń w łańcuchu samego siebie
                if prev_pdt.pk == self.pk:
                    if hasattr(self, 'prev_pdt'):
                        prev_pdt = self.prev_pdt
                    else:
                        prev_pdt = None
                else:
                    # jeśli trafił w dobre miejsce
                    if pdt_order(self, prev_pdt, 'gte'):
                        self.next_pdt = prev_pdt.next_pdt
                        break
                    else:
                        # jeśli doszliśmy do początku
                        if hasattr(prev_pdt, 'prev_pdt'):
                            prev_pdt = prev_pdt.prev_pdt
                        else:
                            self.next_pdt = prev_pdt
                            prev_pdt = None
        else:
            prev_pdt = None
            prev_next_pdt = None

        # skasuj wskaźnik w poprzednim PDT (żeby nie było konfliktu unikalności)
        if reorder and prev_pdt:
            prev_pdt.next_pdt = None
            prev_pdt.save()

        # skasuj wskaźnik w poprzednim-poprzednim PDT (żeby nie było konfliktu unikalności)
        if reorder and hasattr(self, 'prev_pdt'):
            prev_prev_pdt = self.prev_pdt
            prev_prev_pdt.next_pdt = None
            prev_prev_pdt.save()
        else:
            prev_prev_pdt = None

        # zapisz PDT
        res = super(PDT, self).save(*args, **kwargs)

        # jeśli przesunięcie to zaktualizuj wskaźnik w poprzednim PDT
        if reorder and prev_pdt:
            prev_pdt.next_pdt = self
            prev_pdt.save()

        # jeśli przesunięcie to zaktualizuj wskaźnik w poprzednim-poprzednim PDT
        if reorder and prev_prev_pdt:
            prev_prev_pdt.next_pdt = prev_next_pdt
            prev_prev_pdt.save()

        # jeśli wstawiono jako ostatni PDT to zaktualizuj liczniki w SP
        if not self.next_pdt:
            self.aircraft.last_pdt_ref = self.pdt_ref
            self.aircraft.save()

        # sprawdź czy istnieje powiązana operacja CAMO #
        try:
            camo_oper = self.camo_operation
        except ObjectDoesNotExist:
            camo_oper = None

        # zaktualizuj lub utwórz operację CAMO #
        if camo_oper:
            camo_oper.aircraft = Aircraft.objects.get(pk=self.aircraft_id)
            camo_oper.pdt_ref = self.pdt_ref
            camo_oper.date = self.date
            camo_oper.tth_start = self.tth_start
            camo_oper.tth_end = self.tth_end()
            camo_oper.landings = self.landings_sum()
            camo_oper.cycles = self.cycles_sum()
        else:
            camo_oper = CAMO_operation(aircraft = Aircraft.objects.get(pk=self.aircraft_id),
                                       pdt = self,
                                       pdt_ref = self.pdt_ref,
                                       date = self.date,
                                       tth_start = self.tth_start,
                                       tth_end = self.tth_end(),
                                       landings = self.landings_sum(),
                                       cycles = self.cycles_sum())
        camo_oper.full_clean()
        camo_oper.save()

        # Zapisanie pozycji czasu pracy
        # Jeśli PDT ma jakieś operacje i nie jest otwarty
        if len(self.operation_set.filter(status='closed')) > 0 and self.status != 'open':

            # zainicjowanie liczników
            fdp_time = block_time = timedelta(seconds=0)
            landings = 0

            # wyznaczenie posortowanej tableli zamkniętych operacji na PDT
            operation_set = []
            for operation in self.operation_set.filter(status='closed').order_by('time_start'):
                off_block = datetime.combine(self.date, operation.time_start)
                on_block = datetime.combine(self.date, operation.time_end)
                if on_block < off_block:
                    on_block += timedelta(days=1)
                operation_set += [{'off_block': off_block, 'on_block': on_block, 'landings': operation.landings}]

            # bufory przed dla FDP w zależności od rodzaju lotu
            if self.flight_type in ['03B', '03C', '03D', '03E']:
                pre_buffer = timedelta(seconds=30*60)
            elif self.flight_type in ['02', '02H', '04', '05']:
                pre_buffer = timedelta(seconds=15*60)
            else:
                pre_buffer = timedelta(seconds=0)

            # bufory po dla FDP w zależności od rodzaju lotu
            if self.flight_type in ['03B', '03C', '03D', '03E', '02', '02H', '04', '05']:
                post_buffer = timedelta(seconds=15*60)
            else:
                post_buffer = timedelta(seconds=0)

            # wyznaczenie FDP dla poszcególnych operacji
            for i in range(0, len(operation_set)):
                # jeśli poprzednia zakończyła się wcześniej niż post_buffer temu to start od początku operacji
                if i > 0 and (operation_set[i]['off_block'] - operation_set[i-1]['on_block'] <= post_buffer):
                    start_fdp = operation_set[i]['off_block']
                # jeśli między operacjami nie ma czasu na post i pre_buffer to start po post_buffer poprzedniej
                elif i > 0 and (operation_set[i]['off_block'] - operation_set[i-1]['on_block'] <= (pre_buffer + post_buffer)):
                    start_fdp = operation_set[i-1]['on_block'] + post_buffer
                # wystarczający odstęp albo pierwsza operacji
                else:
                    start_fdp = operation_set[i]['off_block'] - pre_buffer

                # jeśli nastęona rozpoczęła się wcześniej niż post_buffer po tej to koniec na początku następnej
                if i < len(operation_set)-1 and (operation_set[i+1]['off_block'] - operation_set[i]['on_block'] <= post_buffer):
                    end_fdp = operation_set[i+1]['off_block']
                # wystarczający odstęp lub ostatnia
                else:
                    end_fdp = operation_set[i]['on_block'] + post_buffer

                fdp_time += end_fdp - start_fdp
                block_time += operation_set[i]['on_block'] - operation_set[i]['off_block']
                landings += operation_set[i]['landings']

            start_duty = operation_set[0]['off_block'] - pre_buffer
            end_duty = operation_set[-1]['on_block'] + post_buffer
            duty_time = end_duty - start_duty

            if self.pic.employee:
                try:
                    duty = Duty.objects.get(pilot=self.pic, pdt=self)
                except:
                    duty = Duty(pilot=self.pic, pdt=self)

                duty.date = self.date
                duty.company = 'salt'
                duty.role = 'Pilot PIC'
                duty.duty_type = FlightTypes()[self.flight_type]
                duty.duty_time = duty_time
                duty.duty_time_from = start_duty.time()
                duty.duty_time_to = end_duty.time()
                duty.fdp_time = fdp_time
                duty.block_time = block_time
                duty.time_factor = 1 if self.aircraft.helicopter else 1
                duty.landings = landings
                duty.remarks = '%s - PDT %s' % (self.aircraft, '{:0>6d}'.format(self.pdt_ref))

                duty.full_clean()
                duty.save()

            if self.sic and self.sic.employee:
                try:
                    duty = Duty.objects.get(pilot=self.sic, pdt=self)
                except:
                    duty = Duty(pilot=self.sic, pdt=self)

                duty.date = self.date
                duty.company = 'salt'
                duty.role = 'Pilot SIC'
                duty.duty_type = FlightTypes()[self.flight_type]
                duty.duty_time = duty_time
                duty.duty_time_from = start_duty.time()
                duty.duty_time_to = end_duty.time()
                duty.fdp_time = fdp_time
                duty.block_time = block_time
                duty.time_factor = 1 if self.aircraft.helicopter else 1
                duty.landings = landings
                duty.remarks = '%s - PDT %s' % (self.aircraft, '{:0>6d}'.format(self.pdt_ref))

                duty.full_clean()
                duty.save()

        return res

    def delete(self, *args, **kwargs):

        # Jeśli to był ostatni PDT to zaktualizj informacje dla SP
        if not self.next_pdt:
            last_pdt_ref = self.prev_pdt.pdt_ref if hasattr(self, 'prev_pdt') else 0
            self.aircraft.last_pdt_ref = last_pdt_ref
            self.aircraft.save()

        # Zaktualizowanie operacji finansowej
        for balance_operation in self.balanceoperation_set.all():
            balance_operation.pdt = None
            balance_operation.document = self.__str__()
            balance_operation.full_clean()
            balance_operation.save()

        # Usunięcie operacji CAMO
        try:
            self.camo_operation.delete()
        except ObjectDoesNotExist:
            pass

        # Zapamiętanie informacji o następnym przed usunięciem PDT
        next_pdt = self.next_pdt
        prev_pdt = self.prev_pdt if hasattr(self, 'prev_pdt') else None

        # Usunięcie PDTa
        res = super(PDT, self).delete(*args, **kwargs)

        # Przeczepienie sekwencji PDTów
        if prev_pdt:
            prev_pdt.next_pdt = next_pdt
            prev_pdt.save()

        return res

    def __str__(self):
        return ' '.join([self.aircraft.registration, '{:0>6d}'.format(self.pdt_ref)])

    def pdt_sum(self):
        return self.operation_set.aggregate(Sum('pax'), Sum('bags'), Sum('fuel_refill'),
                                            Sum('fuel_used'), Sum('oil_refill'), Sum('landings'))

    def tth_sum(self):
        tth_sum = 0
        for operation in self.operation_set.all():
            tth_sum += operation.tth()
        return tth_sum

    def hours_sum(self):
        hours_sum = 0
        for operation in self.operation_set.all():
            hours_sum += operation.hours()[0]
        h, m = divmod(hours_sum, 60)
        return (hours_sum,h,m)

    def tth_end(self):
        tth_max = self.tth_start
        for operation in self.operation_set.all():
            if operation.tth_end or 0 > tth_max:
                tth_max = operation.tth_end or 0
        return tth_max

    def landings_sum(self):
        landings = 0
        for operation in self.operation_set.all():
            landings += operation.landings or 0
        return landings

    def cycles_sum(self):
        cycles = 0
        for operation in self.operation_set.all():
            cycles += operation.cycles or 0
        return cycles

    def fuel_sum(self):
        fuel_sum = 0
        for operation in self.operation_set.all():
            fuel_sum += operation.fuel_refill or 0
        fuel_sum += self.fuel_after or 0
        return fuel_sum

    def status_name(self):
        statuses = {'open':'Otwarty', 'closed':'Zamknięty', 'checked':'Sprawdzony'}
        return statuses[self.status]

    def status_color(self):
        statuses = {'open': '#c4e3ed', 'closed': '#ffe4b3', 'checked': '#b3ffb3'}
        return statuses[self.status]

    def flight_type_name(self):
        try:
            name = FlightTypes()[self.flight_type]
        except:
            name = ''
        return name


# Pojedyncza operacja na PDT
class Operation(models.Model):
    pdt = models.ForeignKey(PDT, on_delete=models.CASCADE)
    operation_no = models.IntegerField(blank=True, null=True, verbose_name='Nr. rejsu')
    pax = models.IntegerField(blank=True, null=True, verbose_name='Liczba pasażerow')
    bags = models.IntegerField(blank=True, null=True, verbose_name='Ciężar bagazu [kg]')
    fuel_refill = models.IntegerField(default=0, verbose_name='Uzupełnione paliwo (L)')
    fuel_source = models.CharField(max_length=10, default='unknown', verbose_name='Źródło paliwa')
    fuel_available = models.IntegerField(verbose_name='Stan paliwa do lotu (L)')
    fuel_used = models.IntegerField(blank=True, null=True, verbose_name='Paliwo zużyte (L)')
    oil_refill = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name='Uzupełniony olej (qt)')
    trans_oil_refill = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, default=0, verbose_name='Uzup. olej przekł. (qt)')
    hydr_oil_refill = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, default=0, verbose_name='Uzup. olej hydr. (qt)')
    loc_start = models.CharField(max_length=20, blank=True, null=True, verbose_name='Miejsce startu')
    time_start = models.TimeField(blank=True, null=True, verbose_name='Czas off-block')
    tth_start = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Licznik początkowy')
    loc_end = models.CharField(max_length=20, blank=True, null=True, verbose_name='Miejsce lądowania')
    time_end = models.TimeField(blank=True, null=True, verbose_name='Czas on-block')
    tth_end = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Licznik końcowy')
    landings = models.IntegerField(default=0, blank=True, null=True, verbose_name='Liczba lądowań')
    cycles = models.IntegerField(default=0, blank=True, null=True, verbose_name='Liczba cykli')
    status = models.CharField(max_length=10, choices=[('open', 'Otwarta'), ('closed', 'Zamknięta')], default='open', verbose_name='Status')

    objects = FastManager()

    class Meta:
        ordering = ['operation_no']

    def save(self, *args, **kwargs):
        # przy zapisie zaktualizuj PDT
        pdt = self.pdt
        res = super(Operation, self).save(*args, **kwargs)
        if self.operation_no == 1:
            pdt.tth_start = self.tth_start
        pdt.save()
        return res

    def delete(self, *args, **kwargs):
        # przy usuwaniu zaktualizuj PDT
        pdt = self.pdt
        res = super(Operation, self).delete(*args, **kwargs)
        pdt.save()
        return res

    def __str__(self):
        return '%s/%d' % (self.pdt, self.operation_no)

    def tth(self):
        if self.tth_start and self.tth_end:
            tth = self.tth_end - self.tth_start
        else:
            tth = 0
        return tth

    def hours(self):
        if self.time_start and self.time_end:
            start = self.time_start.hour*60 + self.time_start.minute
            end = self.time_end.hour*60 + self.time_end.minute
            if start > end:
                end += 60*24
            diff = end - start
        else:
            diff = 0
        h,m = divmod(diff, 60)
        return (diff, h, m)

    def not_allocated_time(self):
        total_time = timedelta(seconds=self.hours()[0]*60)
        allocated_time = timedelta(seconds=sum([exercise.time_allocated.seconds for exercise in self.exercise_oper_set.all()]))
        if allocated_time == 0:
            allocated_time = timedelta(seconds=0)
        return total_time - allocated_time

    def not_allocated_ldg(self):
        allocated_ldg = sum([exercise.num_allocated for exercise in self.exercise_oper_set.all()])
        return self.landings - allocated_ldg


# Relacja pomiędzy pilotem a SP
class PilotAircraft(models.Model):
    pilot = models.ForeignKey(Pilot, verbose_name='Pilot', on_delete=models.CASCADE)
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)

    objects = FastManager()

# Relacja pomiędzy pilotem a rodzajem lotu
class PilotFlightType(models.Model):
    pilot = models.ForeignKey(Pilot, verbose_name='Pilot', on_delete=models.CASCADE)
    flight_type = models.CharField(max_length=3, verbose_name='Rodzaj lotu')

    objects = FastManager()

# Czas pracy / służby pilota
class Duty(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data')
    company = models.CharField(max_length=10,
                              choices=[('salt', 'SALT'), ('other', 'Poza SALT')],
                              default='salt',
                              verbose_name='Firma')
    role = models.CharField(max_length=50, verbose_name='Stanowisko')
    pdt = models.ForeignKey(PDT, blank=True, null=True, on_delete=models.SET_NULL)
    duty_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Rodzaj obowiązków')
    duty_time_from = models.TimeField(verbose_name='Rozpoczęcie')
    duty_time_to = models.TimeField(verbose_name='Zakończenie')
    duty_time = MyDurationField(verbose_name='Czas łączny')
    fdp_time = MyDurationField(blank=True, null=True, verbose_name='Czas czynności')
    block_time = MyDurationField(blank=True, null=True, verbose_name='Czas lotu')
    landings = models.IntegerField(blank=True, null=True, verbose_name='Liczba lądowań')
    time_factor = models.DecimalField(max_digits=3, decimal_places=2, default=1, verbose_name='Mnożnik czasu')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def comp_str(self):
        if self.company == 'other':
            return 'Poza SALT'
        return 'SALT'

    def __str__(self):
        return '%s / %s' % (self.date, self.pilot)

