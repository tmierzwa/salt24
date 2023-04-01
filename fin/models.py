from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from camo.models import Aircraft


class Module(models.Model):

    class Meta:
        permissions = [('fin_reader', 'FIN - Dostęp do odczytu'),
                       ('fin_admin', 'FIN - Dostęp pełny')]

    module = models.BooleanField()


# Zbiornik paliwa
class FuelTank(models.Model):
    tank_ref = models.CharField(max_length=10, verbose_name='Symbol zbiornika')
    name = models.CharField(max_length=50, verbose_name='Nazwa zbiornika')
    fuel_type = models.CharField(max_length=5, choices=[('AVGAS', 'Avgas 100LL'),
                                                        ('MOGAS', 'Benzyna samochodowa'),
                                                        ('JETA1', 'Paliwo JET A-1')], verbose_name='Rodzaj paliwa')
    fuel_volume = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='Objętość paliwa (L)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    # obliczenie wartości paliwa w zbiorniku
    def fuel_value(self):

        # dodaj listę ostatnich dostaw (nie więcej niż objętość paliwa w zbiorniku) #
        deliveries = self.fueldelivery_set.order_by('-date')
        parts, volume = [], 0
        for part in deliveries:
            parts.append({'date':part.date, 'fuel_volume':part.fuel_volume, 'liter_price':part.liter_price})
            volume += part.fuel_volume
            if volume >= self.fuel_volume:
                break

        # dodaj listę ostatnich transferów (nie więcej niż objętość paliwa w zbiorniku) #
        transfers = self.in_transfers.order_by('-date')
        volume = 0
        for part in transfers:
            parts.append({'date':part.date, 'fuel_volume':part.fuel_volume, 'liter_price':part.liter_price})
            volume += part.fuel_volume
            if volume >= self.fuel_volume:
                break

        parts.sort(key=lambda part: part['date'], reverse=True)

        # policz wartość z poczególnych kawałków #
        volume, value = self.fuel_volume, float(0)
        for delivery in parts:
            if delivery['fuel_volume'] >= volume:
                value += float(volume) * float(delivery['liter_price'])
                break
            else:
                value += float(delivery['fuel_volume']) * float(delivery['liter_price'])
                volume -= delivery['fuel_volume']

        return value

    def __str__(self):
        return self.name


