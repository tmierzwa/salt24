import datetime
from django.db import models
from camo.models import Aircraft
from panel.models import FBOUser, PDT


class Module(models.Model):

    class Meta:
        permissions = [('sms_reader', 'SMS - Dostęp do odczytu'),
                       ('sms_ncr', 'SMS - Dostęp do NCR'),
                       ('sms_admin', 'SMS - Dostęp pełny')]

    module = models.BooleanField()


class SMSHazard(models.Model):
    hazard_type	= models.CharField(max_length=10, choices=[('Zewnętrzne', 'Zewnętrzne'),
                                                           ('Osobowe', 'Osobowe'),
                                                           ('Operacyjne','Operacyjne'),
                                                           ('Techniczne', 'Techniczne'),
                                                           ('AS 350', 'AS 350'),
                                                           ('Inne','Inne')], verbose_name='Klasa zagrożenia')
    hazard_ref = models.CharField(max_length=10, verbose_name='Identyfikator zagrożenia')
    hazard_active = models.BooleanField(default=True, verbose_name="Aktywne")
    hazard_date = models.DateField(verbose_name='Data wprowadzenia')

    def __str__(self):
        return self.hazard_ref


class SMSHazardRev(models.Model):
    hazard = models.ForeignKey(SMSHazard, verbose_name='Zarejestrowane zagrożenie')
    rev_num = models.IntegerField(default=1, verbose_name='Numer wersji')
    rev_date = models.DateField(verbose_name='Data wersji')
    rev_last = models.BooleanField(default=True, verbose_name='Aktualna wersja')
    company_area = models.CharField(max_length=10, choices=[('SALT', 'SALT'),
                                                            ('ATO', 'ATO'),
                                                            ('AOC','AOC'),
                                                            ('SPO', 'SPO'),
                                                            ('Inne','Inne')], verbose_name='Obszar firmy')
    name = models.TextField(verbose_name='Nazwa zagrożenia')
    due_date = models.CharField(max_length=30, blank=True, null=True, verbose_name='Termin wykonania')
    responsible = models.CharField(max_length=50, blank=True, null=True, verbose_name='Osoba odpowiedzialna')
    control = models.TextField(blank=True, null=True, verbose_name='Wykonanie / kontrola')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return '%s rev. %d' % (self.hazard.hazard_ref, self.rev_num)


