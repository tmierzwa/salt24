from django import forms
from camo.models import Aircraft, ATA, Part, POT_group, POT_event
from django.contrib.admin.widgets import AdminDateWidget
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class AircraftCreateForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        exclude = ['hours_count', 'landings_count', 'cycles_count', 'production_date', 'fuel_volume',
                   'ms_hours', 'ms_date', 'ms_landings', 'ms_cycles', 'rent_price', 'remarks', 'info', 'color']
        widgets = {
            'production_date': AdminDateWidget(),
            'insurance_date': AdminDateWidget(),
            'wb_date': AdminDateWidget(),
            'arc_date': AdminDateWidget(),
            'radio_date': AdminDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(AircraftCreateForm, self).__init__(*args, **kwargs)
        for prefix in ['af', 'e1', 'e2', 'p1', 'p2']:
            self.fields['%s_name' % prefix] = forms.CharField(label=Part._meta.get_field('name').verbose_name)
            self.fields['%s_maker' % prefix] = forms.CharField(label=Part._meta.get_field('maker').verbose_name)
            self.fields['%s_part_no' % prefix] = forms.CharField(label=Part._meta.get_field('part_no').verbose_name)
            self.fields['%s_serial_no' % prefix] = forms.CharField(label=Part._meta.get_field('serial_no').verbose_name)
            self.fields['%s_f1' % prefix] = forms.CharField(label=Part._meta.get_field('f1').verbose_name)
            self.fields['%s_ata' % prefix] = forms.ChoiceField(label='Sekcja ATA')
            self.fields['%s_lifecycle' % prefix] = forms.ChoiceField(label=Part._meta.get_field('lifecycle').verbose_name)
            self.fields['%s_due_hours' % prefix] = forms.DecimalField(label=POT_group._meta.get_field('due_hours').verbose_name)
            self.fields['%s_due_months' % prefix] = forms.IntegerField(label=POT_group._meta.get_field('due_months').verbose_name)
            self.fields['%s_due_landings' % prefix] = forms.IntegerField(label=POT_group._meta.get_field('due_landings').verbose_name)
            self.fields['%s_due_cycles' % prefix] = forms.IntegerField(label=POT_group._meta.get_field('due_cycles').verbose_name)
            self.fields['%s_production_date' % prefix] = forms.DateField(label=Part._meta.get_field('production_date').verbose_name)
            if prefix != 'af':
                self.fields['%s_install_date' % prefix] = forms.DateField(label=Part._meta.get_field('install_date').verbose_name)
            self.fields['%s_hours_count' % prefix] = forms.DecimalField(label=Part._meta.get_field('hours_count').verbose_name)
            self.fields['%s_landings_count' % prefix] = forms.IntegerField(label=Part._meta.get_field('landings_count').verbose_name)
            self.fields['%s_cycles_count' % prefix] = forms.IntegerField(label=Part._meta.get_field('cycles_count').verbose_name)

            if prefix != 'af':
                self.fields['%s_name' % prefix].required = False
                self.fields['%s_maker' % prefix].required = False
                self.fields['%s_part_no' % prefix].required = False
                self.fields['%s_serial_no' % prefix].required = False
                self.fields['%s_ata' % prefix].required = False
                self.fields['%s_lifecycle' % prefix].required = False
                self.fields['%s_production_date' % prefix].required = False
                self.fields['%s_install_date' % prefix].required = False
                self.fields['%s_hours_count' % prefix].required = False
                self.fields['%s_landings_count' % prefix].required = False
                self.fields['%s_cycles_count' % prefix].required = False

            self.fields['%s_f1' % prefix].required = False
            self.fields['%s_due_hours' % prefix].required = False
            self.fields['%s_due_months' % prefix].required = False
            self.fields['%s_due_landings' % prefix].required = False
            self.fields['%s_due_cycles' % prefix].required = False

            self.fields['%s_name' % prefix].widget = forms.TextInput(attrs={'size':'69'})
            self.fields['%s_maker' % prefix].widget = forms.TextInput(attrs={'size':'69'})
            self.fields['%s_ata' % prefix].choices = [(str(ata.pk), str(ata)[:50]) for ata in ATA.objects.all()]
            self.fields['%s_lifecycle' % prefix].choices = [('llp', 'Ograniczona żywotność (LLP)'),
                                                            ('ovh', 'Podlegająca remontowi (OVH)'),
                                                            ('oth', 'Według stanu')]
            if prefix == 'af':
                self.fields['%s_lifecycle' % prefix].initial = 'oth'
            else:
                self.fields['%s_lifecycle' % prefix].initial = 'ovh'
                self.fields['%s_install_date' % prefix].widget = AdminDateWidget()
            self.fields['%s_production_date' % prefix].widget = AdminDateWidget()

            self.fields['%s_hours_count' % prefix].initial = 0
            self.fields['%s_landings_count' % prefix].initial = 0
            self.fields['%s_cycles_count' % prefix].initial = 0

        self.fields['af_ata'].initial = get_object_or_404(ATA, section='53-00').pk
        self.fields['e1_ata'].initial = get_object_or_404(ATA, section='72(R)-00').pk
        self.fields['e2_ata'].initial = get_object_or_404(ATA, section='72(R)-00').pk
        self.fields['p1_ata'].initial = get_object_or_404(ATA, section='61-00').pk
        self.fields['p2_ata'].initial = get_object_or_404(ATA, section='61-00').pk

        self.fields['fuel_consumption'].initial = 0


class AircraftCloneForm(forms.Form):
    source = forms.ChoiceField(choices=[(str(aircraft.pk), '%s - %s' % (aircraft, aircraft.type))
                                        for aircraft in Aircraft.objects.all()], label='Wzorzec')
    registration = forms.CharField(label='Rejestracja')
    registration.widget = forms.TextInput(attrs={'size': '12', 'maxlength': '12'})
    production_date = forms.DateField(label='Data produkcji')
    production_date.widget = AdminDateWidget()


class AssignExistingPartCreateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        spare_parts = kwargs.pop('spare_parts', None)
        mounted_parts = kwargs.pop('mounted_parts', None)
        use_landings = kwargs.pop('use_landings', False)
        use_cycles = kwargs.pop('use_cycles', False)
        super(AssignExistingPartCreateForm, self).__init__(*args, **kwargs)
        if spare_parts:
            self.fields['part'].choices=[(str(part.pk), part) for part in spare_parts]
        if mounted_parts:
            self.fields['super_part'].choices=[('','')] + [(str(assignment.pk), assignment.part) for assignment in mounted_parts]
            self.fields['super_part'].initial=''
        if not use_landings:
            self.fields['from_landings'].widget = forms.HiddenInput()
        if not use_cycles:
            self.fields['from_cycles'].widget = forms.HiddenInput()


    part = forms.ChoiceField(label='Część do montażu')
    ata = forms.ChoiceField(choices=[(str(ata.pk), str(ata)[:50]) for ata in ATA.objects.all()], label='Sekcja ATA')
    description = forms.CharField(label='Dodatkowy opis')
    description.widget = forms.TextInput(attrs={'size':'69'})
    description.required = False
    crs = forms.CharField(label='CRS montażu')
    crs.widget = forms.TextInput(attrs={'size':'69'})
    crs.required = False
    super_part = forms.ChoiceField(label='Część nadrzędna')
    super_part.required = False
    from_date = forms.DateField(label='Data montażu')
    from_date.widget = AdminDateWidget()
    from_hours = forms.DecimalField(label='TTH przy montażu')
    from_landings = forms.IntegerField(label='Lądowania przy montażu')
    from_cycles = forms.IntegerField(label='Cykle przy montażu')


class AssignNewPartCreateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        mounted_parts = kwargs.pop('mounted_parts', None)
        use_landings = kwargs.pop('use_landings', False)
        use_cycles = kwargs.pop('use_cycles', False)
        super(AssignNewPartCreateForm, self).__init__(*args, **kwargs)
        if mounted_parts:
            self.fields['super_part'].choices=[('','')] + [(str(assignment.pk), assignment.part) for assignment in mounted_parts]
            self.fields['super_part'].initial=''
        if not use_landings:
            self.fields['due_landings'].widget = forms.HiddenInput()
            self.fields['landings_count'].widget = forms.HiddenInput()
            self.fields['from_landings'].widget = forms.HiddenInput()
        if not use_cycles:
            self.fields['due_cycles'].widget = forms.HiddenInput()
            self.fields['cycles_count'].widget = forms.HiddenInput()
            self.fields['from_cycles'].widget = forms.HiddenInput()

    name = forms.CharField(label=Part._meta.get_field('name').verbose_name)
    name.widget = forms.TextInput(attrs={'size':'69'})
    maker = forms.CharField(label=Part._meta.get_field('maker').verbose_name)
    maker.widget = forms.TextInput(attrs={'size':'69'})
    ata = forms.ChoiceField(choices=[(str(ata.pk), str(ata)[:50]) for ata in ATA.objects.all()], label='Sekcja ATA')
    ata.choices = [(str(ata.pk), str(ata)[:50]) for ata in ATA.objects.all()]
    part_no = forms.CharField(label=Part._meta.get_field('part_no').verbose_name)
    serial_no = forms.CharField(label=Part._meta.get_field('serial_no').verbose_name)
    f1 = forms.CharField(label=Part._meta.get_field('f1').verbose_name)
    f1.required = False
    lifecycle = forms.ChoiceField(label=Part._meta.get_field('lifecycle').verbose_name)
    lifecycle.choices = [('llp', 'Ograniczona żywotność (LLP)'),
                         ('ovh', 'Podlegająca remontowi (OVH)'),
                         ('oth', 'Według stanu')]
    lifecycle.initial = 'oth'
    due_hours = forms.DecimalField(label=POT_group._meta.get_field('due_hours').verbose_name)
    due_hours.required = False
    due_months = forms.DecimalField(label=POT_group._meta.get_field('due_months').verbose_name)
    due_months.required = False
    due_landings = forms.IntegerField(label=POT_group._meta.get_field('due_landings').verbose_name)
    due_landings.required = False
    due_cycles = forms.IntegerField(label=POT_group._meta.get_field('due_cycles').verbose_name)
    due_cycles.required = False
    production_date = forms.DateField(label=Part._meta.get_field('production_date').verbose_name)
    production_date.required = False
    production_date.widget = AdminDateWidget()
    install_date = forms.DateField(label=Part._meta.get_field('install_date').verbose_name)
    install_date.widget = AdminDateWidget()
    install_date.required = False
    description = forms.CharField(label='Dodatkowy opis')
    description.widget = forms.TextInput(attrs={'size':'69'})
    description.required = False
    crs = forms.CharField(label='CRS montażu')
    crs.widget = forms.TextInput(attrs={'size':'69'})
    crs.required = False
    super_part = forms.ChoiceField(label='Część nadrzędna')
    super_part.required = False
    from_date = forms.DateField(label='Data montażu')
    from_date.widget = AdminDateWidget()
    from_hours = forms.DecimalField(label='TTH SP przy montażu')
    from_landings = forms.IntegerField(label='Lądowania SP przy montażu')
    from_cycles = forms.IntegerField(label='Cykle SP przy montażu')
    hours_count = forms.DecimalField(label='TTH części przy montażu')
    hours_count.initial = 0
    landings_count = forms.IntegerField(label='Lądowania części przy montażu')
    landings_count.initial = 0
    cycles_count = forms.IntegerField(label='Cykle części przy montażu')
    cycles_count.initial = 0


class AssignmentUpdateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        mounted_parts = kwargs.pop('mounted_parts', None)
        use_landings = kwargs.pop('use_landings', False)
        use_cycles = kwargs.pop('use_cycles', False)
        super(AssignmentUpdateForm, self).__init__(*args, **kwargs)
        if mounted_parts:
            self.fields['super_part'].choices=[('','')] + [(str(assignment.pk), assignment.part) for assignment in mounted_parts]
        if not use_landings:
            self.fields['from_landings'].widget = forms.HiddenInput()
        if not use_cycles:
            self.fields['from_cycles'].widget = forms.HiddenInput()

    ata = forms.ChoiceField(choices=[(str(ata.pk), str(ata)[:50]) for ata in ATA.objects.all()], label='Sekcja ATA')
    description = forms.CharField(label='Dodatkowy opis')
    description.widget = forms.TextInput(attrs={'size':'69'})
    description.required = False
    crs = forms.CharField(label='CRS montażu')
    crs.widget = forms.TextInput(attrs={'size':'69'})
    crs.required = False
    super_part = forms.ChoiceField(label='Część nadrzędna')
    super_part.required = False
    from_date = forms.DateField(label='Data montażu')
    from_date.widget = AdminDateWidget()
    from_hours = forms.DecimalField(label='TTH przy montażu')
    from_landings = forms.IntegerField(label='Lądowania przy montażu')
    from_cycles = forms.IntegerField(label='Cykle przy montażu')


class AssignmentDeleteForm(forms.Form):

     def __init__(self, *args, **kwargs):
        use_landings = kwargs.pop('use_landings', False)
        use_cycles = kwargs.pop('use_cycles', False)
        super(AssignmentDeleteForm, self).__init__(*args, **kwargs)
        if not use_landings:
            self.fields['to_landings'].widget = forms.HiddenInput()
        if not use_cycles:
            self.fields['to_cycles'].widget = forms.HiddenInput()

     to_date = forms.DateField(label='Data demontażu')
     to_hours = forms.DecimalField(label='TTH przy demontażu')
     to_landings = forms.IntegerField(label='Lądowania przy demontażu')
     to_cycles = forms.IntegerField(label='Cykle przy demontażu')


class POTGroupCloneForm(forms.Form):

    def __init__(self, *args, **kwargs):
        parts = kwargs.pop('parts', None)
        super(POTGroupCloneForm, self).__init__(*args, **kwargs)
        if parts:
            self.fields['parts'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='Lista części')
            self.fields['parts'].required = False
            choices = []
            for part in parts:
                if part.assignment_set.filter(current=True):
                    choices.append((part.pk, '%s - S/N: %s' % (part.assignment_set.get(current=True).aircraft, part.serial_no)))
                else:
                    choices.append((part.pk, 'Magazyn - S/N: %s' % part.serial_no))
                self.fields['parts'].choices = choices
            self.fields['parts'].initial = [part.pk for part in parts]


class FileUploadForm(forms.Form):

    def clean_file(self):
        cleaned_data = super(FileUploadForm, self).clean()
        file = cleaned_data['file']
        if file.name[-4:].upper() != '.CSV':
           raise ValidationError('Nieprawidłowe rozszerzenie pliku', code='wrong_ext')
        # elif file.content_type != 'text/csv':
        #    raise ValidationError('Nieprawidłowy format pliku %s' % file.content_type, code='wrong_csv')
        elif file.size > 100000:
           raise ValidationError('Zbyt duży rozmiar pliku', code='wrong_size')
        return file

    def clean_delimiter(self):
        cleaned_data = super(FileUploadForm, self).clean()
        delimiter = cleaned_data['delimiter']
        if delimiter not in [';', ',', '|']:
           raise ValidationError('Niedopuszczalny separator', code='wrong_delimiter')
        return delimiter

    file = forms.FileField()
    file.label = 'Plik z danymi (CSV):'
    delimiter = forms.CharField()
    delimiter.initial = ';'
    delimiter.widget = forms.TextInput(attrs={'size':'1'})
    delimiter.label = 'Separator pól:'
    headerline = forms.BooleanField()
    headerline.initial = True
    headerline.label = 'Wiersz nagłówka:'
    headerline.required = False


class POTGroupImportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        part = kwargs.pop('part', None)
        type = kwargs.pop('type', None)
        fields = kwargs.pop('fields', None)
        super(POTGroupImportForm, self).__init__(*args, **kwargs)

        if data:
            for row, data_row in enumerate(data):
                label = ''
                disabled = False

                # czy dany POT_ref dla danej częsci istnieje w bazie
                if POT_group.objects.filter(part=part, type=type, POT_ref=data_row[0]):
                    existing = True
                else:
                    existing = False

                # kosntrukcja wiersza tabeli ze wszystkich pól
                for ind, data_field in enumerate(data_row):
                    # konwersja pola na tekst
                    str_field = (str(data_field) if data_field != None else "")

                    # skrócenie pola
                    if len(str_field) > 34:
                        str_field = str_field[:31]+'...'

                    # konstrukcja pola tabeli
                    if str_field != "":
                        # dla pól niepustych
                        if existing and ind==0:
                            # jeśli taki identyfikator istnieje w tabeli to na żółto
                            label += '<td style="background-color: #ffdc99">%s</td>' % str_field
                        else:
                            label += '<td>%s</td>' % str_field
                    elif fields[ind][4]:
                        # dla pól pustych wymaganych
                        label += '<td style="background-color: #f4a4a4"></td>'
                        disabled = True
                    else:
                        # dla pól pustych niewymaganych
                        label += '<td></td>'

                # wiersz tabeli jako pole formularza (checkbox dla tych które można wybrać)
                self.fields["row%d" % row] = forms.BooleanField(label=label)
                self.fields["row%d" % row].required = False
                if disabled:
                    self.fields["row%d" % row].widget.attrs['disabled'] = True
                    self.fields["row%d" % row].initial = False
                else:
                    if existing:
                        self.fields["row%d" % row].initial = False
                    else:
                        self.fields["row%d" % row].initial = True


class POTEventImportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', None)
        pot_group = kwargs.pop('pot_group', None)
        fields = kwargs.pop('fields', None)
        super(POTEventImportForm, self).__init__(*args, **kwargs)

        if data:
            for row, data_row in enumerate(data):
                label = ''
                disabled = False

                # czy dany POT_ref dla danej grupy istnieje w bazie
                if POT_event.objects.filter(POT_group=pot_group, POT_ref = data_row[0]):
                    existing = True
                else:
                    existing = False

                # kosntrukcja wiersza tabeli ze wszystkich pól
                for ind, data_field in enumerate(data_row):
                    # konwersja pola na tekst
                    str_field = (str(data_field) if data_field != None else "")

                    # skrócenie pola
                    if len(str_field) > 34:
                        str_field = str_field[:31]+'...'

                    # konstrukcja pola tabeli
                    if str_field != "":
                        # dla pól niepustych
                        if existing and ind==0:
                            # jeśli taki identyfikator istnieje w tabeli to na żółto
                            label += '<td style="background-color: #ffdc99">%s</td>' % str_field
                        else:
                            label += '<td>%s</td>' % str_field
                    elif fields[ind][4]:
                        # dla pól pustych wymaganych
                        label += '<td style="background-color: #f4a4a4"></td>'
                        disabled = True
                    else:
                        # dla pól pustych niewymaganych
                        label += '<td></td>'

                # wiersz tabeli jako pole formularza (checkbox dla tych które można wybrać)
                self.fields["row%d" % row] = forms.BooleanField(label=label)
                self.fields["row%d" % row].required = False
                if disabled:
                    self.fields["row%d" % row].widget.attrs['disabled'] = True
                    self.fields["row%d" % row].initial = False
                else:
                    if existing:
                        self.fields["row%d" % row].initial = False
                    else:
                        self.fields["row%d" % row].initial = True


class PartPurgeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        part = kwargs.pop('part', None)
        type = kwargs.pop('type', None)
        fields = kwargs.pop('fields', None)
        super(PartPurgeForm, self).__init__(*args, **kwargs)

        for group in part.pot_group_set.filter(type=type):

            label = ''
            # konstrukcja wiersza tabeli
            for num, field in enumerate(fields):

                # konwersja pola na tekst
                data_field = getattr(group, field[1])
                str_field = (str(data_field) if data_field != None else "")

                # skrócenie pola
                if len(str_field) > 54:
                    str_field = str_field[:51]+'...'

                # konstrukcja pola tabeli
                label += '<td nowrap style="text-align:'
                if field[2]:
                    label += 'center"'
                else:
                    label += 'left"'
                if num == 0:
                    label += '><b>%s</b></td>' % str_field
                else:
                    label += '>%s</td>' % str_field

            # wiersz tabeli jako pole formularza z checkboxem
            self.fields["group%d" % group.pk] = forms.BooleanField(label=label)
            self.fields["group%d" % group.pk].required = False
            self.fields["group%d" % group.pk].initial = False


class WorkOrderCreateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups', None)
        super(WorkOrderCreateForm, self).__init__(*args, **kwargs)
        if groups:
            for (type, label) in [('oth', 'Obsługi'), ('ad', 'Dyrektywy'), ('sb', 'Biuletyny'), ('llp', 'Demontaże'), ('ovh', 'Remonty')]:
                self.fields[type] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label=label)
                self.fields[type].required = False
                self.fields[type].choices = []
                self.fields[type].initial = []
                list = [group for group in groups if group.type == type]
                if len(list) > 0:
                    for group in list:
                        if group.leftx() < 99999:
                            label = '%s' % group.leftx()
                            if group.leftx() == group.left_hours():
                                label += ' FH'
                            elif group.leftx() == group.left_landings():
                                label += ' ldg.'
                            elif group.leftx() == group.left_cycles():
                                label += ' cycl.'
                            else:
                                label += ' dni'
                            label += ' - (%s) %s' % (group.POT_ref, group.name)
                            self.fields[type].choices.append((group.pk, label))
                            # Automatyczny wybór tych którym pozostało mniej niż 20 jednostek
                            if group.leftx() < 20:
                                self.fields[type].initial.append(group.pk)
                        else:
                            self.fields[type].choices.append((group.pk, '(%s) %s' % (group.POT_ref, group.name)))
                else:
                    self.fields[type].widget = forms.HiddenInput()
                    self.fields[type].initial = ''

    number = forms.CharField(label='Numer zlecenia')
    date = forms.DateField(label='Data zlecenia')
    organization = forms.CharField(label="Organizacja")


class WorkOrderCloseForm(forms.Form):
    pass


class CRSCreateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        use_landings = kwargs.pop('use_landings', False)
        use_cycles = kwargs.pop('use_cycles', False)
        lines = kwargs.pop('lines', None)
        super(CRSCreateForm, self).__init__(*args, **kwargs)
        if lines:
            self.fields['lines'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                                 label='Paczki czynności')
            self.fields['lines'].choices = [(line.pk, '(%s) %s' % (line.pot_group.POT_ref, line.pot_group.name)) for line in lines]
            self.fields['lines'].initial = [line.pk for line in lines]
        if not use_landings:
            self.fields['landings'].widget = forms.HiddenInput()
        if not use_cycles:
            self.fields['cycles'].widget = forms.HiddenInput()

    number = forms.CharField(label='Numer CRS')
    date = forms.DateField(label='Data wykonania')
    hours = forms.DecimalField(label='TTH wykonania')
    landings = forms.IntegerField(label='Liczba lądowań')
    cycles = forms.IntegerField(label='Liczba cykli')
    close = forms.BooleanField(label='Zamknąć zlecenie?', initial=True, required=False)

