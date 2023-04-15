# -*- coding: utf-8 -*-

from datetime import date
import time

from django import forms
from django.forms import Textarea, TextInput, CharField, modelform_factory
from django.forms.widgets import HiddenInput
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from django.db.models import Q

from camo.models import Aircraft
from ato.models import Training, Instructor, Training_inst
from panel.models import PDT, Operation, Pilot, FlightTypes, PilotAircraft, PilotFlightType
from fin.models import FuelTank, Contractor, Voucher, LocalFueling


class PDTEditForm(forms.ModelForm):

    class Meta:
        model = PDT
        exclude = ['status', 'open_user', 'open_time', 'close_user', 'close_time', 'check_user', 'check_time',
                   'repair_desc', 'repair_time', 'repair_user']

    def __init__(self, *args, **kwargs):
        self.fbouser = kwargs.pop('fbouser')
        self.camo = kwargs.pop('camo', False)
        self.instance = kwargs.get('instance', None)
        super(PDTEditForm, self).__init__(*args, **kwargs)

        # Szczegółowa konfiguracja pól formularza

        # Dostepne SP i typy lotów
        if self.fbouser.user.is_staff:
            aircraft_auth = [aircraft for aircraft in Aircraft.objects.all()]
            types_auth = [flight_type_code for flight_type_code, flight_type_name in FlightTypes().items()]
        else:
            if hasattr(self.fbouser, 'pilot'):
                aircraft_auth = [relation.aircraft for relation in PilotAircraft.objects.filter(pilot=self.fbouser.pilot)]
                types_auth = [relation.flight_type for relation in PilotFlightType.objects.filter(pilot=self.fbouser.pilot)]
            else:
                aircraft_auth = [aircraft for aircraft in Aircraft.objects.all()]
                types_auth = ['06', '06A']

        # Jeśli jest to nowy PDT
        if not self.instance.pk:

            # Lista statków powietrznych ze statusami
            aircraft_list = []
            for aircraft in aircraft_auth:
                if not self.camo and not aircraft.status == 'flying':
                    status = 'Uszkodzony'
                    order = 3
                elif not self.camo and not aircraft.airworthy():
                    status = 'Przekroczony MS'
                    order = 2
                elif not len(aircraft.pdt_set.filter(status='open')) == 0:
                    last_pdt = aircraft.pdt_set.filter(status='open').last()
                    status = 'PDT - %s' % last_pdt.open_user
                    order = 1
                else:
                    if self.camo:
                        status = 'bez kontroli MS'
                    else:
                        status = '%.2f TTH' % ((aircraft.ms_hours or 99999) - aircraft.hours_count)
                    order = 0

                aircraft_list += [(aircraft, status, order)]

            # Sortowanie listy, tak aby dostępne były na początku
            aircraft_list.sort(key=lambda a: a[0].registration)
            aircraft_list.sort(key=lambda a: a[2])

            # Domyślny element pustego wyboru
            choices = [('', '---------')]

            # Listy wyborów dla dostępnych i niedostepnych SP
            available = list(
                (aircraft.pk, aircraft.registration + '  (%s)' % status) for (aircraft, status, order) in aircraft_list if
                order == 0)
            not_available = list(
                (aircraft.pk, aircraft.registration + '  (%s)' % status) for (aircraft, status, order) in aircraft_list if
                order != 0)

            # Ostateczne sklejenie listy SP
            if len(available) > 0:
                choices += [('Dostępne', available)]
            if len(not_available) > 0:
                choices += [('Niedostępne', not_available)]

            # Pole Statek powietrzny
            self.fields['aircraft'] = forms.ChoiceField(choices=choices, label='Statek pow.', required=True)
            self.fields['aircraft'].error_messages['required'] = 'Należy wybrać statek powietrzny!'

        else:

            # Pole Statek powietrzny ustawione i zablokowane dla edycji PDT
            choices = [(self.instance.aircraft.pk, self.instance.aircraft.registration)]
            self.fields['aircraft'] = forms.ChoiceField(choices=choices, label='Statek pow.', required=False)
            self.fields['aircraft'].disabled = True
            aircraft_list = [(self.instance.aircraft, '', 0)]

        # Pole Rodzaj lotu
        choices = [('', '---------')]
        for flight_type_code, flight_type_name in FlightTypes().items():
            if flight_type_code in types_auth:
                choices += [(flight_type_code, flight_type_name)]

        self.fields['flight_type'] = forms.ChoiceField(choices=choices, label='Rodzaj lotu', required=True)
        self.fields['flight_type'].error_messages['required'] = 'Należy wybrać rodzaj lotu!'

        # Numery PDT i MS (ukryte)
        for (aircraft, status, order) in aircraft_list:
            self.fields['_pdt_ref_%d' % aircraft.pk] = \
                forms.CharField(initial=aircraft.last_pdt_ref + 1, widget=forms.HiddenInput(), required=False)

            ms_report = aircraft.ms_report_set.order_by('done_date').last()
            if ms_report:
                ms_valid = "%s / %s" % (ms_report.next_hours, ms_report.next_date)
            else:
                ms_valid = "Brak MS!"
            self.fields['_ms_%d' % aircraft.pk] = \
                forms.CharField(initial=ms_valid, widget=forms.HiddenInput(), required=False)

        # Szkolenia tylko aktywne
        self.fields['training'].queryset = Training_inst.objects.select_related().filter(open=True).order_by('student')

        # Ustaw szkolenie na podstawie SIC lub PIC
        if not self.instance.pk and kwargs['initial']['flight_type'] in ['03A', '03B', '03C', '03E']:
            student = getattr(kwargs['initial']['sic'], 'student', None) or getattr(kwargs['initial']['pic'], 'student', None)
            if student:
                self.fields['training'].initial = student.training_inst_set.filter(open=True).first()

            # Ustawienie instruktora na podstawie PIC
            if kwargs['initial']['sic']:
                instructor = getattr(kwargs['initial']['pic'], 'instructor', None)
                if instructor:
                    self.fields['instructor'].initial = instructor.pilot

        # Vouchery tylko opłacone i nie wykorzystane
        self.fields['voucher'].queryset = Voucher.objects.filter(done_date__isnull=True, paid=True)

        # Pozostałe pola formularza

        self.fields['instructor'].label = 'Instruktor'
        self.fields['remarks'].widget = TextInput()
        self.fields['service_remarks'].widget = TextInput()
        self.fields['failure_desc'].widget = TextInput()

        self.fields['ms'] = forms.CharField(label='MS ważny do')
        self.fields['ms'].disabled = True
        self.fields['ms'].required = False

        self.fields['fuel_after'].initial = 0

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in FuelTank.objects.all()]
        fuel_tanks += [("other", "-- Poza SALT --")]
        self.fields['fuel_after_source'] = forms.ChoiceField(choices=fuel_tanks, label='Źródło paliwa', required=True)

        self.fields['tth_start'].required = False
        self.fields['next_pdt'].required = False

        self.fields['date'].required = True
        self.fields['pdt_ref'].required = True
        self.fields['pic'].required = True


    def clean_aircraft(self):

        # Przekształca numer SP na kompletny obiekt
        aircraft_id = self.cleaned_data['aircraft']
        try:
            aircraft = Aircraft.objects.get(pk=aircraft_id)
        except:
            aircraft = None
        return aircraft


    def clean(self):

        cleaned_data = super(PDTEditForm, self).clean()

        # Jeśli jest to nowy PDT
        if not self.instance.pk:
            if cleaned_data.get('aircraft'):
                aircraft = cleaned_data.get('aircraft')
                # Sprawdzenie czy nie ma otwartego wcześniej PDTa
                open_pdt = aircraft.pdt_set.filter(status='open').last()
                if open_pdt:
                    raise forms.ValidationError("Należy najpierw zamknąć PDT dla tego SP!")

                # Sprawdzenie czy nie wybrano niedostępnego SP
                # Wyjątkiem jest oblot techniczny - rodzaj lotu 06, 06A
                # Sprawdzenie nie wystepuje równiez przy wprowadzaniu przez CAMO
                elif (not self.camo) and (aircraft.status != 'flying' or not aircraft.airworthy()) and \
                     (not cleaned_data.get('flight_type') in ['06', '06A']):
                    raise forms.ValidationError("Wybrany statek powietrzny jest niedostępny!")
            else:
                # Z jakiegoś powodu nie wybrano SP
                raise forms.ValidationError("Należy wybrać statek powietrzny!")

        return cleaned_data


