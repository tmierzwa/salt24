from django.db import models
from datetime import date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max


class FastManager(models.Manager):
    def get_queryset(self):
        return super(FastManager, self).get_queryset().select_related()


class Module(models.Model):

    class Meta:
        permissions = [('camo_reader', 'CAMO - Dostęp do odczytu'),
                       ('camo_admin', 'CAMO - Dostęp pełny')]

    module = models.BooleanField()


class Aircraft(models.Model):

    type = models.CharField(max_length=50, verbose_name='Typ SP')
    registration = models.CharField(max_length=12, verbose_name='Rejestracja')
    helicopter = models.BooleanField(default=False, verbose_name='Śmigłowiec')
    status = models.CharField(max_length=10, choices=[('flying','W użytkowaniu'),
                                                      ('damaged','Uszkodzony'),
                                                      ('parked', 'Zaparkowany')], verbose_name='Status użytkowania')
    production_date = models.DateField(verbose_name='Data producji')
    mtow = models.IntegerField(verbose_name='MTOW')
    insurance_date = models.DateField(blank=True, null=True, verbose_name='Ważność ubezp.')
    wb_date = models.DateField(blank=True, null=True, verbose_name='Ważność W&B')
    arc_date = models.DateField(blank=True, null=True, verbose_name='Ważność ARC')
    radio_date = models.DateField(blank=True, null=True, verbose_name='Ważność radia')
    hours_count = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Suma TTH')
    landings_count = models.IntegerField(default=0, verbose_name='Suma lądowań')
    use_landings = models.BooleanField(default=False, verbose_name='Używaj lądowań')
    cycles_count = models.IntegerField(default=0, verbose_name='Suma cykli')
    use_cycles = models.BooleanField(default=False, verbose_name='Używaj cykli')
    tth = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Stan licznika na SP')
    last_pdt_ref = models.IntegerField(default=0, verbose_name='Ostatni numer PDT')
    fuel_type = models.CharField(max_length=5, choices=[('AVGAS', 'Avgas 100LL'),
                                                        ('MOGAS', 'Benzyna samochodowa'),
                                                        ('JETA1', 'Paliwo JET A-1')], verbose_name='Rodzaj paliwa')
    fuel_capacity = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='Zbiornik paliwa (L)')
    fuel_consumption = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='Zużycie paliwa (L/h)')
    fuel_volume = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='Szacowana ilość paliwa (L)')
    rent_price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Cena wynajmu (PLN/h)')
    ms_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='MS do TTH')
    ms_date = models.DateField(blank=True, null=True, verbose_name='MS do daty')
    ms_landings = models.IntegerField(blank=True, null=True, verbose_name='MS do lądowań')
    ms_cycles = models.IntegerField(blank=True, null=True, verbose_name='MS do cykli')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    scheduled = models.BooleanField(default=True, verbose_name='Podlega rezerwacjom')
    info = models.TextField(blank=True, null=True, verbose_name='Informacje dla pilotów')
    color = models.CharField(max_length=7, default='#ccffcc', verbose_name='Kolor wyświetlania')

    objects = FastManager()

    def configuration(self):
        # Funkcja zwracająca aktywne przypisania #
        return Assignment.objects.filter(aircraft=self.pk, current=True).order_by('from_date')

    def components(self):
        # Funkcja zwracająca listę przypisanych cześci #
        return [assignment.part for assignment in self.configuration()]

    def airframe(self):
        # Funkcja zwracająca ostatnią część przypisaną jako płatowiec #
        # Wybór według sekcji ATA 53-00 #
        parts_list = []
        for assignment in self.configuration():
            if assignment.ata.section == '53-00':
                parts_list.append(assignment.part)
        if parts_list:
            airframe=parts_list[-1]
        else:
            airframe = None
        return airframe

    def engines(self):
        # Funkcja zwracająca listę przypisanych silników #
        # Wybór według sekcji ATA 72-00 #
        parts_list = []
        for assignment in self.configuration():
            if assignment.ata.section in ['72(R)-00', '72(T)-00']:
                parts_list.append(assignment.part)
        return parts_list

    def propellers(self):
        # Funkcja zwracająca listę przypisanych śmigieł #
        parts_list = []
        for assignment in self.configuration():
            if assignment.ata.section=='61-00':
                parts_list.append(assignment.part)
        return parts_list

    def months_count(self, ask_date=date.today()):
        # Funkcja zwracająca liczbę miesięcy od daty produkcji do podanej daty #
        if ask_date >= self.production_date:
            m1=self.production_date.year*12+self.production_date.month
            m2=ask_date.year*12+ask_date.month
            months=m2-m1
            if self.production_date.day>ask_date.day:
                months-=1
        else:
            months = 0
        return months

    def next_date(self):
        dates = [(part.next_date() or date.max) for part in self.components()]
        if dates:
            return min(dates)
        else:
            return None

    def next_hours(self):
        all_next = [(part.next_hours() or 99999) for part in self.components()]
        if all_next:
            return min(all_next)
        else:
            return None

    def next_landings(self):
        all_next = [(part.next_landings() or 99999) for part in self.components()]
        if all_next:
            return min(all_next)
        else:
            return None

    def next_cycles(self):
        all_next = [(part.next_cycles() or 99999) for part in self.components()]
        if all_next:
            return min(all_next)
        else:
            return None

    def ins_date_ok(self):
        if (self.insurance_date or date.max) < date.today():
            return False
        return True

    def wb_date_ok(self):
        if (self.wb_date or date.max) < date.today():
            return False
        return True

    def arc_date_ok(self):
        if (self.arc_date or date.max) < date.today():
            return False
        return True

    def arc_hours_ok(self):
        if self.hours_count > (self.next_hours() or 99999):
            return False
        return True

    def arc_landings_ok(self):
        if self.landings_count > (self.next_landings() or 99999):
            return False
        return True

    def arc_cycles_ok(self):
        if self.cycles_count > (self.next_cycles() or 99999):
            return False
        return True

    def radio_date_ok(self):
        if (self.radio_date or date.max) < date.today():
            return False
        return True

    def parts_ok(self):
        # Podsumowanie statusu czynności na wszystkich częściach #
        for part in self.components():
            if not part.ms_ok():
                return False
        return True

    def ms_ok(self):
        # Status zgodności według ostatniego MS
        ms_ok = (self.hours_count<=self.ms_hours if self.ms_hours else False)
        ms_ok = ms_ok and (date.today()<=self.ms_date if self.ms_date else False)
        if self.use_landings:
            ms_ok = ms_ok and (self.landings_count<=self.ms_landings if self.ms_landings else False)
        if self.use_cycles:
            ms_ok = ms_ok and (self.cycles_count<=self.ms_cycles if self.ms_cycles else False)
        return ms_ok

    def airworthy(self):
        return self.ms_ok() and self.radio_date_ok() and self.ins_date_ok() and self.wb_date_ok()

    def status_str(self):
        statuses = {'flying':'W użytkowaniu', 'damaged':'Uszkodzony', 'parked': 'Zaparkowany'}
        return statuses[self.status]

    def __str__(self):
        return self.registration


