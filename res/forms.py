import pytz
from datetime import datetime, timedelta

from django import forms
from django.forms import Textarea, TextInput, DateTimeInput

from camo.models import Aircraft
from res.models import Reservation, ReservationFBO, ResourceFBO
from panel.models import FBOUser, Pilot, FlightTypes, PilotAircraft, PilotFlightType


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['aircraft', 'planned_type', 'owner', 'participant', 'start_time', 'end_time', 'planned_time',
                  'loc_start', 'loc_stop', 'loc_end', 'pax', 'remarks', 'internal_remarks']
        widgets = {'start_time': DateTimeInput(format="%d.%m.%Y %H:%M"),
                   'end_time': DateTimeInput(format="%d.%m.%Y %H:%M"),
                   'loc_start': TextInput(attrs={'size': 36}),
                   'loc_stop': TextInput(attrs={'size': 36}),
                   'loc_end': TextInput(attrs={'size': 36}),
                   'pax': Textarea(attrs={'rows': 2, 'cols': 100}),
                   'remarks': Textarea(attrs={'rows': 2, 'cols': 100}),
                   'internal_remarks': Textarea(attrs={'rows': 2, 'cols': 100})}

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        self.user = kwargs.pop('user')
        self.pilot = getattr(self.user.fbouser, 'pilot', None)
        self.start = kwargs.pop('start', None)
        self.end = kwargs.pop('end', None)
        self.res = kwargs.pop('res', None)
        super(ReservationForm, self).__init__(*args, **kwargs)

        if not (self.user.has_perm('res.res_admin') or self.user.fbouser.infos) or self.is_mobile:
            del self.fields['internal_remarks']

        if self.pilot and (not (self.user.has_perm('res.res_admin') or self.user.fbouser.infos)):
            aircraft_auth = [relation.aircraft for relation in PilotAircraft.objects.filter(pilot=self.pilot)]
            types_auth = [relation.flight_type for relation in PilotFlightType.objects.filter(pilot=self.pilot)]
        else:
            aircraft_auth = [aircraft for aircraft in Aircraft.objects.all()]
            types_auth = [flight_type for (flight_type, flight_type_name) in FlightTypes().items()]

        # Lista statków powietrznych ze statusami
        aircraft_list = []
        for aircraft in aircraft_auth:
            if not aircraft.status == 'flying':
                status = 'Uszkodzony'
                order = 2
            elif not aircraft.airworthy():
                status = 'Przekroczony MS'
                order = 1
            else:
                status = '%.2f TTH' % ((aircraft.ms_hours or 99999) - aircraft.hours_count)
                order = 0

            aircraft_list += [(aircraft, status, order)]

        # Sortowanie listy, tak aby dostępne były na początku
        aircraft_list.sort(key=lambda a: a[2])

        # Statek powietrzny
        choices = [('', ('---------' if not self.is_mobile else 'Wybierz SP ...'))]
        choices += [(aircraft.pk, aircraft.registration + '  (%s)' % status) for (aircraft, status, order) in aircraft_list]
        self.fields['aircraft'].choices = choices
        self.fields['aircraft'].error_messages['required'] = 'Należy wybrać statek powietrzny!'

        # Informacje o SP (ukryte)
        for (aircraft, status, order) in aircraft_list:
            self.fields['_info_%d' % aircraft.pk] = \
                forms.CharField(initial=aircraft.info, widget=forms.HiddenInput(), required=False)

        # Dostępne rodzaje lotów
        choices = [('', ('---------' if not self.is_mobile else 'Wybierz rodzaj lotu ...'))]
        choices += [(flight_type, FlightTypes()[flight_type]) for flight_type in types_auth]
        self.fields['planned_type'].choices = choices
        self.fields['planned_type'].error_messages['required'] = 'Należy wybrać rodzaj lotu!'

        # Właściciel rezerwacji
        choices = [('', ('---------' if not self.is_mobile else 'Wybierz właściciela ...'))]
        choices += [(pilot.pk, pilot) for pilot in Pilot.objects.order_by('fbouser__second_name', 'fbouser__first_name')]
        self.fields['owner'].choices = choices
        self.fields['owner'].error_messages['required'] = 'Należy wybrać właściciela!'
        if self.pilot:
            self.fields['owner'].initial = self.pilot

        # Uczestnik rezerwacji
        choices = [('', ('---------' if not self.is_mobile else 'Opcjonalny uczestnik ...'))]
        choices += [(pilot.pk, pilot) for pilot in Pilot.objects.order_by('fbouser__second_name', 'fbouser__first_name')]
        self.fields['participant'].choices = choices

        if self.is_mobile:
            self.fields['aircraft'].widget.attrs = \
            self.fields['owner'].widget.attrs = \
            self.fields['participant'].widget.attrs = \
            self.fields['planned_type'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

            self.fields['remarks'].widget.attrs = {'placeholder': 'Informacje dodatkowe...'}

        if self.res:
            try:
                aircraft = Aircraft.objects.get(pk=self.res)
            except:
                aircraft = None
            if aircraft:
                self.fields['aircraft'].initial = aircraft

        if self.start:
            try:
                start = datetime.strptime(self.start, '%Y-%m-%dT%H:%M:%S')
            except:
                start = None
            if start:
                self.fields['start_time'].initial = start

        if self.end:
            try:
                end = datetime.strptime(self.end, '%Y-%m-%dT%H:%M:%S')
            except:
                end = None
            if end:
                self.fields['end_time'].initial = end

            try:
                duration = self.fields['end_time'].initial - self.fields['start_time'].initial
                if duration.seconds > 30*60:
                    duration -= timedelta(seconds=30*60)
            except:
                duration = timedelta(seconds=0)

            self.fields['planned_time'].initial = duration

    def clean(self):
        cleaned_data = super(ReservationForm, self).clean()

        if self.is_mobile:
            if (cleaned_data.get('aircraft') == None) or (cleaned_data.get('planned_type') == None):
                raise forms.ValidationError("Wybierz SP i rodzaj lotu!")
            if (cleaned_data.get('start_time') == None or cleaned_data.get('end_time') == None):
                raise forms.ValidationError("Podaj terminy rezerwacji!")
            if cleaned_data.get('planned_time') == None:
                raise forms.ValidationError("Podaj planowany czas!")

        if cleaned_data['planned_type'] != '06A':
            if (cleaned_data.get('loc_start') == '') or (cleaned_data.get('loc_stop') == ''):
                raise forms.ValidationError("Dla tego typu lotu wymagana jest trasa!")

        if cleaned_data['end_time'] <= cleaned_data['start_time']:
            raise forms.ValidationError("Termin rozpoczęcia musi być wcześniejszy niż zakończenia!")
        if (cleaned_data['end_time'] - cleaned_data['start_time']).days >= 10:
            raise forms.ValidationError("Zbyt długi czas trwania rezerwacji!")
        if (cleaned_data['end_time'] - cleaned_data['start_time']).days * 24 * 60 + \
                        (cleaned_data['end_time'] - cleaned_data['start_time']).seconds / 60 < cleaned_data['planned_time'].seconds / 60:
            raise forms.ValidationError("Zbyt długi planowany czas lotu!")
        start = datetime(cleaned_data['start_time'].year, cleaned_data['start_time'].month,
                         cleaned_data['start_time'].day, tzinfo=pytz.utc)
        end = datetime(cleaned_data['end_time'].year, cleaned_data['end_time'].month, cleaned_data['end_time'].day,
                       hour=23, minute=59, tzinfo=pytz.utc)

        overlap = False
        for res in Reservation.objects.filter(aircraft=cleaned_data['aircraft']).exclude(start_time__gt=end).exclude(end_time__lt=start):
            if hasattr(self.instance, 'pk') and res.pk != self.instance.pk:
                if (res.start_time >= cleaned_data['start_time'] and res.start_time < cleaned_data['end_time']) or \
                        (res.end_time > cleaned_data['start_time'] and res.end_time <= cleaned_data['end_time']) or \
                        (cleaned_data['start_time'] >= res.start_time and cleaned_data['end_time'] <= res.end_time):
                    overlap = True
                    break
        if overlap:
            raise forms.ValidationError("Termin koliduje z inną rezerwacją!")

        return cleaned_data


class ReservationFBOForm(forms.ModelForm):
    class Meta:
        model = ReservationFBO
        fields = ['resource', 'owner', 'participant', 'start_time', 'end_time', 'title', 'remarks']
        widgets = {'start_time': DateTimeInput(format="%d.%m.%Y %H:%M"),
                   'end_time': DateTimeInput(format="%d.%m.%Y %H:%M"),
                   'title': TextInput(attrs={'size': 36}),
                   'remarks': Textarea(attrs={'rows': 4, 'cols': 100})}

    def __init__(self, *args, **kwargs):
        self.is_mobile = kwargs.pop('is_mobile')
        self.user = kwargs.pop('user')
        self.start = kwargs.pop('start', None)
        self.end = kwargs.pop('end', None)
        self.res = kwargs.pop('res', None)
        super(ReservationFBOForm, self).__init__(*args, **kwargs)

        # Zasób rezerwacji
        choices = [('', ('---------' if not self.is_mobile else 'Wybierz zasób ...'))]
        choices += [(resource.pk, resource.name) for resource in ResourceFBO.objects.all()]
        self.fields['resource'].choices = choices
        self.fields['resource'].error_messages['required'] = 'Należy wybrać statek powietrzny!'

        # Właściciel rezerwacji
        choices = [('', ('---------' if not self.is_mobile else 'Wybierz właściciela ...'))]
        choices += [(fbouser.pk, fbouser) for fbouser in FBOUser.objects.order_by('second_name', 'first_name')]
        self.fields['owner'].choices = choices
        self.fields['owner'].error_messages['required'] = 'Należy wybrać właściciela!'
        self.fields['owner'].initial = self.user.fbouser

        # Uczestnik rezerwacji
        choices = [('', ('---------' if not self.is_mobile else 'Opcjonalny uczestnik ...'))]
        choices += [(fbouser.pk, fbouser) for fbouser in FBOUser.objects.order_by('second_name', 'first_name')]
        self.fields['participant'].choices = choices

        if self.is_mobile:
            self.fields['resource'].widget.attrs = \
            self.fields['owner'].widget.attrs = \
            self.fields['participant'].widget.attrs = {'data-native-menu': 'false', 'class': 'filterable-select'}

            self.fields['title'].widget.attrs = {'placeholder': 'Tytuł rezerwacji...'}
            self.fields['remarks'].widget.attrs = {'placeholder': 'Informacje dodatkowe...'}

        if self.res:
            if self.res == 'infos':
                try:
                    resource = ResourceFBO.objects.get(name='INFOS')
                except:
                    resource = None
            else:
                try:
                    resource = ResourceFBO.objects.get(pk=self.res)
                except:
                    resource = None
            if resource:
                self.fields['resource'].initial = resource

        if self.start:
            try:
                start = datetime.strptime(self.start, '%Y-%m-%dT%H:%M:%S')
            except:
                start = None
            if start:
                self.fields['start_time'].initial = start

        if self.end:
            try:
                end = datetime.strptime(self.end, '%Y-%m-%dT%H:%M:%S')
            except:
                end = None
            if end:
                self.fields['end_time'].initial = end


    def clean(self):
        cleaned_data = super(ReservationFBOForm, self).clean()

        if self.is_mobile:
            if (cleaned_data.get('resource') == None):
                raise forms.ValidationError("Wybierz zasób!")
            if (cleaned_data.get('start_time') == None or cleaned_data.get('end_time') == None):
                raise forms.ValidationError("Podaj terminy rezerwacji!")
            if cleaned_data.get('title') == None:
                raise forms.ValidationError("Podaj tytuł rezerwacji!")

        if cleaned_data['end_time'] <= cleaned_data['start_time']:
            raise forms.ValidationError("Termin rozpoczęcia musi być wcześniejszy niż zakończenia!")
        if (cleaned_data['end_time'] - cleaned_data['start_time']).days >= 10:
            raise forms.ValidationError("Zbyt długi czas trwania rezerwacji!")

        return cleaned_data