class OperationEditForm(forms.ModelForm):

    class Meta:
        model = Operation
        fields = ['operation_no', 'fuel_refill', 'fuel_source', 'fuel_available',
                  'oil_refill', 'loc_start', 'loc_end', 'tth_start', 'tth_end',
                  'time_start', 'time_end', 'fuel_used', 'landings', 'cycles', 'status']
        localized_fields = ['tth_start', 'tth_end']

    def __init__(self, *args, **kwargs):
        self.pdt = kwargs.pop('pdt')
        self.user = kwargs.pop('user')
        self.do_pfi = kwargs.pop('pfi')
        super(OperationEditForm, self).__init__(*args, **kwargs)

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in FuelTank.objects.filter(fuel_type=self.pdt.aircraft.fuel_type)]
        fuel_tanks+= [("other", "-- Poza SALT --")]
        self.fields['fuel_source'].widget = forms.Select(choices=fuel_tanks)

        self.fields['loc_start'].required = False
        self.fields['time_start'].required = False
        self.fields['loc_end'].required = False
        self.fields['time_end'].required = False
        self.fields['fuel_used'].required = False
        self.fields['landings'].required = False
        self.fields['cycles'].required = False
        self.fields['status'].required = False

        self.fields['operation_no'].widget = TextInput()
        self.fields['operation_no'].disabled = True
        self.fields['time_start'].widget = forms.TimeInput(format="%H:%M")
        self.fields['time_end'].widget = forms.TimeInput(format="%H:%M")
        self.fields['tth_start'] = forms.DecimalField(decimal_places=2, label='Licznik początkowy')
        self.fields['tth_start'].required = False
        self.fields['tth_end'] = forms.DecimalField(decimal_places=2, label='Licznik końcowy')
        self.fields['tth_end'].required = False

        self.fields['pfi'] = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Potwierdzenie PFI')
        self.fields['pfi'].required = False

    def clean_fuel_refill(self):
        cleaned_data = super(OperationEditForm, self).clean()
        if (cleaned_data['fuel_refill'] < 0) or (cleaned_data['fuel_refill'] > self.pdt.aircraft.fuel_capacity):
            raise ValidationError('Niepoprawna ilość uzupełnionego paliwa!')
        return cleaned_data['fuel_refill']

    def clean_fuel_available(self):
        cleaned_data = super(OperationEditForm, self).clean()
        if (int(cleaned_data['fuel_available']) > self.pdt.aircraft.fuel_capacity) or (int(cleaned_data['fuel_available']) == 0):
            raise ValidationError('Niepoprawna ilość paliwa do lotu!')
        return cleaned_data['fuel_available']

    def clean_pfi(self):
        cleaned_data = super(OperationEditForm, self).clean()
        if self.do_pfi:
            if not (cleaned_data['pfi']):
                raise ValidationError('Potwierdź PFI podając hasło PIC!')
            if not self.pdt.pic.fbouser.user.check_password(cleaned_data['pfi']):
                if not (hasattr(self.user.fbouser.pilot, 'instructor') and self.user.check_password(cleaned_data['pfi'])):
                    if not (self.user.is_staff and self.user.check_password(cleaned_data['pfi'])):
                        raise ValidationError('Niepoprawne hasło PIC!')
        return cleaned_data['pfi']

    def clean(self):
        cleaned_data = super(OperationEditForm, self).clean()

        if cleaned_data.get('tth_end', None) and cleaned_data.get('tth_start', None):
            if (cleaned_data.get('tth_end', 0) < cleaned_data.get('tth_start', 0)) or \
               (cleaned_data.get('tth_end', 0) - cleaned_data.get('tth_start', 0) > 6):
                raise ValidationError('Niepoprawny licznik końcowy!')

        if int(cleaned_data.get('fuel_used') or 0) > self.pdt.aircraft.fuel_capacity:
            raise ValidationError('Niepoprawna ilość zużytego paliwa!')

        if all(cleaned_data.get(field) for field in ('time_start', 'time_end', 'tth_start', 'tth_end')):
            start = cleaned_data.get('time_start').hour*60 + cleaned_data.get('time_start').minute
            end = cleaned_data.get('time_end').hour*60 + cleaned_data.get('time_end').minute
            if start > end:
                end += 60*24
            time_diff = end - start
            tth_diff = (cleaned_data.get('tth_end') - cleaned_data.get('tth_start')) * 60
            if not self.pdt.aircraft.helicopter:
                if max(time_diff, tth_diff) != 0:
                    if max(time_diff, tth_diff) - min(time_diff, tth_diff) > 60:
                        raise ValidationError('Czas niezgodny z licznikiem!')

        if all(cleaned_data.get(field) for field in ('time_start', 'time_end')):
            overlap = None
            for oper in Operation.objects.filter(pdt__aircraft=self.pdt.aircraft, pdt__date=self.pdt.date).\
                                          exclude(time_start__gt=cleaned_data.get('time_end')).\
                                          exclude(time_end__lt=cleaned_data.get('time_start')):
                if (not self.instance.pk) or (self.instance.pk and oper.pk != self.instance.pk):
                    if oper.time_start and oper.time_end:
                        if (oper.time_start >= cleaned_data['time_start'] and oper.time_start < cleaned_data['time_end']) or \
                           (oper.time_end > cleaned_data['time_start'] and oper.time_end <= cleaned_data['time_end']) or \
                           (cleaned_data['time_start'] >= oper.time_start and cleaned_data['time_end'] <= oper.time_end):
                            overlap = oper
                            break
            if overlap:
                raise forms.ValidationError("Godziny kolidują z inną operacją na tym SP! (PDT nr. %06d)" % overlap.pdt.pdt_ref)

        if all(cleaned_data.get(field) for field in ('time_start', 'time_end')):
            overlap = None
            for oper in Operation.objects.filter(Q(pdt__pic=self.pdt.pic)|Q(pdt__sic=self.pdt.pic)).\
                                          filter(pdt__date=self.pdt.date).\
                                          exclude(time_start__gt=cleaned_data.get('time_end')).\
                                          exclude(time_end__lt=cleaned_data.get('time_start')):
                if (not self.instance.pk) or (self.instance.pk and oper.pk != self.instance.pk):
                    if (oper.time_start >= cleaned_data['time_start'] and oper.time_start < cleaned_data['time_end']) or \
                       (oper.time_end > cleaned_data['time_start'] and oper.time_end <= cleaned_data['time_end']) or \
                       (cleaned_data['time_start'] >= oper.time_start and cleaned_data['time_end'] <= oper.time_end):
                        overlap = oper
                        break
            if overlap:
                raise forms.ValidationError("Godziny kolidują z inną operacją dla PIC! (%s PDT nr. %06d)" % (overlap.pdt.aircraft.registration, overlap.pdt.pdt_ref))

        if all(cleaned_data.get(field) for field in ('time_start', 'time_end')) and self.pdt.sic:
            overlap = None
            for oper in Operation.objects.filter(Q(pdt__pic=self.pdt.sic)|Q(pdt__sic=self.pdt.sic)).\
                                          filter(pdt__date=self.pdt.date).\
                                          exclude(time_start__gt=cleaned_data.get('time_end')).\
                                          exclude(time_end__lt=cleaned_data.get('time_start')):
                if (not self.instance.pk) or (self.instance.pk and oper.pk != self.instance.pk):
                    if (oper.time_start >= cleaned_data['time_start'] and oper.time_start < cleaned_data['time_end']) or \
                       (oper.time_end > cleaned_data['time_start'] and oper.time_end <= cleaned_data['time_end']) or \
                       (cleaned_data['time_start'] >= oper.time_start and cleaned_data['time_end'] <= oper.time_end):
                        overlap = oper
                        break
            if overlap:
                raise forms.ValidationError("Godziny kolidują z inną operacją dla SIC! (%s PDT nr. %06d)" % (overlap.pdt.aircraft.registration, overlap.pdt.pdt_ref))


        return cleaned_data