class Part(models.Model):
    maker = models.CharField(max_length=100, verbose_name='Producent')
    part_no = models.CharField(max_length=35, verbose_name='Numer części (typ)')
    serial_no = models.CharField(max_length=35, verbose_name='Numer seryjny')
    name = models.CharField(max_length=200, verbose_name='Nazwa')
    f1 = models.CharField(max_length=50, blank=True, null=True, verbose_name='FORM-1')
    lifecycle = models.CharField(max_length=10,
                                 choices=[('llp', 'Ograniczona żywotność (LLP)'),
                                          ('ovh', 'Podlegająca remontowi (OVH)'),
                                          ('oth', 'Według stanu')],
                                 default='oth',
                                 verbose_name='Cykl życia')
    production_date = models.DateField(blank=True, null=True, verbose_name='Data produkcji')
    install_date = models.DateField(blank=True, null=True, verbose_name='Data pierwszej instalacji')
    hours_count = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Suma TTH')
    landings_count = models.IntegerField(default=0, verbose_name='Suma lądowań')
    cycles_count = models.IntegerField(default=0, verbose_name='Suma cykli')

    objects = FastManager()

    def months_count(self, ask_date=date.today()):
        # Funkcja zwracająca wiek częsci w miesiącach od daty produkcji #
        months = 0
        if self.production_date:
            if ask_date >= self.production_date:
                m1=self.production_date.year*12+self.production_date.month
                m2=ask_date.year*12+ask_date.month
                months=m2-m1
                if self.production_date.day>ask_date.day:
                    months-=1
        return months

    def months_inst_count(self, ask_date=date.today()):
        # Funkcja zwracająca wiek częsci w miesiącach od daty instalacji #
        months = 0
        if self.install_date:
            if ask_date >= self.install_date:
                m1=self.install_date.year*12+self.install_date.month
                m2=ask_date.year*12+ask_date.month
                months=m2-m1
                if self.install_date.day>ask_date.day:
                    months-=1
        return months

    def current_assignment(self):
        return self.assignment_set.filter(current=True).first()

    def next_date(self):
        dates = [(group.next_date() or date.max) for group in self.pot_group_set.all()]
        if dates:
            return min(dates)
        else:
            return None

    def next_hours(self):
        all_next = [(group.next_hours() or 99999) for group in self.pot_group_set.all()]
        if all_next:
            return min(all_next)
        else:
            return None

    def next_landings(self):
        all_next = [(group.next_landings() or 99999) for group in self.pot_group_set.all()]
        if all_next:
            return min(all_next)
        else:
            return None

    def next_cycles(self):
        all_next = [(group.next_cycles() or 99999) for group in self.pot_group_set.all()]
        if all_next:
            return min(all_next)
        else:
            return None

    def ms_ok(self):
        for group in self.pot_group_set.all():
            if (group.left_hours() or 0) < 0 or (group.left_days() or 0) < 0:
                return False
        return True

    def use_landings(self):
        if self.current_assignment():
            return self.current_assignment().aircraft.use_landings
        else:
            return True

    def use_cycles(self):
        if self.current_assignment():
            return self.current_assignment().aircraft.use_cycles
        else:
            return True

    def __str__(self):
        return '%s %s (S/N: %s)' % (self.name, self.part_no, self.serial_no)


