import csv, datetime
from django.utils import timezone
from io import TextIOWrapper
from time import strptime, strftime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import permission_required
from django.db.models import Max

from camo.models import Aircraft, Part, POT_group, POT_event, CAMO_operation
from panel.models import PDT
from camo.forms import FileUploadForm, POTGroupImportForm, POTEventImportForm


@permission_required('camo.camo_admin')
def POTGroupUpload (request, type, part_id):
    context = {}
    part = get_object_or_404(Part, pk=part_id)

    context['object'] = part
    context['submenu_template'] = 'camo/part_submenu.html'

    # konfiguracja pól dla różnych typów plików
    if type == 'ad':
        desc = 'dyrektyw'
        fields = [('AD Ref.', 'POT_ref', 'char', 100, True),
                  ('AD No.', 'adsb_no', 'char', 50, True),
                  ('AD\nDate', 'adsb_date', 'date', None, False),
                  ('Subject', 'name', 'char', 500, True),
                  ('Agency', 'adsb_agency', 'char', 20, False),
                  ('Rec.\nFH', 'due_hours', 'number', None, False),
                  ('Rec.\nmths.', 'due_months', 'int', None, False),
                  ('Perf.\ndate', 'done_date', 'date', None, False),
                  ('Perf.\nTTH', 'done_hours', 'number', None, False),
                  ('Maint.\norg.', 'done_aso', 'char', 100, False),
                  ('CRS\nRef.', 'done_crs', 'char', 20, False),
                  ('Related\nSB', 'adsb_related', 'char', 50, False),
                  ('Cyclic', 'cyclic', 'boolean', None, True),
                  ('Apply', 'applies', 'boolean', None, True),
                  ('Analysis', 'remarks', 'char', 500, False)]
        if part.use_cycles():
            fields.insert(9, ('Perf.\ncycl.', 'done_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(9, ('Perf.\nldgs.', 'done_landings', 'int', None, False))
        if part.use_cycles():
            fields.insert(7, ('Rec.\ncycl.', 'due_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(7, ('Rec.\nldgs.', 'due_landings', 'int', None, False))

        defaults = [('parked', False),
                    ('optional', False),
                    ('count_type', 'production')]

        if not part.use_landings():
            defaults.append(('due_landings', None))
            defaults.append(('done_landings', None))
        if not part.use_cycles():
            defaults.append(('due_cycles', None))
            defaults.append(('done_cycles', None))

    elif type == 'sb':
        desc = 'biuletynów'
        fields = [('SB Ref.', 'POT_ref', 'char', 100, True),
                  ('SB No.', 'adsb_no', 'char', 50, True),
                  ('SB\nDate', 'adsb_date', 'date', None, False),
                  ('Subject', 'name', 'char', 500, True),
                  ('Agency', 'adsb_agency', 'char', 20, False),
                  ('Rec.\nFH', 'due_hours', 'number', None, False),
                  ('Rec.\nmths.', 'due_months', 'int', None, False),
                  ('Perf.\ndate', 'done_date', 'date', None, False),
                  ('Perf.\nTTH', 'done_hours', 'number', None, False),
                  ('Maint.\norg.', 'done_aso', 'char', 100, False),
                  ('CRS\nRef.', 'done_crs', 'char', 20, False),
                  ('Related\nAD', 'adsb_related', 'char', 50, False),
                  ('Cyclic', 'cyclic', 'boolean', None, True),
                  ('Apply', 'applies', 'boolean', None, True),
                  ('Analysis', 'remarks', 'char', 500, False)]
        if part.use_cycles():
            fields.insert(9, ('Perf.\ncycl.', 'done_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(9, ('Perf.\nldgs.', 'done_landings', 'int', None, False))
        if part.use_cycles():
            fields.insert(7, ('Rec.\ncycl.', 'due_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(7, ('Rec.\nldgs.', 'due_landings', 'int', None, False))

        defaults = [('parked', False),
                    ('optional', False),
                    ('count_type', 'production')]

        if not part.use_landings():
            defaults.append(('due_landings', None))
            defaults.append(('done_landings', None))
        if not part.use_cycles():
            defaults.append(('due_cycles', None))
            defaults.append(('done_cycles', None))

    elif type == 'llp':
        desc = 'demontaży'
        fields = []
        defaults = []

    elif type == 'ovh':
        desc = 'remontów'
        fields = []
        defaults = []

    else:
        desc = 'obsług'
        fields = [('POT Ref.', 'POT_ref', 'char', 100, True),
                  ('Descr.', 'name', 'char', 500, True),
                  ('Limit\nFH', 'due_hours', 'number', None, False),
                  ('Limit\nmths.', 'due_months', 'int', None, False),
                  ('Perf.\ndate', 'done_date', 'date', None, False),
                  ('Perf.\nTTH', 'done_hours', 'number', None, False),
                  ('Maint.\norg.', 'done_aso', 'char', 100, False),
                  ('CRS\nRef.', 'done_crs', 'char', 20, False),
                  ('Apply', 'applies', 'boolean', None, True),
                  ('Notes', 'remarks', 'char', 500, False)]
        if part.use_cycles():
            fields.insert(6, ('Perf.\ncycl.', 'done_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(6, ('Perf.\nldgs.', 'done_landings', 'int', None, False))
        if part.use_cycles():
            fields.insert(4, ('Limit\ncycl.', 'due_cycles', 'int', None, False))
        if part.use_landings():
            fields.insert(4, ('Limit\nldgs.', 'due_landings', 'int', None, False))

        defaults = [('cyclic', True),
                    ('parked', False),
                    ('optional', False),
                    ('count_type', 'production')]
        if not part.use_landings():
            defaults.append(('due_landings', None))
            defaults.append(('done_landings', None))
        if not part.use_cycles():
            defaults.append(('due_cycles', None))
            defaults.append(('done_cycles', None))

    context['title'] = "Wczytywanie %s dla %s" % (desc, part)

    form = FileUploadForm(request.POST or None, request.FILES or None)
    context['form'] = form
    context['fields'] = fields

    if form.is_valid():

        # funkcja czyszcząca i walidująca różne typy pól
        def validate (value, type, length):
            if value:
                if type == 'char':
                    value = value[:length-1]
                elif type == 'number':
                    value = value.replace(' ','').replace (',','.')
                    try:
                        value = float(value)
                    except:
                        value = None
                elif type == 'int':
                    try:
                        value = int(value)
                    except:
                        value = None
                elif type == 'boolean':
                    if value.upper() == 'TAK':
                        value = True
                    elif value.upper() == 'NIE':
                        value = False
                    else:
                        value = None
                elif type == 'date':
                    value = value.replace ('.','-').replace (':','-').replace ('/','-').replace ('\\','-')[:10]
                    try:
                        value = strptime(value, '%d-%m-%Y')
                    except:
                        try:
                            value = strptime(value, '%Y-%m-%d')
                        except:
                            try:
                                value = strptime(value, '%d-%m-%y')
                            except:
                                try:
                                    value = strptime(value, '%y-%m-%d')
                                except:
                                    value = None
                    if value:
                        value = strftime("%Y-%m-%d", value)

            return value

        file_data = []

        # wraper jest potrzebny bo domyślnie otwiera się jako binary
        with TextIOWrapper(request.FILES['file'].file, encoding='ISO-8859-2') as f:
            reader = csv.reader(f, dialect='excel', delimiter=form.cleaned_data['delimiter'])
            skip = True
            # wczytanie kolejnych linii z pliku źródłoweg0
            for row in reader:
                # ewentualne pominięcie wiersza nagłówkowego
                if form.cleaned_data['headerline'] and skip:
                    skip = False
                else:
                    # jeżeli nie pusta linia
                    if len(row) > 0:
                        row_fields = []
                        i = 0
                        # wczytanie kolejnych pól z pliku źrółowego
                        for field in fields:
                            if i < len(row):
                                row_fields.append(validate(row[i], field[2], field[3]))
                            else:
                                row_fields.append("")
                            i += 1
                        file_data.append(row_fields)

        # zmienne przekazywane w sesji do następnego view
        request.session['fields'] = fields
        request.session['defaults'] = defaults
        request.session['file_data'] = file_data

        return HttpResponseRedirect(reverse('camo:pot-group-import', args=(type, part_id, )))

    return render(request, 'camo/file_upload.html', context)


@permission_required('camo.camo_admin')
def POTGroupImport (request, type, part_id):
    context = {}
    part = get_object_or_404(Part, pk=part_id)

    context['object'] = part
    context['submenu_template'] = 'camo/part_submenu.html'

    if type == 'ad':
        desc = 'dyrektyw'
    elif type == 'sb':
        desc = 'biuletynów'
    elif type == 'llp':
        desc = 'demontaży'
    elif type == 'ovh':
        desc = 'remontów'
    else:
        desc = 'obsług'

    context['title'] = 'Wczytywanie %s dla %s' % (desc, part)

    # odczytanie zmiennych z sesji
    file_data = request.session['file_data']
    fields = request.session['fields']
    defaults = request.session['defaults']

    # formularz w formie tabeli do wybotu rekordów do wczytania
    form = POTGroupImportForm(request.POST or None, request.FILES or None, fields=fields, data=file_data, part=part, type=type)
    context['form'] = form
    context['headers'] = [field[0] for field in fields]

    if form.is_valid():

        # zapisanie do bazy kolejnych zaznaczonych rekordów
        for row, data in enumerate(file_data):
            # jeśli wiersz został zaznaczony
            if form.cleaned_data['row%d' % row]:

                # sprawdzenie czy taka grupa już istnieje dla tej części i typu
                try:
                    group = POT_group.objects.get(part=part, type=type, POT_ref=data[0])
                except ObjectDoesNotExist:
                    group = None

                if not group:
                    # nowa POT_grupa dla tej części i tego typu
                    group = POT_group(part=part, type=type)

                # dla wszystkich pól z danego rekordu
                for i, field in enumerate(fields):
                    # ustawienie wartości atrybutu POT_grupy
                    setattr(group, field[1], (data[i] if data[i] != "" else None))

                # uzupełnienie domyślnych wartości pól nie wczytywanych z pliku
                for field in defaults:
                    setattr(group, field[0], field[1])

                group.clean()
                group.save()

        # skasowanie zmiennych z sesji
        if request.session['file_data']:
            del request.session['file_data']
        if request.session['defaults']:
            del request.session['defaults']
        if request.session['fields']:
            del request.session['fields']

        # przekierowanie do właściwego viewsa na podstawie typu
        if type == 'ad':
            return HttpResponseRedirect(reverse('camo:part-dirs', args=(part_id, )))
        elif type == 'sb':
            return HttpResponseRedirect(reverse('camo:part-sbs', args=(part_id, )))
        elif type == 'llp':
            return HttpResponseRedirect(reverse('camo:part-llp', args=(part_id, )))
        elif type == 'ovh':
            return HttpResponseRedirect(reverse('camo:part-ovhs', args=(part_id, )))
        else:
            return HttpResponseRedirect(reverse('camo:part-pots', args=(part_id, )))

    return render(request, 'camo/file_import.html', context)


@permission_required('camo.camo_admin')
def POTEventUpload (request, pot_group_id):
    context = {}
    pot_group = get_object_or_404(POT_group, pk=pot_group_id)

    context['object'] = pot_group.part
    context['submenu_template'] = 'camo/part_submenu.html'

    # konfiguracja pól
    fields = [('POT Ref.', 'POT_ref', 'char', 100, True),
              ('Subject', 'name', 'char', 500, True),
              ('Perf.\ndate', 'done_date', 'date', None, False),
              ('Perf.\nTTH', 'done_hours', 'number', None, False),
              ('CRS\nRef.', 'done_crs', 'char', 20, False)]
    if pot_group.part.use_cycles():
        fields.insert(4, ('Perf.\ncycl.', 'done_cycles', 'int', None, False))
    if pot_group.part.use_landings():
        fields.insert(4, ('Perf.\nldgs.', 'done_landings', 'int', None, False))

    defaults = []
    if not pot_group.part.use_landings():
        defaults.append(('done_landings', None))
    if not pot_group.part.use_cycles():
        defaults.append(('done_cycles', None))

    context['title'] = "Wczytywanie czynności dla %s" % pot_group.POT_ref

    form = FileUploadForm(request.POST or None, request.FILES or None)
    context['form'] = form
    context['fields'] = fields

    if form.is_valid():

        # funkcja czyszcząca i walidująca różne typy pól
        def validate (value, type, length):
            if value:
                if type == 'char':
                    value = value[:length-1]
                elif type == 'number':
                    value = value.replace(' ','').replace (',','.')
                    try:
                        value = float(value)
                    except:
                        value = None
                elif type == 'int':
                    try:
                        value = int(value)
                    except:
                        value = None
                elif type == 'boolean':
                    if value.upper() == 'TAK':
                        value = True
                    elif value.upper() == 'NIE':
                        value = False
                    else:
                        value = None
                elif type == 'date':
                    value = value.replace ('.','-').replace (':','-').replace ('/','-').replace ('\\','-')[:10]
                    try:
                        value = strptime(value, '%d-%m-%Y')
                    except:
                        try:
                            value = strptime(value, '%Y-%m-%d')
                        except:
                            try:
                                value = strptime(value, '%d-%m-%y')
                            except:
                                try:
                                    value = strptime(value, '%y-%m-%d')
                                except:
                                    value = None
                    if value:
                        value = strftime("%Y-%m-%d", value)

            return value

        file_data = []

        # wraper jest potrzebny bo domyślnie otwiera się jako binary
        with TextIOWrapper(request.FILES['file'].file, encoding='ISO-8859-2') as f:
            reader = csv.reader(f, dialect='excel', delimiter=form.cleaned_data['delimiter'])
            skip = True
            # wczytanie kolejnych linii z pliku źródłoweg0
            for row in reader:
                # ewentualne pominięcie wiersza nagłówkowego
                if form.cleaned_data['headerline'] and skip:
                    skip = False
                else:
                    # jeżeli nie pusta linia
                    if len(row) > 0:
                        row_fields = []
                        i = 0
                        # wczytanie kolejnych pól z pliku źrółowego
                        for field in fields:
                            if i < len(row):
                                row_fields.append(validate(row[i], field[2], field[3]))
                            else:
                                row_fields.append("")
                            i += 1
                        file_data.append(row_fields)

        # zmienne przekazywane w sesji do następnego view
        request.session['fields'] = fields
        request.session['defaults'] = defaults
        request.session['file_data'] = file_data

        return HttpResponseRedirect(reverse('camo:pot-event-import', args=(pot_group_id, )))

    return render(request, 'camo/file_upload.html', context)


@permission_required('camo.camo_admin')
def POTEventImport (request, pot_group_id):
    context = {}
    pot_group = get_object_or_404(POT_group, pk=pot_group_id)

    context['object'] = pot_group.part
    context['submenu_template'] = 'camo/part_submenu.html'

    # odczytanie zmiennych z sesji
    file_data = request.session['file_data']
    fields = request.session['fields']
    defaults = request.session['defaults']

    context['title'] = 'Wczytywanie czynności dla %s' % pot_group.POT_ref

    # formularz w formie tabeli do wybotu rekordów do wczytania
    form = POTEventImportForm(request.POST or None, request.FILES or None, fields=fields, data=file_data, pot_group=pot_group)
    context['form'] = form
    context['headers'] = [field[0] for field in fields]

    if form.is_valid():

        # zapisanie do bazy kolejnych zaznaczonych rekordów
        for row, data in enumerate(file_data):
            # jeśli wiersz został zaznaczony
            if form.cleaned_data['row%d' % row]:

                # sprawdzenie czy dla tegj grupy istnieje już czynność o tym identyfikatorze
                try:
                    event = POT_event.objects.get(POT_group=pot_group, POT_ref = data[0])
                except ObjectDoesNotExist:
                    event = None

                if not event:
                    # nowy POT_event dla tej grupy
                    event = POT_event(POT_group=pot_group)

                # dla wszystkich pól z danego rekordu
                for i, field in enumerate(fields):
                    # ustawienie wartości atrybutu POT_eventu
                    setattr(event, field[1], (data[i] if data[i] != "" else None))

                # uzupełnienie domyślnych wartości pól nie wczytywanych z pliku
                for field in defaults:
                    setattr(event, field[0], field[1])

                event.clean()
                event.save()

        # skasowanie zmiennych z sesji
        if request.session['file_data']:
            del request.session['file_data']
        if request.session['defaults']:
            del request.session['defaults']
        if request.session['fields']:
            del request.session['fields']

        # przekierowanie do właściwego viewsa
        return HttpResponseRedirect(reverse('camo:pot-group-events', args=(pot_group_id, )))

    return render(request, 'camo/file_import.html', context)


def update(request):
    for aircraft in Aircraft.objects.all():
        ms = aircraft.ms_report_set.order_by('done_date').last()
        if ms:
            aircraft.ms_hours = ms.next_hours
            aircraft.ms_date = ms.next_date
            aircraft.ms_landings = ms.next_landings
            aircraft.ms_cycles = ms.next_cycles
        else:
            aircraft.ms_hours = None
            aircraft.ms_date = None
            aircraft.ms_landings = None
            aircraft.ms_cycles = None

        pdt = aircraft.pdt_set.order_by('tth_start').last()
        if pdt:
            aircraft.last_pdt_ref = pdt.pdt_ref
        else:
            aircraft.last_pdt_ref = 0

        tth = CAMO_operation.objects.filter(aircraft=aircraft).aggregate(Max('tth_end'))['tth_end__max']
        if tth:
            aircraft.tth = tth
        else:
            aircraft.tth = 0

        aircraft.full_clean()
        aircraft.save()

    for pdt in PDT.objects.all():
        ms = pdt.aircraft.ms_report_set.order_by('done_date').last()
        pdt.ms_report = ms

        pdt.full_clean()
        pdt.save()

    return HttpResponseRedirect(reverse('camo:aircraft-list'))


def check_history(request):

    for pdt in PDT.objects.all():
        if pdt.date < datetime.date(2016,7,1) and pdt.status == 'checked':
            pdt.check_time = timezone.now()
            pdt.full_clean()
            pdt.save()

    return HttpResponseRedirect(reverse('camo:aircraft-list'))