class CheckOutFormOpen(forms.Form):

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        self.pilot = kwargs.pop('pilot')
        super(CheckOutFormOpen, self).__init__(*args, **kwargs)

        aircraft_auth = [relation.aircraft for relation in PilotAircraft.objects.filter(pilot=self.pilot)]
        types_auth = [relation.flight_type for relation in PilotFlightType.objects.filter(pilot=self.pilot)]

        # Data PDT
        self.fields['pdt_date'] = forms.DateField(label='Data PDT')

        self.fields['pdt_date'].required = False

        # Lista statków powietrznych ze statusami
        aircraft_list = []
        for aircraft in aircraft_auth:
            if not aircraft.status == 'flying':
                status = 'Uszkodzony'
                order = 3
            elif not aircraft.airworthy():
                status = 'Przekroczony MS'
                order = 2
            elif not len(aircraft.pdt_set.filter(status='open')) == 0:
                last_pdt = aircraft.pdt_set.filter(status='open').last()
                status = 'PDT - %s' % last_pdt.open_user
                order = 1
            else:
                status = '%.2f TTH' % ((aircraft.ms_hours or 99999) - aircraft.hours_count)
                order = 0

            aircraft_list += [(aircraft, status, order)]

        # Sortowanie listy, tak aby dostępne były na początku

        aircraft_list.sort(key=lambda a: a[2])

        # Domyślny element pustego wyboru
        choices = [('', ('Wybierz SP ...'))]

        # Listy wyborów dla dostępnych i niedostepnych SP
        available = list((aircraft.pk, aircraft.registration + '  (%s)' % status) for (aircraft, status, order) in aircraft_list if order == 0)
        not_available = list((aircraft.pk, aircraft.registration + '  (%s)' % status) for (aircraft, status, order) in aircraft_list if order != 0)

        # Ostateczne sklejenie listy SP
        if len(available) > 0:
            choices += [('Dostępne', available)]
        if len(not_available) > 0:
            choices += [('Niedostępne', not_available)]

        self.fields['aircraft'] = forms.ChoiceField(choices=choices, label='Statek powietrzny')
        self.fields['aircraft'].error_messages['required'] = 'Należy wybrać statek powietrzny!'

        self.fields['aircraft'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

        # Numer PDT
        for (aircraft, status, order) in aircraft_list:
            self.fields['pdt_ref%d' % aircraft.pk] = CharField(initial=aircraft.last_pdt_ref+1, widget=HiddenInput(), required=False)

        self.fields['pdt_ref'] = forms.IntegerField(label='Numer PDT')
        self.fields['pdt_ref'].error_messages['required'] = 'Należy podać numer PDT!'

        self.fields['pdt_ref'].widget.attrs={'placeholder': 'Wybierz SP ...'}

        # Rodzaj lotu
        choices = [('', ('Wybierz rodzaj lotu ...'))]
        for flight_type_code, flight_type_name in FlightTypes().items():
            if flight_type_code in types_auth:
                choices +=[(flight_type_code, flight_type_name)]

        self.fields['flight_type'] = forms.ChoiceField(choices=choices, label='Rodzaj lotu')
        self.fields['flight_type'].error_messages['required'] = 'Należy wybrać rodzaj lotu!'

        self.fields['flight_type'].widget.attrs = {'data-native-menu': 'false'}

        self.fields['remarks'] = forms.CharField(max_length=400, required=False, widget=Textarea(attrs={'placeholder': 'Informacje dodatkowe ...'}),
                                                 label='Informacje dodatkowe')

    def clean(self):
        cleaned_data = super(CheckOutFormOpen, self).clean()

        # Sprawdzenie czy nie wybrano niedostępnego SP
        # Wyjątkiem jest oblot techniczny - rodzaj lotu 06
        if cleaned_data.get('aircraft'):
            aircraft = Aircraft.objects.get(pk=cleaned_data.get('aircraft'))
            if len(aircraft.pdt_set.filter(status='open')) > 0:
                raise forms.ValidationError("Należy zamknąć PDT dla tego SP!")
            elif (aircraft.status != 'flying' or not aircraft.airworthy()) and (not cleaned_data.get('flight_type') in ['06', '06A']):
                raise forms.ValidationError("Ten SP jest niedostępny!")

        if (cleaned_data.get('aircraft') == None) or (cleaned_data.get('flight_type') == None):
            raise forms.ValidationError("Wybierz SP i rodzaj lotu!")
        if cleaned_data.get('pdt_ref') == None:
            raise forms.ValidationError("Podaj numer PDT!")

        return cleaned_data


class CheckOutFormServices(forms.Form):

    def __init__(self, *args, **kwargs):
        flight_type = kwargs.pop('flight_type')
        self.is_mobile = kwargs.pop('is_mobile')
        super(CheckOutFormServices, self).__init__(*args, **kwargs)

        # lista zarejestrowanych kontrahentów
        choices = [('', 'Wybierz kontrahenta ...')]
        choices+= [(contractor.pk, '%s - %s' % (contractor.contractor_id, contractor.name))
                    for contractor in Contractor.objects.filter(company=True, active=True)]

        if len(choices) > 0:
            self.fields['contractors'] = forms.ChoiceField(choices=choices, label='Kontrahent')
            self.fields['contractors'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

        # Dodatkowy opis do usługi
        self.fields['service_remarks'] = forms.CharField(max_length=400, required=False,
                                                         widget=Textarea(attrs={'rows':4, 'placeholder': 'Opis usługi ...'}),
                                                         label='Opis usługi')
    def clean(self):
        cleaned_data = super(CheckOutFormServices, self).clean()
        if cleaned_data.get('contractors') == None:
            raise forms.ValidationError("Wybierz kontrahenta!")

        return cleaned_data


class CheckOutFormTrainings(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.is_mobile = kwargs.pop('is_mobile')
        super(CheckOutFormTrainings, self).__init__(*args, **kwargs)

        student, instructor = None, None
        if hasattr(self.user, 'pilot'):
            pilot = self.user.pilot
            if hasattr(pilot, 'student'):
                student = pilot.student
            if hasattr(pilot, 'instructor'):
                instructor = pilot.instructor

        # lista szkoleń
        trainings = list(Training_inst.objects.filter(open=True, student=student))
        trainings += list(Training_inst.objects.filter(open=True, instructor=instructor).exclude(student=student))
        trainings += list(Training_inst.objects.filter(open=True).exclude(student=student).exclude(instructor=instructor))

        choices = [('', 'Wybierz szkolenie ...')]
        choices += [(training.pk, '%s - %s' % (training.student, training.training.code))
                    for training in trainings]

        if len(choices) > 0:
            self.fields['trainings'] = forms.ChoiceField(choices=choices, label='Szkolenie')
            self.fields['trainings'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

    def clean(self):
        cleaned_data = super(CheckOutFormTrainings, self).clean()
        if cleaned_data.get('trainings') == None:
            raise forms.ValidationError("Wybierz szkolenie!")

        return cleaned_data


class CheckOutFormVouchers(forms.Form):

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        super(CheckOutFormVouchers, self).__init__(*args, **kwargs)

        # lista voucherów własnych
        choices = [('', 'Wybierz voucher SALT ...')]
        choices+= [(voucher.pk, '%s - %s' % (voucher.voucher_id, voucher.description))
                    for voucher in Voucher.objects.filter(done_date__isnull=True, paid=True)]

        if len(choices) > 0:
            self.fields['vouchers'] = forms.ChoiceField(choices=choices, required = False, label='Voucher')
            self.fields['vouchers'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

        # opis opis obcego vouchera
        self.fields['ext_voucher'] = forms.CharField(max_length=100, required=False, widget=TextInput(attrs={'placeholder': 'Voucher obcy ...'}),
                                                     label='Voucher obcy')


class CheckOutFormRent(forms.Form):

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        super(CheckOutFormRent, self).__init__(*args, **kwargs)

        # wybór opcjonalnego instruktora
        self.fields['instructor'] = forms.ChoiceField(required=False, label='Instruktor',
                                                      choices=[('', 'Wybierz instruktora ...')] + [(instructor.pk, instructor.pilot)
                                                                                                   for instructor in Instructor.objects.order_by('pilot__fbouser__second_name', 'pilot__fbouser__first_name')])
        self.fields['instructor'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}


class CheckOutFormCrew(forms.Form):

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        self.student = kwargs.pop('student')
        super(CheckOutFormCrew, self).__init__(*args, **kwargs)

        self.fields['pic'] = forms.ChoiceField(label='Pilot dowódca')
        self.fields['sic'] = forms.ChoiceField(label='Drugi pilot')

        default_pic = [('', 'Wybierz PIC ...')]
        default_sic = [('', 'Wybierz SIC ...')]

        default_sic += [('', '----- Brak SIC -----')]

        # Jeśli na locie jest uczeń
        if self.student:
            # PIC może być uczniem albo instruktorem
            self.fields['pic'].choices = default_pic + [(self.student.pilot.pk, self.student.pilot)] + \
                                         [(instructor.pilot.pk, instructor.pilot) for instructor in Instructor.objects.order_by('pilot__fbouser__second_name', 'pilot__fbouser__first_name')
                                          if instructor.pilot.pk != self.student.pilot.pk]
            # SIC może być tylko uczniem
            self.fields['sic'].choices = default_sic + [(self.student.pilot.pk, self.student.pilot)]
        else:
            self.fields['pic'].choices = default_pic + [(pilot.pk, pilot) for pilot in Pilot.objects.order_by('fbouser__second_name', 'fbouser__first_name')]
            self.fields['sic'].choices = default_sic + [(pilot.pk, pilot) for pilot in Pilot.objects.order_by('fbouser__second_name', 'fbouser__first_name')]

        self.fields['sic'].required = False

        self.fields['pic'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}
        if self.student:
            self.fields['sic'].widget.attrs = {'data-native-menu': 'false'}
        else:
            self.fields['sic'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

    def clean(self):
        cleaned_data = super(CheckOutFormCrew, self).clean()
        if self.is_mobile and ('pic' not in cleaned_data):
            raise ValidationError('Brak pierwszego pilota!')
        if 'pic' in cleaned_data and 'sic' in cleaned_data:
            if cleaned_data['pic'] == cleaned_data['sic']:
                raise ValidationError('PIC i SIC muszą być różni!')
        if self.student:
            if not ((cleaned_data.get('pic') == str(self.student.pilot.pk)) or (cleaned_data.get('sic') == str(self.student.pilot.pk))):
                raise ValidationError('Brak ucznia w załodze!')
        return cleaned_data


class OperationOpenForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.pdt = kwargs.pop('pdt')
        self.is_mobile = kwargs.pop('is_mobile')
        self.user = kwargs.pop('user')
        super(OperationOpenForm, self).__init__(*args, **kwargs)

        fields = ['pax', 'bags', 'fuel_refill', 'fuel_source', 'fuel_available',
                  'oil_refill', 'trans_oil_refill', 'hydr_oil_refill', 'loc_start']

        localized_fields = ['oil_refill', 'trans_oil_refill', 'hydr_oil_refill']

        for name, field in modelform_factory(Operation, fields=fields, localized_fields=localized_fields).base_fields.items():
            self.fields[name] = field

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in FuelTank.objects.filter(fuel_type=self.pdt.aircraft.fuel_type)]
        fuel_tanks += [("other", "-- Poza SALT --")]
        self.fields['fuel_source'].widget = forms.Select(choices=fuel_tanks)
        self.fields['fuel_source'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select', 'data-mini': 'true'}

        self.fields['pfi'] = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Potwierdzenie PFI')
        self.fields['pfi'].widget.attrs = {'placeholder': 'Aby potwierdzić podaj hasło PIC ...'}
        self.fields['pfi'].error_messages['required'] = 'Potwierdź PFI podając hasło PIC!'


    def clean(self):
        cleaned_data = super(OperationOpenForm, self).clean()
        if self.pdt.flight_type in ['03A', '03B', '03C', '03D', '03E']:
            if (cleaned_data['fuel_available'] < self.pdt.aircraft.fuel_consumption / 2) or \
               (cleaned_data['fuel_available'] > self.pdt.aircraft.fuel_capacity):
                raise ValidationError('Niepoprawna wartość paliwa do lotu!')
        if (cleaned_data['fuel_refill'] < 0) or (cleaned_data['fuel_refill'] > self.pdt.aircraft.fuel_capacity):
            raise ValidationError('Niepoprawna wartość uzupełnionego paliwa!')
        if cleaned_data.get('fuel_available') in (0, '', None):
            raise ValidationError('Podaj stan paliwa do lotu!')
        if cleaned_data.get('loc_start') in ('', None):
            raise ValidationError('Podaj lotnisko startu!')
        if cleaned_data.get('pfi') == None:
            raise ValidationError('Podaj poprawne hasło PIC!')
        if not self.pdt.pic.fbouser.user.check_password(cleaned_data['pfi']):
            if not (hasattr(self.user.fbouser.pilot, 'instructor') and self.user.check_password(cleaned_data['pfi'])):
                raise ValidationError('Podaj poprawne hasło PIC!')

        return cleaned_data


class OperationCloseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.operation = kwargs.pop('operation')
        self.is_mobile = kwargs.pop('is_mobile')
        super(OperationCloseForm, self).__init__(*args, **kwargs)

        fields = ['loc_start', 'loc_end', 'tth_start', 'tth_end', 'time_start', 'time_end',
                  'fuel_used', 'landings', 'cycles']

        for name, field in modelform_factory(Operation, fields=fields, localized_fields=['tth_end']).base_fields.items():
            self.fields[name] = field
            self.fields[name].required = True

        self.fields['tth_start'].widget.attrs = {'readonly': True}

        if not self.operation.pdt.aircraft.use_cycles:
            self.fields['cycles'].required = False

    def clean(self):
        cleaned_data = super(OperationCloseForm, self).clean()

        if (cleaned_data.get('tth_end', 0) < cleaned_data.get('tth_start', 0)) or \
           (cleaned_data.get('tth_end', 0) - cleaned_data.get('tth_start', 0) > 6):
            raise ValidationError('Niepoprawny licznik końcowy!')

        if int(cleaned_data['fuel_used']) > self.operation.pdt.aircraft.fuel_capacity:
            raise ValidationError('Niepoprawna wartość zużytego paliwa!')

        if all(cleaned_data.get(field) for field in ('time_start', 'time_end', 'tth_start', 'tth_end')):
            start = cleaned_data.get('time_start').hour*60 + cleaned_data.get('time_start').minute
            end = cleaned_data.get('time_end').hour*60 + cleaned_data.get('time_end').minute
            if start > end:
                end += 60*24
            time_diff = end - start
            tth_diff = (cleaned_data.get('tth_end') - cleaned_data.get('tth_start')) * 60
            if self.operation.pdt.aircraft.helicopter:
                if time_diff + 6 < tth_diff:
                    raise ValidationError('Czas niezgodny z licznikiem!')
            else:
                if max(time_diff, tth_diff) != 0:

                    # Poprzednia wersja z kontrolą procentową (20%)
                    # if (max(time_diff, tth_diff) - min(time_diff, tth_diff)) / max(time_diff, tth_diff) > 0.2:
                    # Zamieniona na bezwzględną róznicę 1 godzina

                    if max(time_diff, tth_diff) - min(time_diff, tth_diff) > 60:

                        raise ValidationError('Czas niezgodny z licznikiem!')

        if not cleaned_data.get('loc_start', None):
            raise ValidationError('Podaj lotnisko startu!')
        if not cleaned_data.get('loc_end', None):
            raise ValidationError('Podaj lotnisko lądowania!')
        if not cleaned_data.get('time_start', None):
            raise ValidationError('Podaj czas startu!')
        if not cleaned_data.get('time_end', None):
            raise ValidationError('Podaj czas lądowania!')
        if not cleaned_data.get('tth_start', None):
            raise ValidationError('Podaj licznik początkowy!')
        if not cleaned_data.get('tth_end', None):
            raise ValidationError('Podaj licznik końcowy!')
        if not cleaned_data.get('landings', None):
            raise ValidationError('Podaj liczbę lądowań!')

        return cleaned_data


class CheckInForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.pdt = kwargs.pop('pdt')
        self.is_mobile = kwargs.pop('is_mobile')
        super(CheckInForm, self).__init__(*args, **kwargs)

        self.fields['fuel_after'] = forms.DecimalField(label='Paliwo uzup. po locie (L)')
        self.fields['fuel_after'].error_messages['required'] = 'Należy podać uzupełnione paliwo!'
        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in FuelTank.objects.filter(fuel_type=self.pdt.aircraft.fuel_type)]
        fuel_tanks+= [("other", "-- Poza SALT --")]
        self.fields['fuel_after_source'] = forms.ChoiceField(choices=fuel_tanks, label = 'Źródło paliwa')
        self.fields['fuel_after_source'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select', 'data-mini': 'true'}

        self.fields['flying'] = forms.ChoiceField(choices=[('tak', 'Tak'), ('nie', 'Nie')], label='SP zdatny do lotu')
        self.fields['flying'].widget.attrs = {'data-role': 'flipswitch'}

        self.fields['failure_desc'] = forms.CharField(max_length=400, required=False, widget=Textarea(attrs={'placeholder': 'Opis usterki ...'}),
                                                      label='Opis usterki')
        self.fields['remarks'] = forms.CharField(max_length=400, required=False, widget=Textarea(attrs={'placeholder': 'Informacje dodatkowe ...'}),
                                                 label='Informacje dodatkowe')

    def clean(self):
        cleaned_data = super(CheckInForm, self).clean()
        if (cleaned_data.get('fuel_after', 0) < 0 or
            cleaned_data.get('fuel_after', 0) > self.pdt.aircraft.fuel_capacity):
            raise ValidationError('Niepoprawna objętość paliwa!')
        if (cleaned_data.get('flying') == 'nie' and cleaned_data.get('failure_desc') in ('', None)):
            raise ValidationError('Podaj opis usterki!')
        if (cleaned_data.get('flying') == 'tak' and cleaned_data.get('failure_desc') not in ('', None) ):
            raise ValidationError('Oznacz jako niezdatny do lotu!')
        return cleaned_data


class PilotAircraftForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.aircraft_auth = kwargs.pop('aircraft_auth')
        super(PilotAircraftForm, self).__init__(*args, **kwargs)

        for aircraft, auth in self.aircraft_auth:
            self.fields['%s' % aircraft.pk] = forms.BooleanField(label='%s / %s' % (aircraft, aircraft.type), initial=auth)
            self.fields['%s' % aircraft.pk].required = False


class PilotTypesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.types_auth = kwargs.pop('types_auth')
        super(PilotTypesForm, self).__init__(*args, **kwargs)

        for type, auth in self.types_auth:
            self.fields[type] = forms.BooleanField(label=FlightTypes()[type], initial=auth)
            self.fields[type].required = False


class PanelFuelingForm(forms.ModelForm):
    class Meta:
        model = LocalFueling
        fields = ['date', 'person', 'aircraft','fueltank', 'fuel_volume', 'remarks']
        widgets = {'date':AdminDateWidget, 'remarks':Textarea(attrs={'rows':4, 'cols':100})}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        self.is_mobile = kwargs.pop('is_mobile')
        super(PanelFuelingForm, self).__init__(*args, **kwargs)

        aircraft_choices = [('', ('---------' if not self.is_mobile else 'Wybierz SP ...'))]
        aircraft_choices += [(aircraft.pk, '%s / %s' % (aircraft.registration, aircraft.type)) for aircraft in Aircraft.objects.all()]

        tank_choices = [('', ('---------' if not self.is_mobile else 'Wybierz zbiornik ...'))]
        tank_choices += [(tank.pk, '%s / %s' % (tank.name, tank.fuel_type)) for tank in FuelTank.objects.all()]

        self.fields['aircraft'].choices = aircraft_choices
        self.fields['fueltank'].choices = tank_choices
        self.fields['date'].initial = date.today()
        self.fields['person'].initial = user.__str__()

        if self.is_mobile:
            self.fields['aircraft'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}
            self.fields['fueltank'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}
            self.fields['remarks'].widget.attrs= {'rows':4, 'placeholder': 'Informacje dodatkowe ...'}

    def clean_fuel_volume(self, **kwargs):
        cleaned_data = super(PanelFuelingForm, self).clean()
        aircraft = cleaned_data.get('aircraft', None)
        if aircraft:
            if (cleaned_data.get('fuel_volume', 0) > aircraft.fuel_capacity or
                cleaned_data.get('fuel_volume', 0) <= 0):
                raise ValidationError('Niepoprawna objętość paliwa!')
        return cleaned_data['fuel_volume']

    def clean(self):
        cleaned_data = super(PanelFuelingForm, self).clean()
        aircraft = cleaned_data.get('aircraft', None)
        fueltank = cleaned_data.get('fueltank', None)

        if aircraft and fueltank:
            if (aircraft.fuel_type != fueltank.fuel_type):
                raise ValidationError('Niewłaściwy rodzaj paliwa!')

        if self.is_mobile:
            if not (aircraft and fueltank):
                raise ValidationError('Podaj SP oraz zbiornik!')

            if (cleaned_data.get('fuel_volume', 0) > aircraft.fuel_capacity or
                cleaned_data.get('fuel_volume', 0) <= 0):
                raise ValidationError('Niepoprawna objętość paliwa!')

        return cleaned_data