class ATA(models.Model):
    chapter = models.CharField(max_length=5, verbose_name='Rozdział')
    chapter_title = models.CharField(max_length=100, verbose_name='Tytuł rozdziału')
    section = models.CharField(max_length=10, verbose_name='Sekcja')
    section_title = models.CharField(max_length=100, verbose_name='Tytuł sekcji')
    description = models.TextField(verbose_name='Opis')

    class Meta:
        verbose_name_plural = 'Sekcje ATA'

    def __str__(self):
        return ' '.join([self.section, self.chapter_title, self.section_title])


class Assignment(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    ata = models.ForeignKey(ATA, on_delete=models.CASCADE)
    super_ass = models.ForeignKey('Assignment', blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, null=True)
    crs = models.CharField(max_length=200, blank=True, null=True)
    from_date = models.DateField()
    from_hours = models.DecimalField(max_digits=7, decimal_places=2)
    from_landings = models.IntegerField(default=0)
    from_cycles = models.IntegerField(default=0)
    to_date = models.DateField(blank=True, null=True)
    to_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    to_landings = models.IntegerField(blank=True, null=True)
    to_cycles = models.IntegerField(blank=True, null=True)
    current = models.BooleanField(default=False)

    objects = FastManager()

    def install_tth(self):
        return self.part.hours_count - (self.aircraft.hours_count - self.from_hours)

    def __str__(self):
        if self.description:
            return ' '.join([self.aircraft.registration, self.description])
        else:
            return ' '.join([self.aircraft.registration, self.part.name])


class POT_group(models.Model):
    part = models.ForeignKey(Part, verbose_name='Powiązana część', on_delete=models.CASCADE)
    POT_ref = models.CharField(max_length=100, verbose_name='POT ref.')
    adsb_no = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numer AD/SB')
    adsb_date = models.DateField(blank=True, null=True, verbose_name='Data AD/SB')
    adsb_agency = models.CharField(max_length=20, blank=True, null=True, verbose_name='Organ wydający')
    adsb_related = models.CharField(max_length=50, blank=True, null=True, verbose_name='Powiązanie AD/SB')
    name = models.CharField(max_length=500, verbose_name='Opis')
    type = models.CharField(max_length=10,
                            choices=[('oth', 'Obsługa techniczna'),
                                     ('llp', 'Planowy demontaż'),
                                     ('ovh', 'Planowy remont'),
                                     ('ad',  'AD - Dyrektywa'),
                                     ('sb',  'SB - Biuletyn')],
                            default='oth',
                            verbose_name='Rodzaj czynności')
    due_hours = models.IntegerField(blank=True, null=True, verbose_name='Limit TTH')
    due_months = models.IntegerField(blank=True, null=True, verbose_name='Limit miesięcy')
    due_landings = models.IntegerField(blank=True, null=True, verbose_name='Limit lądowań')
    due_cycles = models.IntegerField(blank=True, null=True, verbose_name='Limit cykli')
    cyclic = models.BooleanField(default=True, verbose_name='Czynność cykliczna')
    parked = models.BooleanField(default=False, verbose_name='Czynność postojowa')
    count_type = models.CharField(max_length=10,
                                  choices=[('production', 'Od produkcji/remontu'),
                                           ('install', 'Od instalacji')],
                                  default='production',
                                  verbose_name='Sposób liczenia')
    applies = models.BooleanField(default=True, verbose_name='Dotyczy danej części')
    optional = models.BooleanField(default=False, verbose_name='Czynność opcjonalna')
    done_crs = models.CharField(max_length=20, blank=True, null=True, verbose_name='Wykonano (CRS Ref.)')
    done_date = models.DateField(blank=True, null=True, verbose_name='Wykonano (data)')
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Wykonano (TTH)')
    done_landings = models.IntegerField(blank=True, null=True, verbose_name='Wykonano (lądowania)')
    done_cycles = models.IntegerField(blank=True, null=True, verbose_name='Wykonano (cykle)')
    done_aso = models.CharField(max_length=100, blank=True, null=True, verbose_name="Wykonano (ASO)")
    remarks = models.CharField(max_length=500, blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def next_hours(self):
        if self.due_hours and self.applies:
            if self.done_hours:
                if self.cyclic:
                    next = self.done_hours + self.due_hours
                else:
                    next = None
            else:
                if self.part.current_assignment():
                    next = self.due_hours - self.part.hours_count + self.part.current_assignment().aircraft.hours_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_hours(self):
        if self.next_hours() and self.part.current_assignment():
            left = self.next_hours() - self.part.current_assignment().aircraft.hours_count
        else:
            left = None
        return left

    def next_landings(self):
        if self.due_landings and self.applies:
            if self.done_landings:
                if self.cyclic:
                    next = self.done_landings + self.due_landings
                else:
                    next = None
            else:
                if self.part.current_assignment():
                    next = self.due_landings - self.part.landings_count + self.part.current_assignment().aircraft.landings_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_landings(self):
        if self.next_landings() and self.part.current_assignment():
            left = self.next_landings() - self.part.current_assignment().aircraft.landings_count
        else:
            left = None
        return left

    def next_cycles(self):
        if self.due_cycles and self.applies:
            if self.done_cycles:
                if self.cyclic:
                    next = self.done_cycles + self.due_cycles
                else:
                    next = None
            else:
                if self.part.current_assignment():
                    next = self.due_cycles - self.part.cycles_count + self.part.current_assignment().aircraft.cycles_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_cycles(self):
        if self.next_cycles() and self.part.current_assignment():
            left = self.next_cycles() - self.part.current_assignment().aircraft.cycles_count
        else:
            left = None
        return left

    def next_date(self):

        # Funkcja dodająca do daty okresloną liczbę miesięcy #
        def add_months(start_date, delta):
            if start_date:
                year = start_date.year + delta//12
                month = start_date.month + delta%12
                if month > 12:
                    month -= 12
                    year += 1
                day = start_date.day
                try:
                    end_date = date(year, month, day)
                except ValueError:
                    end_date = date(year, month+1, 1) - timedelta(days=1)
            else:
                end_date = None
            return end_date

        if self.due_months and self.applies:
            if self.count_type == 'production':
                base_date = self.part.production_date
            else:
                base_date = self.part.install_date

            if self.cyclic:
                if self.done_date:
                    next = add_months(self.done_date, self.due_months)
                else:
                    next = add_months(base_date, self.due_months)
            else:
                if self.done_date:
                    next = None
                else:
                    next = add_months(base_date, self.due_months)
        else:
            next = None
        return next

    def left_days(self):
        if self.next_date():
            left = (self.next_date() - date.today()).days
        else:
            left = None
        return left

    def leftx (self):
        return min([(self.left_hours() or 99999), (self.left_days() or 99999), (self.left_landings() or 99999), (self.left_cycles() or 99999)])

    def __str__(self):
        return '%s - %s' % (self.POT_ref, self.name)


class POT_event(models.Model):
    POT_group = models.ForeignKey(POT_group, on_delete=models.CASCADE)
    POT_ref = models.CharField(max_length=100, verbose_name='POT Ref.')
    name = models.TextField(verbose_name='Nazwa czynności')
    done_crs = models.CharField(max_length=20, blank=True, null=True, verbose_name='Wykonano (CRS Ref.)')
    done_date = models.DateField(blank=True, null=True, verbose_name='Wykonano (data)')
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Wykonano (TTH)')
    done_landings = models.IntegerField(blank=True, null=True, verbose_name='Wykonano (lądowania)')
    done_cycles = models.IntegerField(blank=True, null=True, verbose_name='Wykonano (cykle)')

    objects = FastManager()

    def next_hours(self):
        if self.POT_group.due_hours:
            if self.done_hours:
                if self.POT_group.cyclic:
                    next = self.done_hours + self.POT_group.due_hours
                else:
                    next = None
            else:
                if self.POT_group.part.current_assignment():
                    next = self.POT_group.due_hours - self.POT_group.part.hours_count + self.POT_group.part.current_assignment().aircraft.hours_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_hours(self):
        if self.next_hours() and self.POT_group.part.current_assignment():
            left = self.next_hours() - self.POT_group.part.current_assignment().aircraft.hours_count
        else:
            left = None
        return left

    def next_landings(self):
        if self.POT_group.due_landings:
            if self.done_landings:
                if self.POT_group.cyclic:
                    next = self.done_landings + self.POT_group.due_landings
                else:
                    next = None
            else:
                if self.POT_group.part.current_assignment():
                    next = self.POT_group.due_landings - self.POT_group.part.landings_count + self.POT_group.part.current_assignment().aircraft.landings_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_landings(self):
        if self.next_landings() and self.POT_group.part.current_assignment():
            left = self.next_landings() - self.POT_group.part.current_assignment().aircraft.landings_count
        else:
            left = None
        return left

    def next_cycles(self):
        if self.POT_group.due_cycles:
            if self.done_cycles:
                if self.POT_group.cyclic:
                    next = self.done_cycles + self.POT_group.due_cycles
                else:
                    next = None
            else:
                if self.POT_group.part.current_assignment():
                    next = self.POT_group.due_cycles - self.POT_group.part.cycles_count + self.POT_group.part.current_assignment().aircraft.cycles_count
                else:
                    next = None
        else:
            next = None
        return next

    def left_cycles(self):
        if self.next_cycles() and self.POT_group.part.current_assignment():
            left = self.next_cycles() - self.POT_group.part.current_assignment().aircraft.cycles_count
        else:
            left = None
        return left

    def next_date(self):

        # Funkcja dodająca do daty okresloną liczbę miesięcy #
        def add_months(start_date, delta):
            if start_date:
                year = start_date.year + delta//12
                month = start_date.month + delta%12
                if month > 12:
                    month -= 12
                    year += 1
                day = start_date.day
                try:
                    end_date = date(year, month, day)
                except ValueError:
                    end_date = date(year, month+1, 1) - timedelta(days=1)
            else:
                end_date = None
            return end_date

        if self.POT_group.due_months:
            if self.POT_group.count_type == 'production':
                base_date = self.POT_group.part.production_date
            else:
                base_date = self.POT_group.part.install_date

            if self.POT_group.cyclic:
                if self.done_date:
                    next = add_months(self.done_date, self.POT_group.due_months)
                else:
                    next = add_months(base_date, self.POT_group.due_months)
            else:
                if self.done_date:
                    next = None
                else:
                    next = add_months(base_date, self.POT_group.due_months)
        else:
            next = None
        return next

    def left_days(self):
        if self.next_date():
            left = (self.next_date() - date.today()).days
        else:
            left = None
        return left

    def __str__(self):
        return '%s - %s' % (self.POT_ref, self.name)


class Work_order(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    number = models.CharField(max_length=25)
    date = models.DateField()
    aso = models.CharField(max_length=100)
    open = models.BooleanField(default=True)

    objects = FastManager()

    def __str__(self):
        return self.number


class Work_order_line(models.Model):
    work_order = models.ForeignKey(Work_order, on_delete=models.CASCADE)
    pot_group = models.ForeignKey(POT_group, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    done_date = models.DateField(blank=True, null=True)
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    done_landings = models.IntegerField(blank=True, null=True)
    done_cycles = models.IntegerField(blank=True, null=True)
    done_crs = models.CharField(max_length=20, blank=True, null=True)

    objects = FastManager()

    def __str__(self):
        return str(self.pk)


class Modification(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, verbose_name='Opis')
    done_date = models.DateField(verbose_name='Data wykonania')
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='TTH wykonania')
    done_landings = models.IntegerField(blank=True, null=True, verbose_name='Lądowania wykonania')
    done_cycles = models.IntegerField(blank=True, null=True, verbose_name='Cykle wykonania')
    aso = models.CharField(max_length=100, verbose_name='Organizacja')
    done_crs = models.CharField(max_length=20, verbose_name='Numer CRS')
    remarks = models.CharField(max_length=500, blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def __str__(self):
        return self.description


class WB_report(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, verbose_name='Opis')
    doc_ref = models.CharField(max_length=20, blank=True, null=True, verbose_name='Numer dokumentu')
    unit = models.CharField(max_length=3, default='EU', choices=[('EU', 'EU'), ('USA', 'USA')], verbose_name='Jednostki')
    mass_change = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Zmiana masy')
    empty_weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Masa pustego')
    lon_cg = models.DecimalField(max_digits=9, decimal_places=3, blank=True, null=True, verbose_name='Longitudal C.G.')
    lat_cg = models.DecimalField(max_digits=9, decimal_places=3, blank=True, null=True, verbose_name='Lateral C.G.')
    done_date = models.DateField(verbose_name='Data wykonania')
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='TTH wykonania')
    done_landings = models.IntegerField(blank=True, null=True, verbose_name='Lądowania wykonania')
    done_cycles = models.IntegerField(blank=True, null=True, verbose_name='Cykle wykonania')
    aso = models.CharField(max_length=100, verbose_name='Organizacja')
    done_doc = models.CharField(max_length=20, blank=True, null=True, verbose_name='Numer CRS')
    remarks = models.CharField(max_length=500, blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def __str__(self):
        return self.description


class MS_report(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    ms_ref = models.CharField(max_length=20, verbose_name='Numer MS')
    fuselage = models.CharField(max_length=30, verbose_name='Numer płatowca')
    engine1 = models.CharField(max_length=30, verbose_name='Numer silnika L')
    engine2 = models.CharField(max_length=30, blank=True, null=True, verbose_name='Numer silnika R')
    done_date = models.DateField(verbose_name='Data MS')
    done_hours = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Liczba godzin')
    done_landings = models.IntegerField(default=0, verbose_name='Liczba lądowań')
    done_cycles = models.IntegerField(default=0, verbose_name='Liczba cykli')
    crs_ref = models.CharField(max_length=20, blank=True, null=True, verbose_name='Numer CRS')
    crs_date = models.CharField(max_length=21, blank=True, null=True, verbose_name='Data CRS')
    next_date = models.DateField(verbose_name='Ważne do daty')
    next_hours = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Ważne do nalotu')
    next_landings = models.IntegerField(blank=True, null=True, verbose_name='Ważne do liczby lądowań')
    next_cycles = models.IntegerField(blank=True, null=True, verbose_name='Ważne do liczby cykli')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def save(self, *args, **kwargs):
        res = super(MS_report, self).save(*args, **kwargs)
        ms = self.aircraft.ms_report_set.order_by('done_date', 'ms_ref').last()
        self.aircraft.ms_hours = ms.next_hours
        self.aircraft.ms_date = ms.next_date
        self.aircraft.ms_landings = ms.next_landings
        self.aircraft.ms_cycles = ms.next_cycles

        self.aircraft.full_clean()
        self.aircraft.save()
        return res

    def delete(self, *args, **kwargs):
        res = super(MS_report, self).delete(*args, **kwargs)
        ms = self.aircraft.ms_report_set.order_by('done_date', 'ms_ref').last()
        if ms:
            self.aircraft.ms_hours = ms.next_hours
            self.aircraft.ms_date = ms.next_date
            self.aircraft.ms_landings = ms.next_landings
            self.aircraft.ms_cycles = ms.next_cycles
        else:
            self.aircraft.ms_hours = None
            self.aircraft.ms_date = None
            self.aircraft.ms_landings = None
            self.aircraft.ms_cycles = None

        self.aircraft.full_clean()
        self.aircraft.save()
        return res

    def __str__(self):
        return '%s / %s' % (self.aircraft, self.ms_ref)


class CAMO_operation(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    pdt = models.OneToOneField('panel.PDT', blank=True, null=True, verbose_name='Powiązany PDT', on_delete=models.CASCADE)
    pdt_ref = models.CharField(max_length=20, blank=True, null=True, verbose_name='Numer PDT')
    date = models.DateField(verbose_name='Data operacji')
    tth_start = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Licznik początkowy')
    tth_end = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Licznik końcowy')
    landings = models.IntegerField(default=0, verbose_name='Liczba lądowań')
    cycles = models.IntegerField(default=0, verbose_name='Liczba cykli')
    remarks = models.CharField(max_length=350, blank=True, null=True, verbose_name='Uwagi')

    objects = FastManager()

    def __str__(self):
        return '%s/%s' % (self.aircraft, self.tth_end)

    def tth(self):
        return self.tth_end - self.tth_start

    def save(self, *args, **kwargs):
        # sprawdź czy nowa operacja czy zmiana istniejącej #
        try:
            existing = CAMO_operation.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj liczniki dla AC #
        aircraft = self.aircraft

        if existing:
            aircraft.hours_count -= existing.tth()
            aircraft.landings_count -= existing.landings
            aircraft.cycles_count -= existing.cycles
            tth_max = CAMO_operation.objects.filter(aircraft=aircraft).exclude(pk=self.pk).aggregate(Max('tth_end'))['tth_end__max']
        else:
            tth_max = aircraft.tth
        aircraft.hours_count += self.tth()
        aircraft.landings_count += self.landings
        aircraft.cycles_count += self.cycles
        aircraft.tth = max(tth_max or 0, self.tth_end or 0)
        aircraft.full_clean()
        aircraft.save()

        # zaktualizuj liczniki dla przypisanych części #
        for part in aircraft.components():
            if part:
                if existing:
                    part.hours_count -= existing.tth()
                    part.landings_count -= existing.landings
                    part.cycles_count -= existing.cycles
                part.hours_count += self.tth()
                part.landings_count += self.landings
                part.cycles_count += self.cycles
                part.full_clean()
                part.save()

        return super(CAMO_operation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zmniejsz liczniki dla AC #
        self.aircraft.hours_count -= self.tth()
        self.aircraft.landings_count -= self.landings
        self.aircraft.cycles_count -= self.cycles
        self.aircraft.tth = CAMO_operation.objects.filter(aircraft=self.aircraft).exclude(pk=self.pk).aggregate(Max('tth_end'))['tth_end__max'] or 0
        self.aircraft.full_clean()
        self.aircraft.save()
        # zmniejsz liczniki dla przypisanych części #
        for part in self.aircraft.components():
            if part:
                part.hours_count -= self.tth()
                part.landings_count -= self.landings
                part.cycles_count -= self.cycles
                part.full_clean()
                part.save()
        return super(CAMO_operation, self).delete(*args, **kwargs)


class ASO(models.Model):
    name = models.CharField(max_length=100)
    certificate = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = 'Organizacje ASO'

    def __str__(self):
        return ' '.join([self.name, self.certificate])