# Operacja dostawy paliwa
class FuelDelivery(models.Model):
    fueltank = models.ForeignKey(FuelTank, verbose_name='Zbiornik paliwa', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data dostawy')
    provider = models.CharField(max_length=50, blank=True, null=True, verbose_name='Dostawca paliwa')
    document = models.CharField(max_length=30, blank=True, null=True, verbose_name='Dokument dostawy')
    fuel_volume = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='Objętość paliwa (L)')
    liter_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Cena za litr (PLN)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = FuelDelivery.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj zbornik paliwa #
        if existing:
            self.fueltank.fuel_volume -= existing.fuel_volume
        self.fueltank.fuel_volume += self.fuel_volume
        self.fueltank.full_clean()
        self.fueltank.save()
        return super(FuelDelivery, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj zbiornik paliwa #
        self.fueltank.fuel_volume -= self.fuel_volume
        self.fueltank.fuel_value -= self.fuel_volume * self.liter_price
        self.fueltank.full_clean()
        self.fueltank.save()
        return super(FuelDelivery, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Dostawa do zbiornika %s z dnia %s' % (self.fueltank.tank_ref, self.date)


# Operacja wydania wewnętrznego paliwa
class FuelTransfer(models.Model):
    fueltank_from = models.ForeignKey(FuelTank, related_name='out_transfers', verbose_name='Zbiornik żródłowy', on_delete=models.CASCADE)
    fueltank_to = models.ForeignKey(FuelTank, related_name='in_transfers', verbose_name='Zbiornik docelowy', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data wydania wew.')
    document = models.CharField(max_length=30, blank=True, null=True, verbose_name='Dokument wydania wew.')
    fuel_volume = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='Objętość paliwa (L)')
    liter_price = models.FloatField(verbose_name='Średnia cena za litr (PLN)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = FuelTransfer.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # dla nowych policz średnią cenę za litr #
        if not existing:
            deliveries = self.fueltank_from.fueldelivery_set.order_by('-date')
            parts, volume = [], 0
            # dodaj listę ostatnich transferów (nie więcej niż objętość paliwa w zbiorniku źródłowym) #
            for part in deliveries:
                parts.append({'date':part.date, 'fuel_volume':part.fuel_volume, 'liter_price':part.liter_price})
                volume += part.fuel_volume
                if volume >= self.fueltank_from.fuel_volume:
                    break

            transfers = self.fueltank_from.in_transfers.order_by('-date')
            volume = 0
            # dodaj listę ostatnich dostaw (nie więcej niż objętość paliwa w zbiorniku źródłowym) #
            for part in transfers:
                parts.append({'date':part.date, 'fuel_volume':part.fuel_volume, 'liter_price':part.liter_price})
                volume += part.fuel_volume
                if volume >= self.fueltank_from.fuel_volume:
                    break

            # ogranicz połączoną listę do tych, które składają się na istniejącą objętość #
            parts.sort(key=lambda part: part['date'], reverse=True)

            volume = self.fueltank_from.fuel_volume
            for part in parts:
                if part['fuel_volume'] <= volume:
                    volume -= part['fuel_volume']
                else:
                    if volume > 0:
                        part['fuel_volume'] = volume
                        volume = 0
                    else:
                        parts.remove(part)

            # ogranicz listę tylko do tych, które składają się na przelewaną objętość #
            parts.sort(key=lambda part: part['date'])
            volume = self.fuel_volume
            for part in parts:
                if part['fuel_volume'] <= volume:
                    volume -= part['fuel_volume']
                else:
                    if volume > 0:
                        part['fuel_volume'] = volume
                        volume = 0
                    else:
                        parts.remove(part)

            # policz średnią cenę litra paliwa #
            value = float(0)
            for part in parts:
                value += float(part['fuel_volume']) * float(part['liter_price'])
            if self.fuel_volume > 0:
                self.liter_price = value / float(self.fuel_volume)
            else:
                self.liter_price = 0

        # zaktualizuj oba zborniki paliwa #
        if existing:
            self.fueltank_from.fuel_volume += existing.fuel_volume
            self.fueltank_to.fuel_volume -= existing.fuel_volume
        self.fueltank_from.fuel_volume -= self.fuel_volume
        self.fueltank_to.fuel_volume += self.fuel_volume
        self.fueltank_from.full_clean()
        self.fueltank_from.save()
        self.fueltank_to.full_clean()
        self.fueltank_to.save()

        return super(FuelTransfer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj oba zbiorniki paliwa #
        self.fueltank_from.fuel_volume += self.fuel_volume
        self.fueltank_to.fuel_volume -= self.fuel_volume
        self.fueltank_from.full_clean()
        self.fueltank_from.save()
        self.fueltank_to.full_clean()
        self.fueltank_to.save()
        return super(FuelTransfer, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Wydanie ze zbiornika %s do zbiornika %s z dnia %s' % (self.fueltank_from.tank_ref, self.fueltank_to.tank_ref, self.date)


# Operacja korekty ilości paliwa
class FuelCorrection(models.Model):
    fueltank = models.ForeignKey(FuelTank, verbose_name='Zbiornik paliwa', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data protokołu różnic')
    document = models.CharField(max_length=30, blank=True, null=True, verbose_name='Dokument protokołu różnic')
    fuel_volume = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='Objętość różnicy (L)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = FuelCorrection.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj zbornik paliwa #
        if existing:
            self.fueltank.fuel_volume -= existing.fuel_volume
        self.fueltank.fuel_volume += self.fuel_volume
        self.fueltank.full_clean()
        self.fueltank.save()
        return super(FuelCorrection, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj zbiornik paliwa #
        self.fueltank.fuel_volume -= self.fuel_volume
        self.fueltank.full_clean()
        self.fueltank.save()
        return super(FuelCorrection, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Różnica w zbiorniku %s z dnia %s' % (self.fueltank.tank_ref, self.date)


# Operacja tankowania paliwa do AC bez PDT
class LocalFueling(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    fueltank = models.ForeignKey(FuelTank, verbose_name='Zbiornik paliwa', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data tankowania')
    person = models.CharField(max_length=50, blank=True, null=True, verbose_name='Osoba tankująca')
    fuel_volume = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Objętość paliwa (L)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = LocalFueling.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj zbornik paliwa i AC #
        if existing:
            self.fueltank.fuel_volume += existing.fuel_volume
            self.aircraft.fuel_volume -= existing.fuel_volume
        self.fueltank.fuel_volume -= self.fuel_volume
        self.aircraft.fuel_volume += self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.aircraft.fuel_volume < 0:
            self.aircraft.fuel_volume = 0
        # ilosć paliwa na AC nie powina być większa od objętości zbiornika
        if self.aircraft.fuel_volume > self.aircraft.fuel_capacity:
            self.aircraft.fuel_volume = self.aircraft.fuel_capacity
        self.fueltank.full_clean()
        self.fueltank.save()
        self.aircraft.full_clean()
        self.aircraft.save()
        return super(LocalFueling, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj zbiornik paliwa i AC #
        self.fueltank.fuel_volume += self.fuel_volume
        self.aircraft.fuel_volume -= self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.aircraft.fuel_volume < 0:
            self.aircraft.fuel_volume = 0
        self.fueltank.full_clean()
        self.fueltank.save()
        self.aircraft.full_clean()
        self.aircraft.save()
        return super(LocalFueling, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Tankowanie %s z dnia %s' % (self.aircraft, self.date)


# Operacja tankowania paliwa do AC na PDT
class PDTFueling(models.Model):
    pdt = models.ForeignKey('panel.PDT', verbose_name='PDT', on_delete=models.CASCADE)
    fueltank = models.ForeignKey(FuelTank, verbose_name='Zbiornik paliwa', on_delete=models.CASCADE)
    fuel_volume = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Objętość paliwa (L)')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = PDTFueling.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj zbornik paliwa i AC #
        if existing:
            self.fueltank.fuel_volume += existing.fuel_volume
            self.pdt.aircraft.fuel_volume -= existing.fuel_volume
        self.fueltank.fuel_volume -= self.fuel_volume
        self.pdt.aircraft.fuel_volume += self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.pdt.aircraft.fuel_volume < 0:
            self.pdt.aircraft.fuel_volume = 0
        # ilosć paliwa na AC nie powina być większa od objętości zbiornika
        if self.pdt.aircraft.fuel_volume > self.pdt.aircraft.fuel_capacity:
            self.pdt.aircraft.fuel_volume = self.pdt.aircraft.fuel_capacity
        self.fueltank.full_clean()
        self.fueltank.save()
        self.pdt.aircraft.full_clean()
        self.pdt.aircraft.save()
        return super(PDTFueling, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj zbiornik paliwa i AC #
        self.fueltank.fuel_volume += self.fuel_volume
        self.pdt.aircraft.fuel_volume -= self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.pdt.aircraft.fuel_volume < 0:
            self.pdt.aircraft.fuel_volume = 0
        # ilosć paliwa na AC nie powina być większa od objętości zbiornika
        if self.pdt.aircraft.fuel_volume > self.pdt.aircraft.fuel_capacity:
            self.pdt.aircraft.fuel_volume = self.pdt.aircraft.fuel_capacity
        self.fueltank.full_clean()
        self.fueltank.save()
        self.pdt.aircraft.full_clean()
        self.pdt.aircraft.save()
        return super(PDTFueling, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Tankowanie %s z dnia %s' % (self.pdt.aircraft, self.pdt.date)


# Operacja tankowania paliwa poza SALT
class RemoteFueling(models.Model):
    pdt = models.ForeignKey('panel.PDT', verbose_name='PDT', on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True, null=True, verbose_name='Lotnisko tankowania')
    fuel_volume = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Objętość paliwa (L)')
    document = models.CharField(max_length=30, blank=True, null=True, verbose_name='Faktura za tankowanie')
    excise = models.CharField(max_length=30, blank=True, null=True, verbose_name='Dowód dostawy')
    total_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Wartość paliwa (PLN)')
    remarks  = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = RemoteFueling.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj AC #
        if existing:
            self.pdt.aircraft.fuel_volume -= existing.fuel_volume
        self.pdt.aircraft.fuel_volume += self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.pdt.aircraft.fuel_volume < 0:
            self.pdt.aircraft.fuel_volume = 0
        # ilosć paliwa na AC nie powina być większa od objętości zbiornika
        if self.pdt.aircraft.fuel_volume > self.pdt.aircraft.fuel_capacity:
            self.pdt.aircraft.fuel_volume = self.pdt.aircraft.fuel_capacity
        self.pdt.aircraft.full_clean()
        self.pdt.aircraft.save()
        return super(RemoteFueling, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj AC #
        self.pdt.aircraft.fuel_volume -= self.fuel_volume
        # ilosć paliwa na AC nie powina być mniejsza od zera
        if self.pdt.aircraft.fuel_volume < 0:
            self.pdt.aircraft.fuel_volume = 0
        # ilosć paliwa na AC nie powina być większa od objętości zbiornika
        if self.pdt.aircraft.fuel_volume > self.pdt.aircraft.fuel_capacity:
            self.pdt.aircraft.fuel_volume = self.pdt.aircraft.fuel_capacity
        self.pdt.aircraft.full_clean()
        self.pdt.aircraft.save()
        return super(RemoteFueling, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Tankowanie %s z dnia %s' % (self.pdt.aircraft, self.pdt.date)


# Vouchery prezentowe
class Voucher(models.Model):
    voucher_id = models.CharField(max_length=20, verbose_name='Identyfikator')
    voucher_code = models.CharField(max_length=10, verbose_name='Kod vouchera')
    persons = models.IntegerField(verbose_name='Liczba osób')
    time = models.IntegerField(verbose_name='Czas trwania (min)')
    description = models.CharField(max_length=100, verbose_name='Opis vouchera')
    issue_date = models.DateField(verbose_name='Data sprzedaży')
    valid_date = models.DateField(verbose_name='Data ważności')
    payment = models.CharField(max_length=10, choices=[('cash', 'Gotówka'),
                                                       ('transfer', 'Przelew bankowy'),
                                                       ('epay', 'Płatność elektroniczna')], verbose_name='Forma płatności')
    paid = models.BooleanField(default=False, verbose_name='Opłacony')
    done_date = models.DateField(blank=True, null=True, verbose_name='Data realizacji')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return "%s / %s" % (self.voucher_code, self.description)


# Kontrahenci
class Contractor(models.Model):
    contractor_id = models.CharField(max_length=20, verbose_name='Identyfikator FK')
    name = models.CharField(max_length=100, verbose_name='Nazwa kontrahenta')
    address1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='Adres kontrahenta')
    address2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='Adres kontrahenta')
    company = models.BooleanField(default=False, verbose_name='Firma')
    pesel = models.CharField(max_length=11, null=True, blank=True, verbose_name='Numer PESEL')
    nip = models.CharField(max_length=15, null=True, blank=True, verbose_name='Numer NIP')
    regon = models.CharField(max_length=9, null=True, blank=True, verbose_name='Numer REGON')
    active = models.BooleanField(default=True, verbose_name='Czy aktywny?')
    ato_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Saldo szkoleń')
    rent_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Saldo wynajmu')
    aoc_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Saldo AOC')
    spo_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Saldo usług')
    debet_allowed = models.BooleanField(default=False, verbose_name='Zgoda na debet')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return '%s - %s' % (self.contractor_id, self.name)


# Operacja na rachunku
class BalanceOperation(models.Model):
    contractor = models.ForeignKey(Contractor, verbose_name='Kontrahent', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data operacji')
    type = models.CharField(max_length=15, choices=[('Wpłata', 'Wpłata'),
                                                    ('Wypłata', 'Wypłata'),
                                                    ('Korekta', 'Korekta'),
                                                    ('Usługa AOC', 'Usługa AOC'),
                                                    ('Usługa SPO', 'Usługa SPO'),
                                                    ('Wynajem', 'Wynajem'),
                                                    ('Szkolenie', 'Szkolenie'),
                                                    ('Egzamin', 'Egzamin'),
                                                    ('Instruktor', 'Instruktor'),
                                                    ('Zakup pakietu', 'Zakup pakietu'),
                                                    ('Zwrot za pakiet', 'Zwrot za pakiet'),
                                                    ('Zwrot za paliwo', 'Zwrot za paliwo')], verbose_name='Rodzaj operacji')
    document = models.CharField(max_length=30, blank=True, null=True, verbose_name='Dokument operacji')
    pdt = models.ForeignKey('panel.PDT', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Powiązany PDT')
    ato_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Kwota operacji (szkolenia)')
    rent_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Kwota operacji (wynajem)')
    aoc_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Kwota operacji (AOC)')
    spo_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Kwota operacji (SPO)')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = BalanceOperation.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj salda rachunku #
        if existing:
            self.contractor.ato_balance -= existing.ato_amount
            self.contractor.rent_balance -= existing.rent_amount
            self.contractor.aoc_balance -= existing.aoc_amount
            self.contractor.spo_balance -= existing.spo_amount
        self.contractor.ato_balance += self.ato_amount
        self.contractor.rent_balance += self.rent_amount
        self.contractor.aoc_balance += self.aoc_amount
        self.contractor.spo_balance += self.spo_amount
        self.contractor.full_clean()
        self.contractor.save()
        return super(BalanceOperation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj salda rachunku #
        self.contractor.ato_balance -= self.ato_amount
        self.contractor.rent_balance -= self.rent_amount
        self.contractor.aoc_balance -= self.aoc_amount
        self.contractor.spo_balance -= self.spo_amount
        self.contractor.full_clean()
        self.contractor.save()
        return super(BalanceOperation, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Operacja na rachunku %s z dnia %s' % (self.contractor, self.date)


# Cennik pakietów godzin
class RentPackage(models.Model):
    package_id = models.CharField(max_length=20, verbose_name='Identyfikator pakietu')
    name = models.CharField(max_length=100, verbose_name='Nazwa pakietu')
    ac_type = models.CharField(max_length=50, verbose_name='Typ SP')
    hours = models.IntegerField(verbose_name="Liczba godzin")
    hour_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena za godzinę")
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return self.package_id


# Pakiet godzin kupiony przez kontrahenta
class SoldPackage(models.Model):
    contractor = models.ForeignKey(Contractor, verbose_name='Kontrahent', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data zakupu pakietu')
    package_id = models.CharField(max_length=20, verbose_name='Identyfikator pakietu')
    name = models.CharField(max_length=100, verbose_name='Nazwa pakietu')
    ac_type = models.CharField(max_length=50, verbose_name='Typ SP')
    hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Liczba godzin")
    left_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pozostała liczba godzin")
    hour_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena za godzinę")
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return self.package_id


# Specjalna cena dla kontrahenta
class SpecialPrice(models.Model):
    contractor = models.ForeignKey(Contractor, verbose_name='Kontrahent', on_delete=models.CASCADE)
    ac_type = models.CharField(max_length=50, verbose_name='Typ SP')
    hour_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena za godzinę")
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return 'Cena na %s dla %s' % (self.ac_type, self.contractor)