class SMSRisk(models.Model):
    risk_ref = models.CharField(max_length=10, verbose_name='Identyfikator ryzyka')
    rev_num = models.IntegerField(default=1, verbose_name='Numer wersji')
    rev_date = models.DateField(verbose_name='Data wersji')
    rev_last = models.BooleanField(default=True, verbose_name='Aktualna wersja')
    smshazard = models.ForeignKey(SMSHazard, verbose_name='Zarejestrowane zagrożenie')
    description = models.TextField(verbose_name='Szczegółowy opis natury ryzyka')
    init_probability = models.CharField(max_length=1, choices=[('5', '5 - Bardzo wysokie'),
                                                               ('4', '4 - Wysokie'),
                                                               ('3', '3 - Średnie'),
                                                               ('2', '2 - Niskie'),
                                                               ('1', '1 - Bardzo niskie')], verbose_name='Początkowe prawdopodobieństwo')
    init_impact	= models.CharField(max_length=1, choices=[('E', 'E - Bardzo duża'),
                                                          ('D', 'D - Duża'),
                                                          ('C', 'C - Średnia'),
                                                          ('B', 'B - Mała'),
                                                          ('A', 'A - Bardzo mała')], verbose_name='Początkowa dotkliwość')
    mitigation = models.TextField(blank=True, null=True, verbose_name='Sposoby ograniczania ryzyka')
    res_probability	= models.CharField(max_length=1, blank=True, null=True,
                                                     choices=[('5', '5 - Bardzo wysokie'),
                                                              ('4', '4 - Wysokie'),
                                                              ('3', '3 - Średnie'),
                                                              ('2', '2 - Niskie'),
                                                              ('1', '1 - Bardzo niskie')], verbose_name='Szczątkowe prawdopodobieństwo')
    res_impact = models.CharField(max_length=1, blank=True, null=True,
                                                choices=[('E', 'E - Bardzo duża'),
                                                         ('D', 'D - Duża'),
                                                         ('C', 'C - Średnia'),
                                                         ('B', 'B - Mała'),
                                                         ('A', 'A - Bardzo mała')], verbose_name='Szczątkowa dotkliwość')

    def prob_str(self):
        probs = {'5':'5 - Bardzo wysokie', '4': '4 - Wysokie', '3': '3 - Średnie',
                 '2':'2 - Niskie', '1': '1 - Bardzo niskie'}
        if self.init_probability:
            init_str = probs[self.init_probability]
        else:
            init_str = None
        if self.res_probability:
            res_str = probs[self.res_probability]
        else:
            res_str = None
        return (init_str, res_str)

    def impact_str(self):
        impacts = {'E': 'E - Bardzo duża', 'D': 'D - Duża', 'C': 'C - Średnia',
                   'B': 'B - Mała', 'A': 'A - Bardzo mała'}
        if self.init_impact:
            init_str = impacts[self.init_impact]
        else:
            init_str = None
        if self.res_impact:
            res_str = impacts[self.res_impact]
        else:
            res_str = None
        return (init_str, res_str)

    def risk_color(self):
        colors = {'4A': 'lightgreen', '3A': 'lightgreen', '2A': 'lightgreen', '1A': 'lightgreen',
                  '3B': 'lightgreen', '2B': 'lightgreen', '1B': 'lightgreen',
                  '2C': 'lightgreen', '1C': 'lightgreen', '1D': 'lightgreen', '1E': 'lightgreen',
                  '5A': 'yellow', '5B': 'yellow', '4B': 'yellow', '4C': 'yellow',
                  '3C': 'yellow', '3D': 'yellow', '2D': 'yellow', '2E': 'yellow',
                  '5C': 'coral', '5D': 'coral', '5E': 'coral',
                  '4D': 'coral', '4E': 'coral', '3E': 'coral' }
        if self.init_probability and self.init_impact:
            init_color = colors['%s%s' % (self.init_probability, self.init_impact)]
        else:
            init_color = None
        if self.res_probability and self.res_impact:
            res_color = colors['%s%s' % (self.res_probability, self.res_impact)]
        else:
            res_color = None
        return (init_color, res_color)

    def __str__(self):
        return self.risk_ref


class SMSEvent(models.Model):
    aircraft = models.CharField(max_length=10, verbose_name='Statek powietrzny')
    pic = models.CharField(max_length=40, verbose_name='Pilot dowódca')
    event_date = models.DateField(verbose_name='Data zdarzenia')
    oper_type = models.CharField(max_length=10, choices=[('AOC', 'AOC'),
                                                         ('ATO', 'ATO'),
                                                         ('Wynajem','Wynajem'),
                                                         ('Prywatny', 'Prywatny'),
                                                         ('Inne','Inne')], verbose_name='Rodzaj operacji')
    event_type = models.CharField(max_length=20, choices=[('Zdarzenie', 'Zdarzenie'),
                                                          ('Incydent', 'Incydent'),
                                                          ('Poważny incydent', 'Powazny Incydent'),
                                                          ('Wypadek', 'Wypadek')], verbose_name='Kwalifikacja zdarzenia')
    pkbwl_ref = models.CharField(max_length=10, blank=True, null=True, verbose_name='Numer ewidencyjny PKBWL')
    pkbwl_date = models.DateField(blank=True, null=True, verbose_name='Data przyjęcia w PKBWL')
    examiner = models.CharField(max_length=50, blank=True, null=True, verbose_name='Badający zdarzenie')
    description = models.TextField(verbose_name='Opis zdarzenia')
    scrutiny = models.TextField(blank=True, null=True, verbose_name='Przebieg badania wewnętrznego')
    smshazard = models.ForeignKey(SMSHazard, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zagrożenie w rejestrze')
    findings = models.TextField(blank=True, null=True, verbose_name='Wnioski i zalecenia po badaniu wewnętrznym')
    closure	= models.CharField(max_length=30, blank=True, null=True, verbose_name='Zamknięcie badania / raport końcowy')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    reported_by = models.ForeignKey('panel.FBOUser', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zgłaszający użytkownik')

    def __str__(self):
        return 'Zdarzenie %s / %s' % (self.aircraft, str(self.event_date))


class SMSFailure(models.Model):
    aircraft = models.CharField(max_length=10, verbose_name='Statek powietrzny')
    person = models.CharField(max_length=30, blank=True, null=True, verbose_name='Osoba zgłaszająca')
    failure_date = models.DateField(verbose_name='Data zgłoszenia')
    description = models.TextField(verbose_name='Opis usterki')
    pdt_ref = models.ForeignKey(PDT, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Numer PDT')
    repair_date	= models.DateField(blank=True, null=True, verbose_name='Data usunięcia usterki')
    repair_desc	= models.CharField(blank=True, null=True, max_length=500, verbose_name='Sposób usunięcia usterki')
    crs = models.CharField(max_length=20, blank=True, null=True, verbose_name='Numer CRS')
    smshazard = models.ForeignKey(SMSHazard, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zagrożenie w rejestrze')
    findings = models.TextField(blank=True, null=True, verbose_name='Wnioski i zalecenia ogólne')

    def __str__(self):
        return 'Usterka %s/%s' % (self.aircraft, str(self.failure_date))


class SMSReport(models.Model):
    report_date = models.DateField(verbose_name='Data zgłoszenia')
    person = models.CharField(max_length=50, blank=True, null=True, verbose_name='Osoba zgłaszająca')
    privacy = models.BooleanField(default=False, verbose_name='Proszę o zachowanie poufnosci')
    description = models.TextField(verbose_name='Treść zgłoszenia')
    smshazard = models.ForeignKey(SMSHazard, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zagrożenie w rejestrze')
    findings = models.TextField(blank=True, null=True, verbose_name='Wnioski i zalecenia')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    reported_by = models.ForeignKey('panel.FBOUser', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zgłoszajacy użytkownik')

    def __str__(self):
        return 'Dobrowolny raport z dnia %s' % str(self.report_date)


class NCR(models.Model):
    audit_scope = models.CharField(max_length=10, choices=[('AOC', 'AOC'),
                                                           ('SPO', 'SPO'),
                                                           ('CAMO', 'CAMO'),
                                                           ('ATO', 'ATO')], verbose_name='Obszar audytu')
    audit_type = models.CharField(max_length=10, choices=[('Wewnętrzny', 'Wewnętrzny'),
                                                          ('Zewnętrzny', 'Zewnętrzny')], verbose_name='Rodzaj audytu')
    audit_nbr = models.CharField(max_length=30, verbose_name='Numer audytu')
    audit_date = models.DateField(verbose_name='Data audytu')
    ncr_nbr = models.IntegerField(verbose_name='Numer NCR')
    description = models.TextField(verbose_name='Treść NCR')
    due_date = models.DateField(verbose_name='Wyznaczona data usunięcia')
    ncr_user1 = models.ForeignKey(FBOUser, related_name='ncr_user1_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Osoba odpowiedzialna 1')
    ncr_user2 = models.ForeignKey(FBOUser, related_name='ncr_user2_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Osoba odpowiedzialna 2')
    done_date = models.DateField(blank=True, null=True, verbose_name='Data usunięcia')
    check_date = models.DateField(blank=True, null=True, verbose_name='Data audytu sprawdzającego')

    def left_days(self):
        if self.done_date:
            return None
        else:
            diff = self.due_date - datetime.date.today()
            return diff.days or 0

    def __str__(self):
        return 'NCR %s nr. %s z dnia %s' % (self.audit_nbr, self.ncr_nbr, str(self.audit_date))
