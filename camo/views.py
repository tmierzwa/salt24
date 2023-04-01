from datetime import date
from django import forms
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.forms import Textarea, TextInput
from django.forms.models import modelform_factory
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import permission_required

from django.utils.decorators import method_decorator
def class_view_decorator(function_decorator):

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator

from camo.models import Aircraft, Part, ATA, Assignment
from camo.models import POT_group, POT_event, Work_order, Work_order_line
from camo.models import Modification, WB_report, MS_report
from camo.models import CAMO_operation

from fin.models import FuelTank, RemoteFueling, BalanceOperation
from sms.models import SMSFailure

from panel.models import PDT, Operation
from panel.views import fueling_save

from camo.forms import AircraftCreateForm, AircraftCloneForm
from camo.forms import AssignNewPartCreateForm
from camo.forms import AssignExistingPartCreateForm, AssignmentUpdateForm, AssignmentDeleteForm
from camo.forms import POTGroupCloneForm
from camo.forms import WorkOrderCreateForm, WorkOrderCloseForm, CRSCreateForm
from camo.forms import PartPurgeForm


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftList (ListView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Posortuj listę inicjalnie po typach
    def get_queryset(self):
        return Aircraft.objects.order_by('type')

    def get_context_data(self, **kwargs):
        # Informacje nagłówkowe
        context = super(AircraftList, self).get_context_data(**kwargs)
        context['page_title'] = 'Lista SP'
        context['header_text'] = 'Lista statków powietrznych'
        context['empty_text'] = 'Brak statków powietrznych.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowy statek powietrzny', 'path': reverse("camo:aircraft-create")})
        local_menu.append({'text': 'Sklonuj statek powietrzny', 'path': reverse("camo:aircraft-clone")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Rejestracja'})
        header_list.append({'header': 'Typ'})
        header_list.append({'header': 'Status\nobsługi'})
        header_list.append({'header': 'Miesięcy'})
        header_list.append({'header': 'TTH'})
        header_list.append({'header': 'Lądowań'})
        header_list.append({'header': 'Cykli'})
        header_list.append({'header': 'Licznik'})
        header_list.append({'header': 'Status\nużytkowania'})
        header_list.append({'header': 'Ważność\nubezp.'})
        header_list.append({'header': 'Ważność\nW&B'})
        header_list.append({'header': 'Ważność\nARC'})
        header_list.append({'header': 'Ważność\nradia'})
        header_list.append({'header': 'ARC'})
        header_list.append({'header': 'MS'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'registration', 'value': object, 'link': reverse('camo:aircraft-info', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'type', 'value': object.type})
            if object.airworthy():
                fields.append({'name': 'ms_ok', 'value': 'Dopuszczony', 'just': 'center'})
            else:
                fields.append({'name': 'ms_ok', 'value': 'Nie dopuszczony', 'color': 'lightcoral', 'just': 'center'})
            fields.append({'name': 'months', 'value': object.months_count, 'just': 'center'})
            fields.append({'name': 'tth', 'value': object.hours_count, 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings_count, 'just': 'center'})
            fields.append({'name': 'cycles', 'value': (object.cycles_count if object.use_cycles else '---'), 'just': 'center'})
            fields.append({'name': 'tth', 'value': object.tth, 'just': 'center'})
            fields.append({'name': 'status', 'value': object.status_str(), 'color': ('lightcoral' if object.status == 'damaged' else 'auto'), 'just': 'center'})
            fields.append({'name': 'ins_date', 'value': object.insurance_date, 'color': ('auto' if object.ins_date_ok() else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'wb_date', 'value': object.wb_date, 'color': ('auto' if object.wb_date_ok() else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'arc_date', 'value': object.arc_date, 'color': ('auto' if object.arc_date_ok() else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'radio_date', 'value': object.radio_date, 'color': ('auto' if object.radio_date_ok() else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'arc', 'report_link': reverse('camo:aircraft-arc', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'ms', 'report_link': reverse('camo:aircraft-ms', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:aircraft-update', args=[object.pk]),
                           'delete_link': (reverse('camo:aircraft-delete', args=[object.pk]) if not object.assignment_set.filter(current=True) else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftInfo (DetailView):
    model = Aircraft
    template_name = 'camo/details_template.html'

    # Kontekst dla ekranu informacji o SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftInfo, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o statku powietrznym'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:aircraft-update', args=[self.object.pk])})
        # Jeśli nie ma przypisanych części to można usunąć
        if not self.object.assignment_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('camo:aircraft-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Rejestracja', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Typ SP', 'value': self.object.type})
        field_list.append({'header': 'Śmigłowiec', 'value': 'TAK' if self.object.helicopter else 'NIE'})
        if self.object.remarks:
            field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        field_list.append({'header': 'MTOW', 'value': '%d kg' % self.object.mtow})
        field_list.append({'header': 'Data produkcji', 'value': self.object.production_date})
        field_list.append({'header': 'Wiek w miesiącach', 'value': self.object.months_count})
        field_list.append({'header': 'Stan licznika', 'value': self.object.tth})
        field_list.append({'header': 'Suma TTH', 'value': self.object.hours_count})
        field_list.append({'header': 'Suma lądowań', 'value': self.object.landings_count})
        if self.object.use_cycles:
            field_list.append({'header': 'Suma cykli', 'value': self.object.cycles_count})
        field_list.append({'header': 'Data ważności ubezp.', 'value': self.object.insurance_date})
        field_list.append({'header': 'Data ważności W&B', 'value': self.object.wb_date})
        field_list.append({'header': 'Data ważności ARC', 'value': self.object.arc_date})
        field_list.append({'header': 'Data ważności radia', 'value': self.object.radio_date})
        field_list.append({'header': 'Status', 'value': self.object.status_str()})
        field_list.append({'header': 'Podlega rezerwacjom', 'value': 'TAK' if self.object.scheduled else 'NIE'})
        context['field_list'] = field_list

        context['type'] = 'info'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftParts (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu najbliższych obsług SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftParts, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista zabudowanych części'
        context['empty_text'] = 'Brak zabudowanych części.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Zabuduj nową część', 'path': reverse("camo:assign-new-part-create", args=[self.object.pk])})
        local_menu.append({'text': 'Zabuduj istniejącą część', 'path': reverse("camo:assign-existing-part-create", args=[self.object.pk])})
        local_menu.append({'text': 'Raport części', 'path': reverse("camo:report-parts", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Lp.'})
        header_list.append({'header': 'Sekcja ATA'})
        header_list.append({'header': 'Część'})
        header_list.append({'header': 'Opis'})
        header_list.append({'header': 'Msc.'})
        header_list.append({'header': 'TTH'})
        if self.object.use_landings:
            header_list.append({'header': 'Ldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Cycl.'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Utwórz listę aktualnych przypisań
        assignments = self.object.assignment_set.filter(current=True).order_by('ata__chapter')
        assignment_list = []
        ind = 0
        for assignment in assignments:
            if not assignment.super_ass:
                ind = ind + 1
                if Assignment.objects.filter(super_ass=assignment):
                    deletable = False
                else:
                    deletable = True
                assignment_list.append((assignment, deletable, "%d" % ind))
                sub = 0
                for child in assignments:
                    if child.super_ass == assignment:
                        sub = sub + 1
                        assignment_list.append((child, True, '%d.%02d' % (ind, sub)))

        # Zawartość tabeli
        row_list = []
        for object, deletable, index in assignment_list:
            fields = []
            fields.append({'name': 'index', 'value': index})
            fields.append({'name': 'ata', 'value': object.ata})
            fields.append({'name': 'part', 'value': ('└─ ' if object.super_ass else '') + object.part.__str__(), 'link': reverse('camo:part-info', args=[object.part.pk])})
            fields.append({'name': 'description', 'value': object.description})
            fields.append({'name': 'months_count', 'value': object.part.months_count, 'just': 'center'})
            fields.append({'name': 'hours_count', 'value': object.part.hours_count, 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'landings_count', 'value': object.part.landings_count, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'cycles_count', 'value': object.part.cycles_count, 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:assign-part-update', args=[object.pk]),
                           'delete_link': (reverse('camo:assign-part-delete', args=[object.pk]) if deletable else None)})

            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'parts'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftPOTs (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu najbliższych obsług SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftPOTs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Najbliższe planowe obsługi wg. POT'
        context['empty_text'] = 'Brak zdefiniowanych obsług.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Utwórz listę przypisanych grup czynności
        groups = []
        for part in self.object.components():
            for group in part.pot_group_set.all():
                if group.leftx() != 99999 and group.applies:
                    groups.append(group)

        # Posortuj po ilości pozostałych godzin
        groups = sorted(groups, key=lambda group: group.leftx())

        # Lokalne menu
        local_menu = []
        if groups:
            local_menu.append({'text': 'Wystaw nowe zlecenie', 'path': reverse("camo:order-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Paczka czynności'})
        header_list.append({'header': 'Wykon.\ndnia'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings:
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Wykon.\ncykli'})
        header_list.append({'header': 'Pozost.\nFH'})
        header_list.append({'header': 'Pozost.\ndni'})
        if self.object.use_landings:
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Pozost.\ncykli'})
        header_list.append({'header': 'Nast.\nTTH'})
        header_list.append({'header': 'Nast.\ndata'})
        if self.object.use_landings:
            header_list.append({'header': 'Nast.\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Nast.\ncykli'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'pot', 'value': object.POT_ref, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'group', 'value': object.name})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'done_ldg', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'done_cycl', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'left_ldg', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'left_cycl', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'next_hours', 'value': object.next_hours(), 'color': ('auto' if (object.left_hours() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            fields.append({'name': 'next_days', 'value': object.next_date(), 'color': ('auto' if (object.left_days() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'next_ldg', 'value': object.next_landings(), 'color': ('auto' if (object.left_landings() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'next_cycl', 'value': object.next_cycles(), 'color': ('auto' if (object.left_cycles() or 1) > 0 else 'lightcoral'), 'just': 'center'})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'pots'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftOrders (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu zleceń obsługowych dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftOrders, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista zleceń obsługowych'
        context['empty_text'] = 'Brak zleceń obsługowych.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Utwórz listę przypisanych grup czynności
        groups = []
        for part in self.object.components():
            for group in part.pot_group_set.all():
                groups.append(group)

        # Lokalne menu
        local_menu = []
        if groups:
            local_menu.append({'text': 'Wystaw nowe zlecenie', 'path': reverse("camo:order-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer'})
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'ASO'})
        header_list.append({'header': 'Status'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Wybierz aktywne zlecenia dla SP
        orders = self.object.work_order_set.order_by('-open', '-date')

        # Zawartość tabeli
        row_list = []
        for object in orders:
            fields = []
            fields.append({'name': 'number', 'value': object.number, 'link': reverse('camo:order-details', args=[object.pk])})
            fields.append({'name': 'date', 'value': object.date, 'just': 'center'})
            fields.append({'name': 'aso', 'value': object.aso})
            fields.append({'name': 'aso', 'value': ('Otwarte' if object.open else 'Zamknięte'), 'just': 'center'})
            fields.append({'name': 'change', 'delete_link': (reverse('camo:order-close', args=[object.pk]) if object.open else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'orders'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftOpers (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu zleceń obsługowych dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftOpers, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista wykonanych operacji'
        context['empty_text'] = 'Brak zarejestrowanych operacji.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Rejestracja nowej operacji', 'path': reverse("camo:oper-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer PDT'})
        header_list.append({'header': 'Data\noperacji'})
        header_list.append({'header': 'Licznik\npoczątkowy'})
        header_list.append({'header': 'Licznik\nkońcowy'})
        header_list.append({'header': 'Czas\nlotu'})
        header_list.append({'header': 'Liczba\nlądowań'})
        if self.object.use_cycles:
            header_list.append({'header': 'Liczba\ncykli'})
        header_list.append({'header': 'Suma\nTTH'})
        header_list.append({'header': 'Suma\nlądowań'})
        if self.object.use_cycles:
            header_list.append({'header': 'Suma\ncykli'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz operacje wykonane na SP
        opers = self.object.camo_operation_set.order_by('-tth_end')
        opers_list = []
        sum_tth = self.object.hours_count
        sum_landings = self.object.landings_count
        sum_cycles = self.object.cycles_count
        for oper in opers:
            opers_list.append((oper, sum_tth, sum_landings, sum_cycles))
            sum_tth -= oper.tth_end - oper.tth_start
            sum_landings -= oper.landings
            sum_cycles -= oper.cycles

        # Zawartość tabeli
        row_list = []
        for object, sum_tth, sum_landings, sum_cycles in opers_list:
            fields = []
            if object.pdt:
                fields.append({'name': 'pdt_ref', 'value': "%06d" % object.pdt.pdt_ref, 'link': reverse('panel:pdt-info', args=[object.pdt.pk]), 'just': 'center'})
            else:
                fields.append({'name': 'pdt_ref', 'value': object.pdt_ref, 'just': 'center'})
            fields.append({'name': 'date', 'value': object.date, 'link': reverse('camo:oper-details', args=[object.pk])})
            fields.append({'name': 'tth_start', 'value': object.tth_start, 'just': 'center'})
            fields.append({'name': 'tth_end', 'value': object.tth_end, 'just': 'center'})
            fields.append({'name': 'tth', 'value': object.tth_end - object.tth_start, 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'cycles', 'value': object.cycles, 'just': 'center'})
            fields.append({'name': 'sum_tth', 'value': sum_tth, 'just': 'center'})
            fields.append({'name': 'sum_landings', 'value': sum_landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'sum_cycles', 'value': sum_cycles, 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('camo:oper-update', args=[object.pk]), 'delete_link': reverse('camo:oper-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'opers'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftMods (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu modyfikacji i napraw dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftMods, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista modyfikacji i napraw'
        context['empty_text'] = 'Brak modyfikacji i napraw.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Nowa modyfikacja lub naprawa', 'path': reverse("camo:modification-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Opis'})
        header_list.append({'header': 'Wykon.\ndata'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings:
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'Organizacja'})
        header_list.append({'header': 'CRS Ref.'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz modyfikacje dla SP
        mods = self.object.modification_set.order_by('-done_date')

        # Zawartość tabeli
        row_list = []
        for object in mods:
            fields = []
            fields.append({'name': 'description', 'value': object.description, 'link': reverse('camo:modification-details', args=[object.pk])})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'aso', 'value': object.aso})
            fields.append({'name': 'done_crs', 'value': object.done_crs})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('camo:modification-update', args=[object.pk]),
                           'delete_link': reverse('camo:modification-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'mods'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftWBs (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu ważeń dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftWBs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista raportów W&B'
        context['empty_text'] = 'Brak raportów W&B.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Nowy raport W&B', 'path': reverse("camo:wb-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Opis'})
        header_list.append({'header': 'Doc ref.'})
        header_list.append({'header': 'Zmiana\nmasy'})
        header_list.append({'header': 'Zmiana\ncałkowita'})
        header_list.append({'header': 'Zmiana\nproc.'})
        header_list.append({'header': 'Masa\npustego'})
        header_list.append({'header': 'Lon\nC.G.'})
        header_list.append({'header': 'Lat\nC.G.'})
        header_list.append({'header': 'Lon\nmoment'})
        header_list.append({'header': 'Lat\nmoment'})
        header_list.append({'header': 'Wykon.\ndata'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings:
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'Dokument'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz raporty W%B dla SP
        wbs = self.object.wb_report_set.order_by('done_date').values()
        mc = 0
        for wb in wbs:
            mc += wb['mass_change']
            wb['tot_mass_change'] = mc
            if self.object.mtow != 0:
                wb['pct_mass_change'] = 100 * (mc / self.object.mtow)
            else:
                wb['pct_mass_change'] = None

        # Zawartość tabeli
        row_list = []
        for wb in wbs:

            # Wybór właściwych jednostek
            if wb['unit'] == 'USA':
                mas_u, len_u, mom_u = 'lb', 'in', 'lb*in'
            else:
                mas_u, len_u, mom_u = 'kg', 'm', 'kg*m'

            fields = []
            fields.append({'name': 'description', 'value': wb['description'], 'link': reverse('camo:wb-details', args=[wb['id']])})
            fields.append({'name': 'doc_ref', 'value': wb['doc_ref']})
            fields.append({'name': 'change', 'value': '%.2f %s' % (wb['mass_change'], mas_u), 'just': 'center'})
            fields.append({'name': 'tot_change', 'value': '%.2f %s' % (wb['tot_mass_change'], mas_u), 'just': 'center'})
            fields.append({'name': 'pct_change', 'value': '%.2f %%' % wb['pct_mass_change'], 'just': 'center'})
            fields.append({'name': 'empty_weight', 'value': '%.2f %s' % (wb['empty_weight'], mas_u), 'just': 'center'})
            fields.append({'name': 'lon_cg', 'value': ("%.2f %s" % (wb['lon_cg'], len_u) if wb['lon_cg'] else None), 'just': 'center'})
            fields.append({'name': 'lat_cg', 'value': ("%.2f %s" % (wb['lat_cg'], len_u) if wb['lat_cg'] else None), 'just': 'center'})
            fields.append({'name': 'lon_moment', 'value': ("%.2f %s" % (wb['empty_weight']*wb['lon_cg'], mom_u) if wb['lon_cg'] else None), 'just': 'center'})
            fields.append({'name': 'lat_moment', 'value': ("%.2f %s" % (wb['empty_weight']*wb['lat_cg'], mom_u) if wb['lat_cg'] else None), 'just': 'center'})
            fields.append({'name': 'done_date', 'value': wb['done_date'], 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': wb['done_hours'], 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'done_landings', 'value': wb['done_landings'], 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'done_cycles', 'value': wb['done_cycles'], 'just': 'center'})
            fields.append({'name': 'done_doc', 'value': wb['done_doc']})
            fields.append({'name': 'change', 'edit_link': reverse('camo:wb-update', args=[wb['id']]),
                           'delete_link': reverse('camo:wb-delete', args=[wb['id']])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'wbs'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftStatements (DetailView):
    model = Aircraft
    template_name = 'camo/list_template.html'

    # Kontekst dla ekranu ważeń dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftStatements, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Lista świadectw MS'
        context['empty_text'] = 'Brak świadectw MS.'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Nowe świadectwo MS', 'path': reverse("camo:ms-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer\nMS'})
        header_list.append({'header': 'Data\nMS'})
        header_list.append({'header': 'Przy\nnalocie'})
        if self.object.use_landings:
            header_list.append({'header': 'Liczba\nlądowań'})
        if self.object.use_cycles:
            header_list.append({'header': 'Liczba\ncykli'})
        header_list.append({'header': 'Ważny do\ndata'})
        header_list.append({'header': 'Ważny do\nTTH'})
        if self.object.use_landings:
            header_list.append({'header': 'Ważny do\nldg.'})
        if self.object.use_cycles:
            header_list.append({'header': 'Ważny do\ncycl.'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz raporty MS dla SP
        mss = self.object.ms_report_set.order_by('done_date')

        # Zawartość tabeli
        row_list = []
        for object in mss:
            fields = []
            fields.append({'name': 'ms_ref', 'value': object.ms_ref, 'link': reverse('camo:ms-details', args=[object.pk])})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'next_date', 'value': object.next_date, 'just': 'center'})
            fields.append({'name': 'next_hours', 'value': object.next_hours, 'just': 'center'})
            if self.object.use_landings:
                fields.append({'name': 'next_landings', 'value': object.next_landings, 'just': 'center'})
            if self.object.use_cycles:
                fields.append({'name': 'next_cycles', 'value': object.next_cycles, 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('camo:ms-update', args=[object.pk]),
                           'delete_link': reverse('camo:ms-delete', args=[object.pk])})
            row_list.append({'fields': fields})

        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'ms'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftARC (DetailView):
    model = Aircraft
    template_name = 'camo/aircraft_arc.html'

    # Kontekst dla raportu ARC dla SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftARC, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Otwórz jako PDF', 'path': reverse("camo:report-arc", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Wybierz informacje do raportu ARC dla SP
        groups = []
        for part in self.object.components():
            for group in part.pot_group_set.all():
                groups.append(group)

        # Posortuj po ilości pozostałych godzin/dni
        # groups = sorted(groups, key=lambda group: group.leftx())

        context['oth_list'] = [group for group in groups if group.type=='oth']
        context['llp_list'] = [group for group in groups if group.type=='llp']
        context['ovh_list'] = [group for group in groups if group.type=='ovh']

        # context['adsb_ac_list'] = [group for group in groups if group.type in ['ad','sb'] and
        #                                                         group.part == self.object.airframe()]
        # context['adsb_en_list'] = [group for group in groups if group.type in ['ad', 'sb'] and
        #                                                         group.part in self.object.engines()]
        # context['adsb_pr_list'] = [group for group in groups if group.type in ['ad', 'sb'] and
        #                                                         group.part in self.object.propellers()]

        # Utwórz listę części
        assignments = self.object.assignment_set.filter(current=True).order_by('ata__chapter')
        part_list = []
        ind = 0
        for assignment in assignments:
            if not assignment.super_ass:
                ind = ind + 1
                part_list.append([assignment.part, "%d" % ind])
                sub = 0
                for child in assignments:
                    if child.super_ass == assignment:
                        sub = sub + 1
                        part_list.append([child.part, '%d.%02d' % (ind, sub)])

        # Przpisz do części dyrektywy i biuletyny
        for part in part_list:
            part.append([group for group in groups if group.part==part[0] and group.type in ('ad', 'sb')])

        context['part_list'] = [part for part in part_list if part[2] != []]

        mods = self.object.modification_set.order_by('-done_date')
        context['mods_list'] = mods

        wbs = self.object.wb_report_set.order_by('done_date').values()
        mc = 0
        for wb in wbs:
            mc += wb['mass_change']
            wb['tot_mass_change'] = mc
            if self.object.mtow != 0:
                wb['pct_mass_change'] = 100 * (mc / self.object.mtow)
            else:
                wb['pct_mass_change'] = None
            if wb['lon_cg']:
                wb['lon_moment'] = wb['empty_weight']*wb['lon_cg']
            if wb['lat_cg']:
                wb['lat_moment'] = wb['empty_weight']*wb['lat_cg']
        context['wbs_list'] = wbs

        # Informacja, które liczniki powunny być użyte
        context['use_landings'] = self.object.use_landings
        context['use_cycles'] = self.object.use_cycles

        # Pozycja w bocznym menu
        context['type'] = 'arc'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftFuel (DetailView):
    model = Aircraft
    template_name = 'camo/details_template.html'

    # Kontekst dla ekranu informacji o SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftFuel, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o paliwie'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:aircraft-fuel-update', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Rodzaj paliwa', 'value': self.object.fuel_type})
        field_list.append({'header': 'Objętość zbiornika', 'value': '%d L' % self.object.fuel_capacity})
        field_list.append({'header': 'Zużycie paliwa', 'value': '%d L/h' % self.object.fuel_consumption})
        field_list.append({'header': 'Zatankowane paliwo', 'value': '%d L' % self.object.fuel_volume})
        context['field_list'] = field_list

        context['type'] = 'fuel'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class AircraftMsg (DetailView):
    model = Aircraft
    template_name = 'camo/details_template.html'

    # Kontekst dla ekranu informacji o SP #
    def get_context_data(self, **kwargs):
        context = super(AircraftMsg, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje dla pilotów'
        context['submenu_template'] = 'camo/aircraft_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:aircraft-msg-update', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Informacja', 'value': self.object.info if self.object.info else '-- brak --'})
        context['field_list'] = field_list

        context['type'] = 'msg'

        return context


@permission_required('camo.camo_admin')
def AircraftCreate (request):

    def ComponentCreate(part_data):
        # Utworzenie cześci #
        part = Part(maker = part_data['maker'],
                    part_no = part_data['part_no'],
                    serial_no = part_data['serial_no'],
                    f1 = part_data['f1'],
                    name = part_data['name'],
                    lifecycle = part_data['lifecycle'],
                    production_date = part_data['production_date'],
                    install_date = part_data['install_date'],
                    hours_count = part_data['hours_count'],
                    landings_count = part_data['landings_count'],
                    cycles_count = part_data['cycles_count'])
        part.full_clean()
        part.save()

        # Utworzenie przypisania #
        assignment = Assignment(aircraft = aircraft,
                                part = part,
                                ata = get_object_or_404(ATA, pk=part_data['ata']),
                                super_ass = None,
                                description = None,
                                crs = None,
                                from_date = part_data['install_date'],
                                from_hours = 0, from_landings = 0, from_cycles=0,
                                to_date = None, to_hours = None, to_landings = None, to_cycles=None,
                                current = True)
        assignment.full_clean()
        assignment.save()

        # Utworzenie obsługi #
        if part.lifecycle in ['llp', 'ovh'] and (part_data['due_hours'] or part_data['due_months'] or
                                                 part_data['due_landings'] or part_data['due_cycles']):
            pot_group = POT_group(part = part,
                                  adsb_no = None, adsb_date = None, adsb_agency = None,
                                  type=part.lifecycle,
                                  due_hours = part_data['due_hours'],
                                  due_months = part_data['due_months'],
                                  due_landings = part_data['due_landings'],
                                  due_cycles = part_data['due_cycles'],
                                  parked = False, count_type = 'production',
                                  optional = False,
                                  done_crs = None, done_date = None, done_hours = None,
                                  done_landings = None, done_cycles=None, done_aso = None,
                                  remarks = 'Czynność utworzona automatycznie')

            if part.lifecycle == 'llp':
                pot_group.POT_ref = '%s.UM' % part.part_no
                pot_group.name = 'Planowy demontaż %s' % part.name
                pot_group.cyclic = False
            else:
                pot_group.POT_ref = '%s.OVH' % part.part_no
                pot_group.name = 'Remont %s' % part.part_no
                pot_group.cyclic = True

            pot_group.full_clean()
            pot_group.save()

        return assignment

    context = {}
    prefixes = ['af', 'e1', 'e2', 'p1', 'p2']
    context['prefixes'] = prefixes
    context['airframe'] = [('af', 'Płatowiec')]
    context['lh'] = [('e1', 'Silnik LH'), ('p1', 'Śmigło/Wirnik LH')]
    context['rh'] = [('e2', 'Silnik RH'), ('p2', 'Śmigło/Wirnik RH')]
    form = AircraftCreateForm(request.POST or None)
    context['form'] = form
    if form.is_valid():
        # Utworznenie nowego statku powietrznego #
        aircraft = Aircraft(type = form.cleaned_data['af_part_no'],
                            registration = form.cleaned_data['registration'],
                            status = form.cleaned_data['status'],
                            mtow = form.cleaned_data['mtow'],
                            production_date = form.cleaned_data['af_production_date'],
                            insurance_date = form.cleaned_data['insurance_date'],
                            wb_date = form.cleaned_data['wb_date'],
                            arc_date = form.cleaned_data['arc_date'],
                            radio_date = form.cleaned_data['radio_date'],
                            hours_count = form.cleaned_data['af_hours_count'],
                            landings_count = form.cleaned_data['af_landings_count'],
                            cycles_count = form.cleaned_data['af_cycles_count'],
                            use_landings = form.cleaned_data['use_landings'],
                            use_cycles = form.cleaned_data['use_cycles'],
                            tth = form.cleaned_data['tth'],
                            last_pdt_ref = form.cleaned_data['last_pdt_ref'],
                            fuel_type=form.cleaned_data['fuel_type'],
                            fuel_capacity=form.cleaned_data['fuel_capacity'],
                            fuel_consumption=form.cleaned_data['fuel_consumption'])
        aircraft.full_clean()
        aircraft.save()

        # Utworzenie poszczególnych komponentów #
        for prefix in prefixes:
            part_data = {}
            part_data['name'] = form.cleaned_data['%s_name' % prefix]
            part_data['maker'] = form.cleaned_data['%s_maker' % prefix]
            part_data['part_no'] = form.cleaned_data['%s_part_no' % prefix]
            part_data['serial_no'] = form.cleaned_data['%s_serial_no' % prefix]
            part_data['f1'] = form.cleaned_data['%s_f1' % prefix]
            part_data['ata'] = form.cleaned_data['%s_ata' % prefix]
            part_data['lifecycle'] = form.cleaned_data['%s_lifecycle' % prefix]
            part_data['due_hours'] = form.cleaned_data['%s_due_hours' % prefix]
            part_data['due_months'] = form.cleaned_data['%s_due_months' % prefix]
            part_data['due_landings'] = form.cleaned_data['%s_due_landings' % prefix]
            part_data['due_cycles'] = form.cleaned_data['%s_due_cycles' % prefix]
            part_data['production_date'] = form.cleaned_data['%s_production_date' % prefix] or form.cleaned_data['af_production_date']
            if prefix == 'af':
                part_data['install_date'] = form.cleaned_data['af_production_date']
            else:
                part_data['install_date'] = form.cleaned_data['%s_install_date' % prefix] or form.cleaned_data['af_production_date']
            part_data['hours_count'] = form.cleaned_data['%s_hours_count' % prefix] or 0
            part_data['landings_count'] = form.cleaned_data['%s_landings_count' % prefix] or 0
            part_data['cycles_count'] = form.cleaned_data['%s_cycles_count' % prefix] or 0
            if part_data['name'] and part_data['maker'] and part_data['part_no'] and part_data['serial_no']:
                ComponentCreate(part_data)

        return HttpResponseRedirect(reverse('camo:aircraft-info', args=[aircraft.pk]))
    return render(request, 'camo/aircraft_create.html', context)


@permission_required('camo.camo_admin')
def AircraftClone(request):

    def AssignmentClone(component, super_ass):
        # Sklonowanie cześci #
        part = Part(maker = component.part.maker,
                    part_no = component.part.part_no or '---',
                    serial_no = '---',
                    f1 = '---',
                    name = component.part.name,
                    lifecycle = component.part.lifecycle,
                    production_date = form.cleaned_data['production_date'],
                    install_date = form.cleaned_data['production_date'],
                    hours_count = 0,
                    landings_count = 0,
                    cycles_count = 0)
        part.full_clean()
        part.save()

        # Sklonowanie grup obsługowych #
        for group in component.part.pot_group_set.all():
            pot_group = POT_group(part = part,
                                  POT_ref = group.POT_ref,
                                  adsb_no = group.adsb_no,
                                  adsb_date = group.adsb_date,
                                  adsb_agency = group.adsb_agency,
                                  name = group.name,
                                  type = group.type,
                                  due_hours = group.due_hours,
                                  due_months = group.due_months,
                                  due_landings = group.due_landings,
                                  due_cycles = group.due_cycles,
                                  cyclic = group.cyclic,
                                  parked = group.parked,
                                  count_type = group.count_type,
                                  optional = group.optional,
                                  done_crs = None, done_date = None, done_hours = None,
                                  done_landings = None, done_cycles = None, done_aso = None, remarks = None)
            pot_group.full_clean()
            pot_group.save()

            # Sklonowanie czynności obsługowych #
            for event in group.pot_event_set.all():
                pot_event = POT_event(POT_group = pot_group,
                                      POT_ref = event.POT_ref,
                                      name = event.name,
                                      done_crs = None, done_date = None,
                                      done_hours = None, done_landings = None, done_cycles = None)
                pot_event.full_clean()
                pot_event.save()

        # Sklonowanie przypisania #
        assignment = Assignment(aircraft = aircraft,
                                part = part,
                                ata = component.ata,
                                super_ass = super_ass,
                                description = component.description,
                                crs = None,
                                from_date = form.cleaned_data['production_date'],
                                from_hours = 0, from_landings = 0, from_cycles = 0,
                                to_date = None, to_hours = None, to_landings = None, to_cycles = None,
                                current = True)
        assignment.full_clean()
        assignment.save()
        return assignment

    context = {}
    form = AircraftCloneForm(request.POST or None)
    context['form']=form
    if form.is_valid():
        source = get_object_or_404(Aircraft, pk=form.cleaned_data['source'])
        # Utworznenie nowego statku powietrznego #
        aircraft = Aircraft(type = source.type,
                            registration = form.cleaned_data['registration'],
                            helicopter = source.helicopter,
                            status = 'flying',
                            mtow = source.mtow,
                            production_date = form.cleaned_data['production_date'],
                            insurance_date = None,
                            wb_date = None,
                            arc_date = None,
                            radio_date = None,
                            hours_count = 0,
                            landings_count = 0,
                            cycles_count = 0,
                            tth = 0,
                            last_pdt_ref = 0,
                            fuel_type=source.fuel_type,
                            fuel_capacity=source.fuel_capacity,
                            fuel_consumption=source.fuel_consumption,
                            fuel_volume=0,
                            use_landings = source.use_landings,
                            use_cycles = source.use_cycles,
                            rent_price=0)
        aircraft.full_clean()
        aircraft.save()
        # Sklonowanie poszczegónych przypisań #
        for component in source.configuration():
            if not component.super_ass:
                new_super = AssignmentClone(component, None)
                for child in source.configuration():
                    if child.super_ass == component:
                        AssignmentClone(child, new_super)

        return HttpResponseRedirect(reverse('camo:aircraft-info', args=[aircraft.pk]))

    return render(request, 'camo/aircraft_clone.html', context)


@class_view_decorator(permission_required('camo.camo_admin'))
class AircraftUpdate (UpdateView):
    model = Aircraft
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(AircraftUpdate, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Zmiana danych statku powietrznego'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['type'] = 'info'

        return context

    def get_form_class(self, **kwargs):
        return modelform_factory(Aircraft, fields=('type', 'registration', 'helicopter', 'mtow', 'status', 'production_date',
                                                   'insurance_date', 'wb_date', 'arc_date', 'radio_date', 'tth',
                                                   'hours_count', 'landings_count', 'last_pdt_ref', 'use_landings', 'cycles_count',
                                                   'use_cycles', 'scheduled', 'remarks'),
                                          widgets={'production_date':AdminDateWidget(),
                                                   'insurance_date':AdminDateWidget(),
                                                   'wb_date':AdminDateWidget(),
                                                   'arc_date':AdminDateWidget(),
                                                   'radio_date':AdminDateWidget(),
                                                   'remarks':Textarea(attrs={'rows':3, 'cols':100})})

    def get_success_url(self):
        return reverse('camo:aircraft-info', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class AircraftFuelUpdate (UpdateView):
    model = Aircraft
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(AircraftFuelUpdate, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Zmiana informacji o paliwie'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['type'] = 'fuel'

        return context

    def get_form_class(self, **kwargs):
        return modelform_factory(Aircraft, fields=('fuel_type', 'fuel_capacity', 'fuel_consumption', 'fuel_volume'))

    def get_success_url(self):
        return reverse('camo:aircraft-fuel', args=[self.object.pk])\


@class_view_decorator(permission_required('camo.camo_admin'))
class AircraftMsgUpdate (UpdateView):
    model = Aircraft
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(AircraftMsgUpdate, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Zmiana informacji dla pilotów'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['type'] = 'msg'

        return context

    def get_form_class(self, **kwargs):
        return modelform_factory(Aircraft, fields=['info'], widgets={'info':Textarea(attrs={'rows':3, 'cols':100})})

    def get_success_url(self):
        return reverse('camo:aircraft-msg', args=[self.object.pk])\


@class_view_decorator(permission_required('camo.camo_admin'))
class AircraftDelete (DeleteView):
    model = Aircraft
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(AircraftDelete, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Usunięcie statku powietrznego'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['type'] = 'info'

        return context

    def get_success_url(self):
        return reverse('camo:aircraft-list')


@permission_required('camo.camo_admin')
def AssignExistingPartCreate (request, aircraft_id):
    context = {}
    aircraft = get_object_or_404(Aircraft, pk=aircraft_id)
    context['object'] = aircraft
    context['type'] = 'parts'

    spare_parts = []
    for part in Part.objects.all():
        if not part.assignment_set.filter(current = True):
            spare_parts.append(part)
    context['spare_parts'] = spare_parts
    mounted_parts = aircraft.assignment_set.filter(current=True, super_ass=None)
    form = AssignExistingPartCreateForm(request.POST or None, spare_parts=spare_parts, mounted_parts=mounted_parts,
                                        use_landings=aircraft.use_landings, use_cycles=aircraft.use_cycles,
                                        initial={'from_date': date.today(),
                                                 'from_hours': aircraft.hours_count,
                                                 'from_landings': aircraft.landings_count,
                                                 'from_cycles': aircraft.cycles_count})
    context['form'] = form

    if form.is_valid():
        if form.cleaned_data['super_part'] != '':
            super_ass = get_object_or_404(Assignment, pk=form.cleaned_data['super_part'])
        else:
            super_ass = None
        assignment = Assignment(aircraft=aircraft,
                                part=get_object_or_404(Part, pk=form.cleaned_data['part']),
                                ata=get_object_or_404(ATA, pk=form.cleaned_data['ata']),
                                super_ass=super_ass,
                                description=form.cleaned_data['description'],
                                from_date=form.cleaned_data['from_date'],
                                from_hours=form.cleaned_data['from_hours'],
                                from_landings=form.cleaned_data['from_landings'],
                                from_cycles=form.cleaned_data['from_cycles'],
                                crs=form.cleaned_data['crs'],
                                current=True)
        assignment.full_clean()
        assignment.save()
        return HttpResponseRedirect(reverse('camo:aircraft-parts', args=[aircraft_id]))
    return render(request, 'camo/assign_existing_part.html', context)


@permission_required('camo.camo_admin')
def AssignNewPartCreate (request, aircraft_id):
    context = {}
    aircraft = get_object_or_404(Aircraft, pk=aircraft_id)
    context['object'] = aircraft
    context['type'] = 'parts'
    mounted_parts = aircraft.assignment_set.filter(current=True, super_ass=None)
    form = AssignNewPartCreateForm(request.POST or None, mounted_parts=mounted_parts, use_landings=aircraft.use_landings, use_cycles=aircraft.use_cycles,
                                   initial={'from_date': date.today(),
                                            'from_hours': aircraft.hours_count,
                                            'from_landings': aircraft.landings_count,
                                            'from_cycles': aircraft.cycles_count})
    context['form'] = form
    if form.is_valid():
        # Utworzenie cześci #
        part = Part(maker = form.cleaned_data['maker'],
                    part_no = form.cleaned_data['part_no'],
                    serial_no = form.cleaned_data['serial_no'],
                    f1 = form.cleaned_data['f1'],
                    name = form.cleaned_data['name'],
                    lifecycle = form.cleaned_data['lifecycle'],
                    production_date = form.cleaned_data['production_date'],
                    install_date = form.cleaned_data['install_date'],
                    hours_count = aircraft.hours_count - form.cleaned_data['from_hours'] + form.cleaned_data['hours_count'],
                    landings_count = aircraft.landings_count - form.cleaned_data['from_landings'] + form.cleaned_data['landings_count'],
                    cycles_count = aircraft.cycles_count - form.cleaned_data['from_cycles'] + form.cleaned_data['cycles_count'])
        part.full_clean()
        part.save()

        # Utworzenie przypisania #
        if form.cleaned_data['super_part'] != '':
            super_ass = get_object_or_404(Assignment, pk=form.cleaned_data['super_part'])
        else:
            super_ass = None

        assignment = Assignment(aircraft = aircraft,
                                part = part,
                                ata = get_object_or_404(ATA, pk=form.cleaned_data['ata']),
                                super_ass = super_ass,
                                description = form.cleaned_data['description'],
                                from_date = form.cleaned_data['from_date'],
                                from_hours = form.cleaned_data['from_hours'],
                                from_landings = form.cleaned_data['from_landings'],
                                from_cycles = form.cleaned_data['from_cycles'],
                                crs = form.cleaned_data['crs'],
                                current = True)
        assignment.full_clean()
        assignment.save()

        # Utworzenie obsługi #
        if part.lifecycle in ['llp', 'ovh'] and (form.cleaned_data['due_hours'] or form.cleaned_data['due_months']):
            pot_group = POT_group(part = part,
                                  adsb_no = None, adsb_date = None, adsb_agency = None,
                                  type = part.lifecycle,
                                  due_hours = form.cleaned_data['due_hours'],
                                  due_months = form.cleaned_data['due_months'],
                                  due_landings = form.cleaned_data['due_landings'],
                                  due_cycles = form.cleaned_data['due_cycles'],
                                  parked = False, count_type = 'production',
                                  optional = False,
                                  done_crs = None, done_date = None, done_hours = None,
                                  done_landings = None, done_cycles = None, done_aso = None,
                                  remarks = 'Czynność utworzona automatycznie')

            if part.lifecycle == 'llp':
                pot_group.POT_ref = '%s.UM' % part.part_no
                pot_group.name = 'Planowy demontaż %s' % part.name
                pot_group.cyclic = False
            else:
                pot_group.POT_ref = '%s.OVH' % part.part_no
                pot_group.name = 'Remont %s' % part.part_no
                pot_group.cyclic = True

            pot_group.full_clean()
            pot_group.save()

        return HttpResponseRedirect(reverse('camo:aircraft-parts', args=[aircraft_id]))
    return render(request, 'camo/assign_new_part.html', context)


@class_view_decorator(permission_required('camo.camo_reader'))
class PartList (ListView):
    model = Part
    template_name = 'camo/list_template.html'

    def get_queryset(self):
        spare_parts = []
        for part in Part.objects.all():
            if not part.assignment_set.filter(current = True):
                spare_parts.append(part)
        return spare_parts

    def get_context_data(self, **kwargs):
        # Informacje nagłówkowe
        context = super(PartList, self).get_context_data(**kwargs)
        context['page_title'] = 'Lista części'
        context['header_text'] = 'Lista części dostępnych w magazynie'
        context['empty_text'] = 'Brak części w magazynie.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową część', 'path': reverse("camo:part-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nazwa'})
        header_list.append({'header': 'Numer\nczęści'})
        header_list.append({'header': 'Numer\nseryjny'})
        header_list.append({'header': 'FORM-1'})
        header_list.append({'header': 'Cykl\nżycia'})
        header_list.append({'header': 'Godziny'})
        header_list.append({'header': 'Miesiące'})
        header_list.append({'header': 'Lądowania'})
        header_list.append({'header': 'Cykle'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'name', 'value': object.name, 'link': reverse('camo:part-info', args=[object.pk])})
            fields.append({'name': 'part_no', 'value': object.part_no})
            fields.append({'name': 'serial_no', 'value': object.serial_no})
            fields.append({'name': 'f1', 'value': object.f1})
            fields.append({'name': 'cycle', 'value': ('LLP' if object.lifecycle == 'llp' else ('OVH' if object.lifecycle == 'ovh' else '')), 'just': 'center'})
            fields.append({'name': 'tth', 'value': object.hours_count, 'just': 'center'})
            fields.append({'name': 'months', 'value': object.months_count, 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings_count, 'just': 'center'})
            fields.append({'name': 'cycles', 'value': object.cycles_count, 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:part-update', args=[object.pk]),
                           'delete_link': (reverse('camo:part-delete', args=[object.pk]) if not object.assignment_set.all() else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartInfo (DetailView):
    model = Part
    template_name = 'camo/details_template.html'

    # Kontekst dla ekranu informacji o części #
    def get_context_data(self, **kwargs):
        context = super(PartInfo, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o %s' % self.object
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:part-update', args=[self.object.pk])})
        # Jeśli nie ma przypisanych części to można usunąć
        if not self.object.assignment_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('camo:part-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Producent', 'value': self.object.maker, 'bold': True})
        field_list.append({'header': 'Nazwa', 'value': self.object.name, 'bold': True})
        field_list.append({'header': 'Numer części (Typ)', 'value': self.object.part_no})
        field_list.append({'header': 'Numer seryjny', 'value': self.object.serial_no})
        field_list.append({'header': 'FORM-1', 'value': self.object.f1})
        field_list.append({'header': 'Cykl życia', 'value': ('Ograniczona żywotność (LLP)' if self.object.lifecycle == 'llp' else
                                                            ('Podlegająca remontowi (OVH)' if self.object.lifecycle == 'ovh' else 'Według stanu'))})
        field_list.append({'header': 'Data produkcji', 'value': '%s (%d msc.)' % ((self.object.production_date or 'Brak'), self.object.months_count())})
        field_list.append({'header': 'Data instalacji', 'value': '%s (%d msc.)' % ((self.object.install_date or 'Brak'), self.object.months_inst_count())})
        field_list.append({'header': 'Nalot TTH', 'value': self.object.hours_count})
        if self.object.use_landings():
            field_list.append({'header': 'Liczba lądowań', 'value': self.object.landings_count})
        if self.object.use_cycles():
            field_list.append({'header': 'Liczba cykli', 'value': self.object.cycles_count})
        context['field_list'] = field_list

        context['type'] = 'info'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartHistory (DetailView):
    model = Part
    template_name = 'camo/part_history.html'

    # Kontekst dla ekranu informacji o części #
    def get_context_data(self, **kwargs):
        context = super(PartHistory, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Aktualny montaż %s' % self.object
        context['empty_text'] = 'Część znajduje się w magazynie.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Historia montażu części
        history = self.object.assignment_set.order_by('from_date')
        assignment = history.filter(current=True).last()
        has_children = (Assignment.objects.filter(super_ass=assignment).count() > 0)

        # Lokalne menu
        local_menu = []
        # Jeśli nie ma przypisanych części to można usunąć
        if assignment and not has_children:
            local_menu.append({'text': 'Zdemontuj', 'path': reverse('camo:assign-part-delete', args=[assignment.pk])})
        context['local_menu'] = local_menu

        # Jeśli część jest przypisana
        if assignment:
            field_list = []
            field_list.append({'header': 'Statek powietrzny', 'value': assignment.aircraft, 'link': reverse('camo:aircraft-parts', args=[assignment.aircraft.pk])})
            field_list.append({'header': 'Od daty', 'value': assignment.from_date})
            field_list.append({'header': 'Sekcja ATA', 'value': assignment.ata})
            field_list.append({'header': 'Dodatkowy opis', 'value': assignment.description})
            context['field_list'] = field_list

        context['header_width'] = '120px'

        # Informacje nagłówkowe dla podeskcji
        context['history_header_text'] = 'Historia montażu %s' % self.object
        context['history_empty_text'] = 'Część nie była dotąd montowana.'

        # Nagłówki tabeli w podsekcji
        header_list = []
        header_list.append({'header': 'SP'})
        header_list.append({'header': 'Data od'})
        header_list.append({'header': 'Data do'})
        header_list.append({'header': 'TTH od'})
        header_list.append({'header': 'TTH do'})
        if self.object.use_landings():
            header_list.append({'header': 'Ldg. od'})
            header_list.append({'header': 'Ldg. do'})
        if self.object.use_cycles():
            header_list.append({'header': 'Cycl. od'})
            header_list.append({'header': 'Cycl. do'})
        context['history_header_list'] = header_list

        # Zawartość tabeli w podsekcji
        row_list = []
        for object in history:
            fields = []
            fields.append({'name': 'aircrat', 'value': object.aircraft, 'link': reverse('camo:aircraft-parts', args=[object.aircraft.pk]), 'just': 'center'})
            fields.append({'name': 'from_date', 'value': object.from_date, 'just': 'center'})
            fields.append({'name': 'to_date', 'value': (object.to_date or 'aktualnie'), 'just': 'center'})
            fields.append({'name': 'from_tth', 'value': object.from_hours, 'just': 'center'})
            fields.append({'name': 'to_tth', 'value': (object.to_hours or 'aktualnie'), 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'from_landings', 'value': object.from_landings, 'just': 'center'})
                fields.append({'name': 'to_landings', 'value': (object.to_landings or 'aktualnie'), 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'from_cycles', 'value': object.from_cycles, 'just': 'center'})
                fields.append({'name': 'to_cycles', 'value': (object.to_cycles or 'aktualnie'), 'just': 'center'})
            row_list.append({'fields': fields})
        context['history_row_list'] = row_list

        context['type'] = 'history'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartPOTs (DetailView):
    model = Part
    template_name = 'camo/list_template.html'

    # Kontekst dla listy czynności POT
    def get_context_data(self, **kwargs):
        context = super(PartPOTs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Obsługi dla %s' % self.object
        context['empty_text'] = 'Brak zdefiniowanych czynności obsługowych.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową paczkę czynności', 'path': reverse("camo:pot-group-create", args=['oth', self.object.pk])})
        local_menu.append({'text': 'Importuj z pliku', 'path': reverse("camo:pot-group-upload", args=['oth', self.object.pk])})
        local_menu.append({'text': 'Usuń wybrane', 'path': reverse("camo:part-purge", args=['oth', self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Nazwa'})
        header_list.append({'header': 'Limit\nTTH'})
        header_list.append({'header': 'Limit\nmsc.'})
        if self.object.use_landings():
            header_list.append({'header': 'Limit\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Limit\ncycl.'})
        header_list.append({'header': 'Cykl'})
        header_list.append({'header': 'Wykon.\ndnia'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz grupy POT dla części
        groups = POT_group.objects.filter(part=self.object.pk, type='oth')

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'pot_ref', 'value': object.POT_ref, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'name', 'value': object})
            fields.append({'name': 'due_hours', 'value': object.due_hours, 'just': 'center'})
            fields.append({'name': 'due_months', 'value': object.due_months, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'due_landings', 'value': object.due_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'due_cycles', 'value': object.due_cycles, 'just': 'center'})
            fields.append({'name': 'cyclic', 'value': ('TAK' if object.cyclic else 'NIE'), 'just': 'center'})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-group-update', args=['oth', object.pk]),
                           'delete_link': reverse('camo:pot-group-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'pots'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartDirs (DetailView):
    model = Part
    template_name = 'camo/list_template.html'

    # Kontekst dla listy dyrektyw
    def get_context_data(self, **kwargs):
        context = super(PartDirs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Dyrektywy dla %s' % self.object
        context['empty_text'] = 'Brak dyrektyw.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową dyrektywę', 'path': reverse("camo:pot-group-create", args=['ad', self.object.pk])})
        local_menu.append({'text': 'Importuj z pliku', 'path': reverse("camo:pot-group-upload", args=['ad', self.object.pk])})
        local_menu.append({'text': 'Usuń wybrane', 'path': reverse("camo:part-purge", args=['ad', self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer AD'})
        header_list.append({'header': 'Data AD'})
        header_list.append({'header': 'Treść dyrektywy'})
        header_list.append({'header': 'Organ'})
        header_list.append({'header': 'Limit\nTTH'})
        header_list.append({'header': 'Limit\nmsc.'})
        if self.object.use_landings():
            header_list.append({'header': 'Limit\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Limit\ncycl.'})
        header_list.append({'header': 'Cykl'})
        header_list.append({'header': 'Wykon.\ndnia'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': 'Dotyczy'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz dyrektywy dla części
        groups = POT_group.objects.filter(part=self.object.pk, type='ad')

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'ad_no', 'value': object.adsb_no, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'ad_date', 'value': object.adsb_date, 'just': 'center'})
            fields.append({'name': 'ad', 'value': object})
            fields.append({'name': 'ad_agency', 'value': object.adsb_agency})
            fields.append({'name': 'due_hours', 'value': object.due_hours, 'just': 'center'})
            fields.append({'name': 'due_hours', 'value': object.due_months, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'due_landings', 'value': object.due_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'due_cycles', 'value': object.due_cycles, 'just': 'center'})
            fields.append({'name': 'cyclic', 'value': ('TAK' if object.cyclic else 'NIE'), 'just': 'center'})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'applies', 'value': ('TAK' if object.applies else 'NIE'), 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-group-update', args=['ad', object.pk]),
                           'delete_link': reverse('camo:pot-group-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'dirs'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartSBs (DetailView):
    model = Part
    template_name = 'camo/list_template.html'

    # Kontekst dla listy biuletynów
    def get_context_data(self, **kwargs):
        context = super(PartSBs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Biuletyny dla %s' % self.object
        context['empty_text'] = 'Brak biuletynów.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowy biuletyn', 'path': reverse("camo:pot-group-create", args=['sb', self.object.pk])})
        local_menu.append({'text': 'Importuj z pliku', 'path': reverse("camo:pot-group-upload", args=['sb', self.object.pk])})
        local_menu.append({'text': 'Usuń wybrane', 'path': reverse("camo:part-purge", args=['sb', self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer SB'})
        header_list.append({'header': 'Data SB'})
        header_list.append({'header': 'Treść biuletynu'})
        header_list.append({'header': 'Organ'})
        header_list.append({'header': 'Limit\nTTH'})
        header_list.append({'header': 'Limit\nmsc.'})
        if self.object.use_landings():
            header_list.append({'header': 'Limit\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Limit\ncycl.'})
        header_list.append({'header': 'Cykl'})
        header_list.append({'header': 'Wykon.\ndnia'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': 'Dotyczy'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz biuletyny dla części
        groups = POT_group.objects.filter(part=self.object.pk, type='sb')

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'sb_no', 'value': object.adsb_no, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'sb_date', 'value': object.adsb_date, 'just': 'center'})
            fields.append({'name': 'sb', 'value': object})
            fields.append({'name': 'sb_agency', 'value': object.adsb_agency})
            fields.append({'name': 'due_hours', 'value': object.due_hours, 'just': 'center'})
            fields.append({'name': 'due_hours', 'value': object.due_months, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'due_landings', 'value': object.due_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'due_cycles', 'value': object.due_cycles, 'just': 'center'})
            fields.append({'name': 'cyclic', 'value': ('TAK' if object.cyclic else 'NIE'), 'just': 'center'})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'applies', 'value': ('TAK' if object.applies else 'NIE'), 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-group-update', args=['sb', object.pk]),
                           'delete_link': reverse('camo:pot-group-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'sbs'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartLLP (DetailView):
    model = Part
    template_name = 'camo/list_template.html'

    # Kontekst dla listy demontaży
    def get_context_data(self, **kwargs):
        context = super(PartLLP, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Planowy demontaż dla %s' % self.object
        context['empty_text'] = 'Brak zaplanowanego demontażu.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowy demontaż', 'path': reverse("camo:pot-group-create", args=['llp', self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Nazwa'})
        header_list.append({'header': 'Limit\nTTH'})
        header_list.append({'header': 'Limit\nmsc.'})
        if self.object.use_landings():
            header_list.append({'header': 'Limit\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Limit\ncycl.'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz demontaże dla części
        groups = POT_group.objects.filter(part=self.object.pk, type='llp')

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'pot_ref', 'value': object.POT_ref, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'name', 'value': object})
            fields.append({'name': 'due_hours', 'value': object.due_hours, 'just': 'center'})
            fields.append({'name': 'due_hours', 'value': object.due_months, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'due_landings', 'value': object.due_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'due_cycles', 'value': object.due_cycles, 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-group-update', args=['llp', object.pk]),
                           'delete_link': reverse('camo:pot-group-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'llp'

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PartOvhs (DetailView):
    model = Part
    template_name = 'camo/list_template.html'

    # Kontekst dla listy remontów
    def get_context_data(self, **kwargs):
        context = super(PartOvhs, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Remonty dla %s' % self.object
        context['empty_text'] = 'Brak zaplanowanych remontów.'
        context['submenu_template'] = 'camo/part_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowy remont', 'path': reverse("camo:pot-group-create", args=['ovh', self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Nazwa'})
        header_list.append({'header': 'Limit\nTTH'})
        header_list.append({'header': 'Limit\nmsc.'})
        if self.object.use_landings():
            header_list.append({'header': 'Limit\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Limit\ncycl.'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\nTTH'})
        if self.object.use_landings():
            header_list.append({'header': 'Pozost.\nldg.'})
        if self.object.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz remonty dla części
        groups = POT_group.objects.filter(part=self.object.pk, type='ovh')

        # Zawartość tabeli
        row_list = []
        for object in groups:
            fields = []
            fields.append({'name': 'pot_ref', 'value': object.POT_ref, 'link': reverse('camo:pot-group-info', args=[object.pk])})
            fields.append({'name': 'name', 'value': object})
            fields.append({'name': 'due_hours', 'value': object.due_hours, 'just': 'center'})
            fields.append({'name': 'due_hours', 'value': object.due_months, 'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'due_landings', 'value': object.due_landings, 'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'due_cycles', 'value': object.due_cycles, 'just': 'center'})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-group-update', args=['ovh', object.pk]),
                           'delete_link': reverse('camo:pot-group-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'ovhs'

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class PartCreate (CreateView):
    model = Part
    template_name = 'camo/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(PartCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowa część'
        context['header_text'] = 'Utwórz nową część w magazynie'
        return context

    def get_form_class(self, **kwargs):
        return modelform_factory(Part, fields=('name', 'maker', 'part_no', 'serial_no', 'f1', 'lifecycle',
                                               'production_date', 'install_date', 'hours_count', 'landings_count', 'cycles_count'),
                                 widgets={'name':TextInput(attrs={'size':69}),
                                          'maker':TextInput(attrs={'size':69}),
                                          'production_date':AdminDateWidget(),
                                          'install_date':AdminDateWidget()})

    def get_success_url(self):
        return reverse('camo:part-info', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class PartUpdate (UpdateView):
    model = Part
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(PartUpdate, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Zmiana danych części'
        context['submenu_template'] = 'camo/part_submenu.html'
        context['type'] = 'info'

        return context

    def get_form_class(self, **kwargs):
        return modelform_factory(Part, fields=('name', 'maker', 'part_no', 'serial_no', 'f1', 'lifecycle',
                                               'production_date', 'install_date', 'hours_count', 'landings_count', 'cycles_count'),
                                 widgets={'name':TextInput(attrs={'size':69}),
                                          'maker':TextInput(attrs={'size':69}),
                                          'production_date':AdminDateWidget(),
                                          'install_date':AdminDateWidget()})

    def get_success_url(self):
        return reverse('camo:part-info', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class PartDelete (DeleteView):
    model = Part
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PartDelete, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Usunięcie części'
        context['submenu_template'] = 'camo/part_submenu.html'
        context['type'] = 'info'

        return context

    def get_success_url(self):
        return reverse('camo:part-list')


@permission_required('camo.camo_admin')
def PartPurge (request, type, part_id):
    context = {}
    part = get_object_or_404(Part, pk=part_id)

    context['object'] = part
    context['submenu_template'] = 'camo/part_submenu.html'

    if type == 'ad':
        context['type'] = 'dirs'
        desc = 'dyrektyw'
        fields = [('AD Ref.', 'POT_ref', False),
                  ('Numer\nAD', 'adsb_no', False),
                  ('Data\nAD', 'adsb_date', True),
                  ('Treść', 'name', False),
                  ('Organ', 'adsb_agency', False),
                  ('Limit\nFH', 'due_hours', True),
                  ('Limit\nmsc.', 'due_months', True)]
        if part.use_landings():
            fields.append(('Limit\ldg.', 'due_landings', True))
        if part.use_cycles():
            fields.append(('Limit\ncycl.', 'due_cycles', True))

    elif type == 'sb':
        context['type'] = 'sbs'
        desc = 'biuletynów'
        fields = [('SB Ref.', 'POT_ref', False),
                  ('Numer\nSB', 'adsb_no', False),
                  ('Data\nSB', 'adsb_date', True),
                  ('Treść', 'name', False),
                  ('Organ', 'adsb_agency', False),
                  ('Limit\nFH', 'due_hours', True),
                  ('Limit\nmsc.', 'due_months', True)]
        if part.use_landings():
            fields.append(('Limit\nldg.', 'due_landings', True))
        if part.use_cycles():
            fields.append(('Limit\ncycl.', 'due_cycles', True))

    elif type == 'llp':
        desc = 'demontaży'
        fields = []

    elif type == 'ovh':
        desc = 'remontów'
        fields = []

    else:
        context['type'] = 'pots'
        desc = 'obsług'
        fields = [('POT Ref.', 'POT_ref', False),
                  ('Opis', 'name', False),
                  ('Limit\nFH', 'due_hours', True),
                  ('Limit\nmsc.', 'due_months', True)]
        if part.use_landings():
            fields.append(('Limit\nldg.', 'due_landings', True))
        if part.use_cycles():
            fields.append(('Limit\ncycl.', 'due_cycles', True))

    context['title'] = 'Usuwanie %s dla %s' % (desc, part)
    context['empty_text'] = 'Brak %s do usunięcia.' % desc

    # formularz w formie tabeli do wybotu rekordów do usunięcia
    form = PartPurgeForm(request.POST or None, part=part, type=type, fields=fields)
    context['form'] = form
    context['headers'] = [field[0] for field in fields]

    if form.is_valid():

        # skasowanie z bazy kolejnych zaznaczonych rekordów
        for group in part.pot_group_set.filter(type=type):
            # jeśli wiersz został zaznaczony
            if form.cleaned_data['group%d' % group.pk]:
                group.delete()

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

    return render(request, 'camo/part_purge.html', context)


@permission_required('camo.camo_admin')
def AssignmentUpdate (request, assignment_id):

    context = {}
    context['submenu_template'] = 'camo/aircraft_submenu.html'
    context['type'] = 'parts'

    assignment = get_object_or_404(Assignment, pk=assignment_id)
    context['aircraft'] = assignment.aircraft
    context['part'] = assignment.part
    mounted_parts = assignment.aircraft.assignment_set.filter(current=True, super_ass=None).exclude(pk=assignment_id)
    form = AssignmentUpdateForm(request.POST or None, mounted_parts=mounted_parts,
                                use_landings=assignment.aircraft.use_landings, use_cycles=assignment.aircraft.use_cycles,
                                initial={'ata': assignment.ata_id,
                                         'super_part': assignment.super_ass_id,
                                         'description': assignment.description,
                                         'from_date': assignment.from_date,
                                         'from_hours': assignment.from_hours,
                                         'from_landings': assignment.from_landings,
                                         'from_cycles': assignment.from_cycles,
                                         'crs' : assignment.crs})
    context['form']=form
    if form.is_valid():
        if form.cleaned_data['super_part'] != '':
            super_ass = get_object_or_404(Assignment, pk=form.cleaned_data['super_part'])
        else:
            super_ass = None
        assignment.ata = get_object_or_404(ATA, pk=form.cleaned_data['ata'])
        assignment.super_ass=super_ass
        assignment.description=form.cleaned_data['description']
        assignment.from_date=form.cleaned_data['from_date']
        assignment.from_hours=form.cleaned_data['from_hours']
        assignment.from_landings=form.cleaned_data['from_landings']
        assignment.from_cycles=form.cleaned_data['from_cycles']
        assignment.crs=form.cleaned_data['crs']
        assignment.full_clean()
        assignment.save()
        return HttpResponseRedirect(reverse('camo:aircraft-parts', args=[assignment.aircraft.pk]))
    return render(request, 'camo/assignment_update.html', context)


@permission_required('camo.camo_admin')
def AssignmentDelete (request, assignment_id):

    context = {}
    context['submenu_template'] = 'camo/aircraft_submenu.html'
    context['type'] = 'parts'

    # poniższe wyrażenie do przemyślenia jeszcze #
    # dodać sprawdzenie że data do nie może być wcześniejsza niż from #
    assignment = Assignment.objects.get(pk=assignment_id)
    context['aircraft'] = assignment.aircraft
    context['part'] = assignment.part
    form = AssignmentDeleteForm(request.POST or None,
                                use_landings=assignment.aircraft.use_landings, use_cycles=assignment.aircraft.use_cycles,
                                initial={'to_date': date.today(),
                                         'to_hours': assignment.aircraft.hours_count,
                                         'to_landings': assignment.aircraft.landings_count,
                                         'to_cycles': assignment.aircraft.cycles_count})
    context['form'] = form
    if form.is_valid():
        assignment.to_date = form.cleaned_data['to_date']
        assignment.to_hours = form.cleaned_data['to_hours']
        assignment.to_landings = form.cleaned_data['to_landings']
        assignment.to_cycles = form.cleaned_data['to_cycles']
        assignment.super_ass = None
        assignment.current = False
        assignment.full_clean()
        assignment.save()
        return HttpResponseRedirect(reverse('camo:aircraft-parts', args=[assignment.aircraft.pk]))
    return render(request, 'camo/assignment_delete.html', context)


@class_view_decorator(permission_required('camo.camo_reader'))
class POTGroupInfo (DetailView):
    model = POT_group
    template_name = 'camo/details_template.html'

    # Kontekst dla ekranu informacji o grupie obsługowej #
    def get_context_data(self, **kwargs):
        context = super(POTGroupInfo, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object.POT_ref
        if self.object.type == 'ad':
            context['header_text'] = 'Informacje o dyrektywie %s' % self.object.POT_ref
        elif self.object.type == 'sb':
            context['header_text'] = 'Informacje o biuletynie %s' % self.object.POT_ref
        elif self.object.type == 'llp':
            context['header_text'] = 'Informacje o planowym demontażu %s' % self.object.POT_ref
        elif self.object.type == 'ovh':
            context['header_text'] = 'Informacje o remoncie %s' % self.object.POT_ref
        else:
            context['header_text'] = 'Informacje o paczce obsługowej %s' % self.object.POT_ref

        context['header_width'] = '150px'
        context['submenu_template'] = 'camo/group_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Czynności składowe', 'path': reverse('camo:pot-group-events', args=[self.object.pk])})
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:pot-group-update', args=[self.object.type, self.object.pk])})
        local_menu.append({'text': 'Klonuj', 'path': reverse('camo:pot-group-clone', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('camo:pot-group-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'POT Ref.', 'value': self.object.POT_ref, 'bold': True})
        field_list.append({'header': 'Część', 'value': self.object.part})
        field_list.append({'header': 'Nazwa', 'value': self.object.name})
        if self.object.type in ['ad', 'sb']:
            field_list.append({'header': 'Numer AD/SB', 'value': self.object.adsb_no})
            field_list.append({'header': 'Data AD/SB', 'value': self.object.adsb_date})
            field_list.append({'header': 'Organ wydający', 'value': self.object.adsb_agency})
            field_list.append({'header': 'Powiązanie AD/SB', 'value': self.object.adsb_related})
        field_list.append({'header': 'Limit godzin', 'value': '%s%s' % ((self.object.due_hours if self.object.due_hours else 'Nie określono'),
                           (' (pozostało: %s FH)' % self.object.left_hours() if self.object.due_hours and self.object.left_hours() else ''))})
        field_list.append({'header': 'Limit miesięcy', 'value': '%s%s' % ((self.object.due_months if self.object.due_months else 'Nie określono'),
                           (' (pozostało: %s dni)' % self.object.left_days() if self.object.due_months and self.object.left_days() else ''))})
        if self.object.part.use_landings():
            field_list.append({'header': 'Limit lądowań', 'value': '%s%s' % ((self.object.due_landings if self.object.due_landings else 'Nie określono'),
                               (' (pozostało: %s)' % self.object.left_landings() if self.object.due_landings and self.object.left_landings() else ''))})
        if self.object.part.use_cycles():
            field_list.append({'header': 'Limit cykli', 'value': '%s%s' % ((self.object.due_cycles if self.object.due_cycles else 'Nie określono'),
                               (' (pozostało: %s)' % self.object.left_cycles() if self.object.due_cycles and self.object.left_cycles() else ''))})
        field_list.append({'header': 'Sposób liczenia', 'value': ('Od produkcji/remontu' if self.object.count_type == 'production' else 'Od instalacji')})
        if self.object.type != 'llp':
            field_list.append({'header': 'Czynność cykliczna', 'value': 'TAK' if self.object.cyclic else 'NIE'})
        if self.object.type == 'oth':
            field_list.append({'header': 'Czynność postojowa', 'value': 'TAK' if self.object.parked else 'NIE'})
        if self.object.type in ['oth', 'sb']:
            field_list.append({'header': 'Czynność opcjonalna', 'value': 'TAK' if self.object.optional else 'NIE'})
        if self.object.type in ['ad', 'sb']:
            field_list.append({'header': 'Dotyczy danej cześci', 'value': 'TAK' if self.object.applies else 'NIE'})
        if self.object.done_date:
            field_list.append({'header': 'Wykonano (data)', 'value': self.object.done_date})
        if self.object.done_hours:
            field_list.append({'header': 'Wykonano (TTH)', 'value': self.object.done_hours})
        if self.object.done_landings and self.object.part.use_landings():
            field_list.append({'header': 'Wykonano (lądowania)', 'value': self.object.done_landings})
        if self.object.done_cycles and self.object.part.use_cycles():
            field_list.append({'header': 'Wykonano (cykle)', 'value': self.object.done_cycles})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        context['type'] = 'info'
        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class POTGroupEvents (DetailView):
    model = POT_group
    template_name = 'camo/list_template.html'

    # Kontekst dla listy czynności w grupie POT
    def get_context_data(self, **kwargs):
        context = super(POTGroupEvents, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object.POT_ref
        context['header_text'] = 'Lista czynności dla %s' % self.object.POT_ref
        context['empty_text'] = 'Brak zdefiniowanych czynności.'
        context['submenu_template'] = 'camo/group_submenu.html'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową czynność', 'path': reverse("camo:pot-event-create", args=[self.object.pk])})
        local_menu.append({'text': 'Importuj z pliku', 'path': reverse("camo:pot-event-upload", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Czynność'})
        header_list.append({'header': 'Wykon.\ndata'})
        header_list.append({'header': 'Wykon.\nTTH'})
        if self.object.part.use_landings():
            header_list.append({'header': 'Wykon.\nldg.'})
        if self.object.part.use_cycles():
            header_list.append({'header': 'Wykon.\ncycl.'})
        header_list.append({'header': 'CRS\nwykonania'})
        header_list.append({'header': 'Pozost.\ndni'})
        header_list.append({'header': 'Pozost.\ngodzin'})
        if self.object.part.use_landings():
            header_list.append({'header': 'Pozost..\nldg.'})
        if self.object.part.use_cycles():
            header_list.append({'header': 'Pozost.\ncycl.'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Wybierz czynności dla grupy POT
        events = self.object.pot_event_set.all()

        # Zawartość tabeli
        row_list = []
        for object in events:
            fields = []
            fields.append({'name': 'pot_ref', 'value': object.POT_ref, 'link': reverse('camo:pot-event-details', args=[object.pk])})
            fields.append({'name': 'name', 'value': object.name})
            fields.append({'name': 'done_date', 'value': object.done_date, 'just': 'center'})
            fields.append({'name': 'done_hours', 'value': object.done_hours, 'just': 'center'})
            if self.object.part.use_landings():
                fields.append({'name': 'done_landings', 'value': object.done_landings, 'just': 'center'})
            if self.object.part.use_cycles():
                fields.append({'name': 'done_cycles', 'value': object.done_cycles, 'just': 'center'})
            fields.append({'name': 'done_crs', 'value': object.done_crs})
            fields.append({'name': 'left_days', 'value': object.left_days(), 'color': ('auto' if (object.left_days() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'left_hours', 'value': object.left_hours(), 'color': ('auto' if (object.left_hours() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.part.use_landings():
                fields.append({'name': 'left_landings', 'value': object.left_landings(), 'color': ('auto' if (object.left_landings() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            if self.object.part.use_cycles():
                fields.append({'name': 'left_cycles', 'value': object.left_cycles(), 'color': ('auto' if (object.left_cycles() or 0) >= 0 else 'lightcoral'),'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('camo:pot-event-update', args=[object.pk]),
                           'delete_link': reverse('camo:pot-event-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        # Pozycja w bocznym menu
        context['type'] = 'events'

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class POTGroupCreate (CreateView):
    model = POT_group
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        part = get_object_or_404(Part, pk=self.kwargs['part_id'])
        if self.kwargs['type'] == 'llp':
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type', 'remarks']
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'ovh':
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type',
                    'done_date', 'done_hours', 'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(7, 'done_cycles')
            if part.use_landings():
                fields.insert(7, 'done_landings')
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'ad':
            fields=['POT_ref', 'adsb_no', 'adsb_date', 'name', 'adsb_agency', 'adsb_related',
                    'due_hours', 'due_months', 'count_type', 'cyclic', 'applies', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(12, 'done_cycles')
            if part.use_landings():
                fields.insert(12, 'done_landings')
            if part.use_cycles():
                fields.insert(8, 'due_cycles')
            if part.use_landings():
                fields.insert(8, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'adsb_date':AdminDateWidget(),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'sb':
            fields=['POT_ref', 'adsb_no', 'adsb_date', 'name', 'adsb_agency', 'adsb_related',
                    'due_hours', 'due_months', 'count_type', 'cyclic', 'optional', 'applies', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(13, 'done_cycles')
            if part.use_landings():
                fields.insert(13, 'done_landings')
            if part.use_cycles():
                fields.insert(8, 'due_cycles')
            if part.use_landings():
                fields.insert(8, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'adsb_date':AdminDateWidget(),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
            form_class.base_fields['optional'].initial = False
        else:
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type',
                    'cyclic', 'parked', 'optional', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(10, 'done_cycles')
            if part.use_landings():
                fields.insert(10, 'done_landings')
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        return form_class

    def form_valid(self, form):
        form.instance.part = get_object_or_404(Part, pk=self.kwargs['part_id'])
        form.instance.type = self.kwargs['type']
        return super(POTGroupCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(POTGroupCreate, self).get_context_data(**kwargs)
        part = get_object_or_404(Part, pk=self.kwargs['part_id'])
        titles = {'oth': 'Nowa paczka czynności',
                   'ad': 'Nowa dyrektywa',
                   'sb': 'Nowy biuletyn',
                  'llp': 'Nowy demontaż',
                  'ovh': 'Nowy remont'}

        types = {'oth': 'pots',
                  'ad': 'dirs',
                  'sb': 'sbs',
                 'llp': 'llp',
                 'ovh': 'ovhs'}

        context['page_title'] = titles[self.kwargs['type']]
        context['header_text'] = '%s dla %s' % (titles[self.kwargs['type']], part)
        context['object'] = part
        context['submenu_template'] = 'camo/part_submenu.html'
        context['type'] = types[self.kwargs['type']]

        return context

    def get_success_url(self):
        return reverse('camo:pot-group-info', args=[self.object.pk])


@permission_required('camo.camo_admin')
def POTGroupClone (request, potgroup_id):
    context = {}
    group = get_object_or_404(POT_group, pk=potgroup_id)

    context['group'] = group
    context['object'] = group
    context['submenu_template'] = 'camo/group_submenu.html'
    context['type'] = 'info'

    parts = []
    for part in Part.objects.filter(maker = group.part.maker, part_no = group.part.part_no).exclude(pk = group.part.pk):
        if not part.pot_group_set.filter(POT_ref = group.POT_ref, type=group.type):
            parts.append(part)
    context['parts']=parts
    form = POTGroupCloneForm(request.POST or None, parts=parts)
    context['form']=form
    if form.is_valid():
        for part_id in form.cleaned_data['parts']:
            part = Part.objects.get(pk=part_id)
            pot_group = POT_group(part = part,
                                  POT_ref = group.POT_ref,
                                  adsb_no = group.adsb_no,
                                  adsb_date = group.adsb_date,
                                  adsb_agency = group.adsb_agency,
                                  name = group.name,
                                  type = group.type,
                                  due_hours = group.due_hours,
                                  due_months = group.due_months,
                                  due_landings = group.due_landings,
                                  due_cycles = group.due_cycles,
                                  cyclic = group.cyclic,
                                  parked = group.parked,
                                  count_type = group.count_type,
                                  optional = group.optional,
                                  applies = group.applies,
                                  done_crs = None, done_date = None, done_hours = None,
                                  done_landings = None, done_cycles = None,
                                  done_aso = None, remarks = None)
            pot_group.full_clean()
            pot_group.save()

        return HttpResponseRedirect(reverse('camo:pot-group-info', args=[group.pk]))
    return render(request, 'camo/pot_group_clone.html', context)


@class_view_decorator(permission_required('camo.camo_admin'))
class POTGroupUpdate (UpdateView):
    model = POT_group
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        part = self.object.part
        if self.kwargs['type'] == 'llp':
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type', 'remarks']
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'ovh':
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type',
                    'done_date', 'done_hours', 'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(7, 'done_cycles')
            if part.use_landings():
                fields.insert(7, 'done_landings')
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'ad':
            fields=['POT_ref', 'adsb_no', 'adsb_date', 'name', 'adsb_agency', 'adsb_related',
                    'due_hours', 'due_months', 'count_type', 'cyclic', 'applies', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(12, 'done_cycles')
            if part.use_landings():
                fields.insert(12, 'done_landings')
            if part.use_cycles():
                fields.insert(8, 'due_cycles')
            if part.use_landings():
                fields.insert(8, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'adsb_date':AdminDateWidget(),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        elif self.kwargs['type'] == 'sb':
            fields=['POT_ref', 'adsb_no', 'adsb_date', 'name', 'adsb_agency', 'adsb_related',
                    'due_hours', 'due_months', 'count_type', 'cyclic', 'optional', 'applies', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(13, 'done_cycles')
            if part.use_landings():
                fields.insert(13, 'done_landings')
            if part.use_cycles():
                fields.insert(8, 'due_cycles')
            if part.use_landings():
                fields.insert(8, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'adsb_date':AdminDateWidget(),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        else:
            fields=['POT_ref', 'name', 'due_hours', 'due_months', 'count_type',
                    'cyclic', 'parked', 'optional', 'done_date', 'done_hours',
                    'done_crs', 'done_aso', 'remarks']
            if part.use_cycles():
                fields.insert(10, 'done_cycles')
            if part.use_landings():
                fields.insert(10, 'done_landings')
            if part.use_cycles():
                fields.insert(4, 'due_cycles')
            if part.use_landings():
                fields.insert(4, 'due_landings')
            form_class = modelform_factory(POT_group, fields=fields,
                                           widgets={'name':TextInput(attrs={'size':100}),
                                                    'done_date':AdminDateWidget(),
                                                    'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        return form_class

    def get_context_data(self, **kwargs):
        context = super(POTGroupUpdate, self).get_context_data(**kwargs)

        titles = {'oth': 'Aktualizacja paczki czynności',
                   'ad': 'Aktualizacja dyrektywy',
                   'sb': 'Aktualizacja biuletynu',
                  'llp': 'Aktualizacja demontażu',
                  'ovh': 'Aktualizacja remontu'}

        context['page_title'] = self.object.POT_ref
        context['header_text'] = titles[self.object.type]
        context['submenu_template'] = 'camo/group_submenu.html'
        context['type'] = 'info'

        return context

    def form_valid(self, form):
        done_fields = ['done_crs', 'done_date', 'done_hours', 'done_landings', 'done_cycles']

        # zaktualizuj parametry wykonania dla czynności składowych
        if any(field in form.changed_data for field in done_fields):
            for event in self.object.pot_event_set.all():
                for event_field in done_fields:
                    if event_field in form.changed_data:
                        setattr(event, event_field, form.cleaned_data[event_field])
                event.save()

        return super(POTGroupUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:pot-group-info', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class POTGroupDelete (DeleteView):
    model = POT_group
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(POTGroupDelete, self).get_context_data(**kwargs)

        titles = {'oth': 'Usunięcie paczki czynności',
                   'ad': 'Usunięcie dyrektywy',
                   'sb': 'Usunięcie biuletynu',
                  'llp': 'Usunięcie demontażu',
                  'ovh': 'Usunięcie remontu'}

        context['page_title'] = self.object.POT_ref
        context['header_text'] = titles[self.object.type]
        context['submenu_template'] = 'camo/group_submenu.html'
        context['type'] = 'info'

        return context

    def get_success_url(self):
        # przekierowanie do właściwego viewsa na podstawie typu
        if self.object.type == 'ad':
            return reverse('camo:part-dirs', args=[self.object.part.pk])
        elif self.object.type == 'sb':
            return reverse('camo:part-sbs', args=[self.object.part.pk])
        elif self.object.type == 'llp':
            return reverse('camo:part-llp', args=[self.object.part.pk])
        elif self.object.type == 'ovh':
            return reverse('camo:part-ovhs', args=[self.object.part.pk])
        else:
            return reverse('camo:part-pots', args=[self.object.part.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class POTEventDetails (DetailView):
    model = POT_event
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(POTEventDetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o czynności %s' % self.object.POT_ref

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:pot-event-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('camo:pot-event-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'POT Ref.', 'value': self.object.POT_ref, 'bold': True})
        field_list.append({'header': 'Nazwa', 'value': self.object.name})
        field_list.append({'header': 'Wykonano (data)', 'value': self.object.done_date})
        field_list.append({'header': 'Wykonano (TTH)', 'value': self.object.done_hours})
        if self.object.POT_group.part.use_landings():
            field_list.append({'header': 'Wykonano (lądowania)', 'value': self.object.done_landings})
        if self.object.POT_group.part.use_cycles():
            field_list.append({'header': 'Wykonano (cykle)', 'value': self.object.done_cycles})
        field_list.append({'header': 'Wykonano (CRS ref.)', 'value': self.object.done_crs})
        context['field_list'] = field_list

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class POTEventCreate (CreateView):
    model = POT_event
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        pot_group = get_object_or_404(POT_group, pk=self.kwargs['pot_group_id'])
        fields=['POT_ref', 'name', 'done_date', 'done_hours', 'done_crs']
        if pot_group.part.use_cycles():
            fields.insert(4, 'done_cycles')
        if pot_group.part.use_landings():
            fields.insert(4, 'done_landings')
        form_class = modelform_factory(POT_event, fields=fields,
                                       widgets={'name':Textarea(attrs={'rows':3, 'cols':100}),
                                                'done_date':AdminDateWidget()})
        return form_class

    def form_valid(self, form):
        form.instance.POT_group = get_object_or_404(POT_group, pk=self.kwargs['pot_group_id'])
        return super(POTEventCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(POTEventCreate, self).get_context_data(**kwargs)
        pot_group = get_object_or_404(POT_group, pk=self.kwargs['pot_group_id'])

        context['page_title'] = 'Nowa czynność'
        context['header_text'] = 'Nowa czynność dla %s' % pot_group.POT_ref
        context['object'] = pot_group
        context['submenu_template'] = 'camo/group_submenu.html'
        context['type'] = 'events'

        return context

    def get_success_url(self):
        return reverse('camo:pot-group-events', args=[self.object.POT_group.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class POTEventUpdate (UpdateView):
    model = POT_event
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        pot_group = self.object.POT_group
        fields=['POT_ref', 'name', 'done_date', 'done_hours', 'done_crs']
        if pot_group.part.use_cycles():
            fields.insert(4, 'done_cycles')
        if pot_group.part.use_landings():
            fields.insert(4, 'done_landings')
        form_class = modelform_factory(POT_event, fields=fields,
                                       widgets={'name':Textarea(attrs={'rows':3, 'cols':100}),
                                                'done_date':AdminDateWidget()})
        return form_class

    def get_context_data(self, **kwargs):
        context = super(POTEventUpdate, self).get_context_data(**kwargs)

        context['page_title'] = self.object.POT_ref
        context['header_text'] = 'Aktualizacja czynności'

        return context

    def get_success_url(self):
        return reverse('camo:pot-group-events', args=[self.object.POT_group.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class POTEventDelete (DeleteView):
    model = POT_event
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(POTEventDelete, self).get_context_data(**kwargs)

        context['page_title'] = self.object.POT_ref
        context['header_text'] = 'Usunięcie czynności'

        return context

    def get_success_url(self):
        return reverse('camo:pot-group-events', args=[self.object.POT_group.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class ATAList (ListView):
    model = ATA
    template_name = 'camo/list_template.html'

    def get_queryset(self, **kwargs):
        return ATA.objects.order_by('section')

    def get_context_data(self, **kwargs):
        # Informacje nagłówkowe
        context = super(ATAList, self).get_context_data(**kwargs)
        context['page_title'] = 'ATA'
        context['header_text'] = 'Lista pozycji ATA'
        context['empty_text'] = 'Brak pozycji ATA.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową pozycję ATA', 'path': reverse("camo:ata-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Rozdz.'})
        header_list.append({'header': 'Tytuł\nrozdziału'})
        header_list.append({'header': 'Sekcjs'})
        header_list.append({'header': 'Tytuł\nsekcji'})
        header_list.append({'header': 'Opis'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'chapter', 'value': object.chapter, 'just': 'center'})
            fields.append({'name': 'chapter_title', 'value': object.chapter_title})
            fields.append({'name': 'section', 'value': object.section, 'link': reverse('camo:ata-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'section_title', 'value': object.section_title, 'link': reverse('camo:ata-details', args=[object.pk])})
            fields.append({'name': 'description', 'value': object.description})
            fields.append({'name': 'change', 'edit_link': reverse('camo:ata-update', args=[object.pk]),
                           'delete_link': (reverse('camo:ata-delete', args=[object.pk]) if not object.assignment_set.all() else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class ATADetails (DetailView):
    model = ATA
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(ATADetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object.section
        context['header_text'] = 'Informacje o sekcji %s' % self.object.section
        context['header_width'] = '100px'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:ata-update', args=[self.object.pk])})
        if not self.object.assignment_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('camo:ata-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Rozdział', 'value': self.object.chapter})
        field_list.append({'header': 'Tytuł rozdziału', 'value': self.object.chapter_title})
        field_list.append({'header': 'Sekcja', 'value': self.object.section, 'bold': True})
        field_list.append({'header': 'Tytuł sekcji', 'value': self.object.section_title, 'bold': True})
        field_list.append({'header': 'Opis', 'value': self.object.description})
        context['field_list'] = field_list

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class ATACreate (CreateView):
    model = ATA
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        return modelform_factory(ATA, fields='__all__', widgets={'chapter_title':TextInput(attrs={'size':100}),
                                                                 'section_title':TextInput(attrs={'size':100}),
                                                                 'description':Textarea(attrs={'rows':10, 'cols':100})})

    def get_context_data(self, **kwargs):
        context = super(ATACreate, self).get_context_data(**kwargs)

        context['page_title'] = 'Nowa ATA'
        context['header_text'] = 'Nowa pozycja ATA'

        return context

    def get_success_url(self):
        return reverse('camo:ata-list')


@class_view_decorator(permission_required('camo.camo_admin'))
class ATAUpdate (UpdateView):
    model = ATA
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        return modelform_factory(ATA, fields='__all__', widgets={'chapter_title':TextInput(attrs={'size':100}),
                                                                 'section_title':TextInput(attrs={'size':100}),
                                                                 'description':Textarea(attrs={'rows':10, 'cols':100})})

    def get_context_data(self, **kwargs):
        context = super(ATAUpdate, self).get_context_data(**kwargs)

        context['page_title'] = self.object.section
        context['header_text'] = 'Zmiana pozycji ATA'

        return context

    def get_success_url(self):
        return reverse('camo:ata-list')


@class_view_decorator(permission_required('camo.camo_admin'))
class ATADelete (DeleteView):
    model = ATA
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(ATADelete, self).get_context_data(**kwargs)

        context['page_title'] = self.object.section
        context['header_text'] = 'Usunięcie pozycji ATA'

        return context

    def get_success_url(self):
        return reverse('camo:ata-list')


@permission_required('camo.camo_admin')
def WorkOrderCreate (request, aircraft_id):
    context = {}
    aircraft = get_object_or_404(Aircraft, pk=aircraft_id)
    context['aircraft'] = aircraft
    context['page_title'] = 'Nowe zlecenie'
    context['header_text'] = 'Nowe zlecenie obsługi dla %s' % aircraft
    context['object'] = aircraft
    context['submenu_template'] = 'camo/aircraft_submenu.html'
    context['type'] = 'orders'

    groups = []
    for part in aircraft.components():
        for group in part.pot_group_set.all():
            groups.append(group)
    groups = sorted(groups, key=lambda group: group.leftx())
    form = WorkOrderCreateForm(request.POST or None, initial={'date': date.today()}, groups=groups)
    context['form'] = form

    if form.is_valid():
        work_order = Work_order(aircraft=get_object_or_404(Aircraft, pk=aircraft_id),
                                number=form.cleaned_data['number'],
                                date=form.cleaned_data['date'],
                                aso=form.cleaned_data['organization'])
        work_order.full_clean()
        work_order.save()
        for type in ['oth', 'ad', 'sb', 'llp', 'ovh']:
            list = form.cleaned_data[type]
            for group in list:
                work_order_line = Work_order_line(work_order=work_order, pot_group=get_object_or_404(POT_group, pk=group))
                work_order_line.full_clean()
                work_order_line.save()
        return HttpResponseRedirect(reverse('camo:aircraft-orders', args=[aircraft_id]))
    return render(request, 'camo/create_template.html', context)


@class_view_decorator(permission_required('camo.camo_reader'))
class WorkOrderList (ListView):
    model = Work_order
    template_name = 'camo/list_template.html'

    # Posortuj listę po datach malejąco
    def get_queryset(self):
        return Work_order.objects.order_by('-date')

    def get_context_data(self, **kwargs):
        # Informacje nagłówkowe
        context = super(WorkOrderList, self).get_context_data(**kwargs)
        context['page_title'] = 'Zlecenia'
        context['header_text'] = 'Lista zleceń obsługowych'
        context['empty_text'] = 'Brak zleceń obsługowych.'

        # Lokalne menu
        local_menu = []
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Numer'})
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'Rejestracja'})
        header_list.append({'header': 'Organizacja'})
        header_list.append({'header': 'Staus'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'number', 'value': object.number, 'link': reverse('camo:order-details', args=[object.pk])})
            fields.append({'name': 'date', 'value': object.date, 'just': 'center'})
            fields.append({'name': 'aircraft', 'value': object.aircraft, 'link': reverse('camo:aircraft-info', args=[object.aircraft.pk]), 'just': 'center'})
            fields.append({'name': 'aso', 'value': object.aso})
            fields.append({'name': 'status', 'value': ('Otwarte' if object.open else 'Zamknięte'), 'just': 'center'})
            fields.append({'name': 'change', 'delete_link': (reverse('camo:order-close', args=[object.pk]) if object.open else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class WorkOrderDetails (DetailView):
    model = Work_order
    template_name = 'camo/order_details.html'

    def get_context_data(self, **kwargs):
        context = super(WorkOrderDetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o zleceniu %s' % self.object.number

        # Lokalne menu
        local_menu = []
        if self.object.open:
            local_menu.append({'text': 'Wystaw CRS', 'path': reverse('camo:crs-create', args=[self.object.pk])})
            local_menu.append({'text': 'Anuluj zlecenie', 'path': reverse('camo:order-close', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Numer zlecenia', 'value': self.object.number, 'bold': True})
        field_list.append({'header': 'Data utworzenia', 'value': self.object.date})
        field_list.append({'header': 'Statek powietrzny', 'value': self.object.aircraft})
        field_list.append({'header': 'Organizacja', 'value': self.object.aso})
        field_list.append({'header': 'Status zlecenia', 'value': ('Otwarte' if self.object.open else 'Zamknięte')})
        context['field_list'] = field_list

        groups = self.object.work_order_line_set.all()

        # Informacje nagłówkowe dla podeskcji
        context['groups_header_text'] = 'Paczki czynności w zleceniu'
        context['groups_empty_text'] = 'Brak paczek czynności.'

        # Nagłówki tabeli w podsekcji
        header_list = []
        header_list.append({'header': 'Lp.'})
        header_list.append({'header': 'POT Ref.'})
        header_list.append({'header': 'Nazwa\nczynności'})
        header_list.append({'header': 'Status'})
        context['groups_header_list'] = header_list

        # Zawartość tabeli w podsekcji
        row_list = []
        lp = 1
        for object in groups:
            fields = []
            fields.append({'name': 'counter', 'value': '%d.' % lp, 'just': 'center'})
            fields.append({'name': 'pot_ref', 'value': object.pot_group.POT_ref, 'link': reverse('camo:pot-group-info', args=[object.pot_group.pk])})
            fields.append({'name': 'name', 'value': object.pot_group})
            fields.append({'name': 'status', 'value': ('Wykonano' if object.done else 'Nie wykonano'), 'just': 'center'})
            row_list.append({'fields': fields})
            lp += 1
        context['groups_row_list'] = row_list

        return context


@permission_required('camo.camo_admin')
def WorkOrderClose (request, work_order_id):
    context = {}
    work_order = get_object_or_404(Work_order, pk=work_order_id)
    context['order'] = work_order
    form = WorkOrderCloseForm(request.POST or None)
    context['form'] = form

    if form.is_valid():
        work_order.open = False
        work_order.full_clean()
        work_order.save()
        return HttpResponseRedirect(reverse('camo:order-list'))
    return render(request, 'camo/order_close.html', context)


@permission_required('camo.camo_admin')
def CRSCreate (request, work_order_id):
    context = {}
    work_order = get_object_or_404(Work_order, pk=work_order_id)
    context['work_order'] = work_order
    lines = work_order.work_order_line_set.filter(done = False)
    form = CRSCreateForm(request.POST or None, use_landings=work_order.aircraft.use_landings, use_cycles=work_order.aircraft.use_cycles, lines=lines,
                         initial={'date': date.today(),
                                  'hours': work_order.aircraft.hours_count,
                                  'landings': work_order.aircraft.landings_count,
                                  'cycles': work_order.aircraft.cycles_count})
    context['form'] = form
    if form.is_valid():
        for line_id in form.cleaned_data['lines']:
            work_order_line = get_object_or_404(Work_order_line, pk=line_id)
            pot_group=get_object_or_404(POT_group, pk=work_order_line.pot_group.pk)
            for pot_event in pot_group.pot_event_set.all():
                pot_event.done_crs=form.cleaned_data['number']
                pot_event.done_date=form.cleaned_data['date']
                pot_event.done_hours=form.cleaned_data['hours']
                pot_event.done_landings=form.cleaned_data['landings']
                pot_event.done_cycles=form.cleaned_data['cycles']
                pot_event.full_clean()
                pot_event.save()
            pot_group.done_crs=form.cleaned_data['number']
            pot_group.done_date=form.cleaned_data['date']
            pot_group.done_hours=form.cleaned_data['hours']
            pot_group.done_landings=form.cleaned_data['landings']
            pot_group.done_cycles=form.cleaned_data['cycles']
            pot_group.done_aso=work_order.aso
            pot_group.full_clean()
            pot_group.save()
            work_order_line.done = True
            work_order_line.done_crs=form.cleaned_data['number']
            work_order_line.done_date=form.cleaned_data['date']
            work_order_line.done_hours=form.cleaned_data['hours']
            work_order_line.done_landings=form.cleaned_data['landings']
            work_order_line.done_cycles=form.cleaned_data['cycles']
            work_order_line.full_clean()
            work_order_line.save()
        # Jeśli wybrano 'Zamknij' lub nie ma już otwartych lini #
        if form.cleaned_data['close'] or not work_order.work_order_line_set.filter(done=False):
            work_order.open=False
            work_order.save()
        return HttpResponseRedirect(reverse('camo:order-details', args=[work_order_id]))
    return render(request, 'camo/crs_create.html', context)


@class_view_decorator(permission_required('camo.camo_reader'))
class ModificationDetails (DetailView):
    model = Modification
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(ModificationDetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o modyfikacji lub naprawie dla %s' % self.object.aircraft
        context['header_width'] = '120px'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'mods'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:modification-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('camo:modification-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Statek powietrzny', 'value': self.object.aircraft, 'bold': True})
        field_list.append({'header': 'Opis', 'value': self.object.description})
        field_list.append({'header': 'Wykonano (data)', 'value': self.object.done_date})
        field_list.append({'header': 'Wykonano (TTH)', 'value': self.object.done_hours})
        if self.object.aircraft.use_landings:
            field_list.append({'header': 'Wykonano (lądowania)', 'value': self.object.done_landings})
        if self.object.aircraft.use_cycles:
            field_list.append({'header': 'Wykonano (cykle)', 'value': self.object.done_cycles})
        field_list.append({'header': 'Organizacja', 'value': self.object.aso})
        field_list.append({'header': 'CRS Ref.', 'value': self.object.done_crs})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class ModificationCreate (CreateView):
    model = Modification
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        fields = ['description', 'done_date', 'done_hours', 'aso', 'done_crs', 'remarks']
        if aircraft.use_cycles:
            fields.insert(3, 'done_cycles')
        if aircraft.use_landings:
            fields.insert(3, 'done_landings')
        form_class = modelform_factory(Modification, fields=fields,
                                       widgets={'description':TextInput(attrs={'size':103}),
                                                'done_date':AdminDateWidget(),
                                                'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        form_class.base_fields['done_date'].initial = date.today()
        form_class.base_fields['done_hours'].initial = aircraft.hours_count
        if aircraft.use_landings:
            form_class.base_fields['done_landings'].initial = aircraft.landings_count
        if aircraft.use_cycles:
            form_class.base_fields['done_cycles'].initial = aircraft.cycles_count
        return form_class

    def get_context_data(self, **kwargs):
        context = super(ModificationCreate, self).get_context_data(**kwargs)
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])

        context['page_title'] = 'Modyfikacja'
        context['header_text'] = 'Nowa modyfikacja/naprawa dla %s' % aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = aircraft
        context['type'] = 'mods'

        return context

    def form_valid(self, form):
        form.instance.aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        return super(ModificationCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:aircraft-mods', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class ModificationUpdate (UpdateView):
    model = Modification
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        fields = ['description', 'done_date', 'done_hours', 'aso', 'done_crs', 'remarks']
        if self.object.aircraft.use_cycles:
            fields.insert(3, 'done_cycles')
        if self.object.aircraft.use_landings:
            fields.insert(3, 'done_landings')
        return modelform_factory(Modification, fields=fields,
                                 widgets={'description':TextInput(attrs={'size':100}),
                                          'done_date':AdminDateWidget(),
                                          'remarks':Textarea(attrs={'rows':2, 'cols':100})})

    def get_context_data(self, **kwargs):
        context = super(ModificationUpdate, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Aktualizacja modyfikacji lub naprawy dla %s' % self.object.aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'mods'

        return context

    def get_success_url(self):
        return reverse('camo:aircraft-mods', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class ModificationDelete (DeleteView):
    model = Modification
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(ModificationDelete, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Usunięcie modyfikacji lub naprawy dla %s' % self.object.aircraft

        return context

    def get_success_url(self):
        return reverse('camo:aircraft-mods', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class WBDetails (DetailView):
    model = WB_report
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(WBDetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o raporcie W&B dla %s' % self.object.aircraft
        context['header_width'] = '120px'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'wbs'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:wb-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('camo:wb-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Wybór właściwych jednostek
        if self.object.unit == 'USA':
            mas_u, len_u, mom_u = 'lb', 'in', 'lb*in'
        else:
            mas_u, len_u, mom_u = 'kg', 'm', 'kg*m'

        field_list = []
        field_list.append({'header': 'Statek powietrzny', 'value': self.object.aircraft, 'bold': True})
        field_list.append({'header': 'Opis', 'value': self.object.description})
        field_list.append({'header': 'Doc ref.', 'value': self.object.doc_ref})
        field_list.append({'header': 'Zmiana masy', 'value': '%.2f %s' % (self.object.mass_change, mas_u)})
        field_list.append({'header': 'Masa pustego', 'value': '%.2f %s' % (self.object.empty_weight, mas_u)})
        if self.object.lon_cg:
            field_list.append({'header': 'Lon C.G.', 'value': '%.2f %s' % (self.object.lon_cg, len_u)})
        if self.object.lat_cg:
            field_list.append({'header': 'Lat C.G.', 'value': '%.2f %s' % (self.object.lat_cg, len_u)})
        if self.object.empty_weight and self.object.lon_cg:
            field_list.append({'header': 'Lon moment', 'value': '%.2f %s' % (self.object.empty_weight * self.object.lon_cg, mom_u)})
        if self.object.empty_weight and self.object.lat_cg:
            field_list.append({'header': 'Lat moment', 'value': '%.2f %s' % (self.object.empty_weight * self.object.lat_cg, mom_u)})
        field_list.append({'header': 'Wykonano (data)', 'value': self.object.done_date})
        field_list.append({'header': 'Wykonano (TTH)', 'value': self.object.done_hours})
        if self.object.aircraft.use_landings:
            field_list.append({'header': 'Wykonano (lądowania)', 'value': self.object.done_landings})
        if self.object.aircraft.use_cycles:
            field_list.append({'header': 'Wykonano (cykle)', 'value': self.object.done_cycles})
        field_list.append({'header': 'Organizacja', 'value': self.object.aso})
        field_list.append({'header': 'CRS Ref.', 'value': self.object.done_doc})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class WBCreate (CreateView):
    model = WB_report
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        fields = ['description', 'doc_ref', 'unit', 'mass_change', 'empty_weight', 'lon_cg', 'lat_cg',
                  'done_date', 'done_hours', 'aso', 'done_doc', 'remarks']
        if aircraft.use_cycles:
            fields.insert(10, 'done_cycles')
        if aircraft.use_landings:
            fields.insert(10, 'done_landings')
        form_class = modelform_factory(WB_report, fields=fields,
                                       widgets={'description':TextInput(attrs={'size':100}),
                                                'done_date':AdminDateWidget(),
                                                'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        form_class.base_fields['done_date'].initial = date.today()
        form_class.base_fields['done_hours'].initial = aircraft.hours_count
        if aircraft.use_landings:
            form_class.base_fields['done_landings'].initial = aircraft.landings_count
        if aircraft.use_cycles:
            form_class.base_fields['done_cycles'].initial = aircraft.cycles_count
        return form_class

    def get_context_data(self, **kwargs):
        context = super(WBCreate, self).get_context_data(**kwargs)
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])

        context['page_title'] = 'Raport W&B'
        context['header_text'] = 'Nowy raport W&B dla %s' % aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = aircraft
        context['type'] = 'wbs'

        return context

    def form_valid(self, form):
        form.instance.aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        return super(WBCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:aircraft-wbs', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class WBUpdate (UpdateView):
    model = WB_report
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        fields = ['description', 'doc_ref', 'unit', 'mass_change', 'empty_weight', 'lon_cg', 'lat_cg',
                  'done_date', 'done_hours', 'aso', 'done_doc', 'remarks']
        if self.object.aircraft.use_cycles:
            fields.insert(10, 'done_cycles')
        if self.object.aircraft.use_landings:
            fields.insert(10, 'done_landings')
        form_class = modelform_factory(WB_report, fields=fields,
                                       widgets={'description':TextInput(attrs={'size':100}),
                                                'done_date':AdminDateWidget(),
                                                'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        return form_class

    def get_context_data(self, **kwargs):
        context = super(WBUpdate, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Aktualizacja raportu W&B dla %s' % self.object.aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'wbs'

        return context

    def get_success_url(self):
        return reverse('camo:aircraft-wbs', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class WBDelete (DeleteView):
    model = WB_report
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(WBDelete, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Usunięcie raportu W&B dla %s' % self.object.aircraft
        return context

    def get_success_url(self):
        return reverse('camo:aircraft-wbs', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class MSDetails (DetailView):
    model = MS_report
    template_name = 'camo/ms.html'

    # Kontekst dla raportu MS dla SP #
    def get_context_data(self, **kwargs):
        context = super(MSDetails, self).get_context_data(**kwargs)
        context['use_landings'] = self.object.aircraft.use_landings
        context['use_cycles'] = self.object.aircraft.use_cycles

        # Pozycja w bocznym menu
        context['type'] = 'ms'

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class MSCreate (CreateView):
    model = MS_report
    template_name = 'camo/create_template.html'

    def get_form_class(self, **kwargs):
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        fields = ['ms_ref', 'done_date', 'done_hours', 'crs_ref', 'crs_date', 'next_date', 'next_hours', 'remarks']
        if aircraft.use_cycles:
            fields.insert(7, 'next_cycles')
        if aircraft.use_landings:
            fields.insert(7, 'next_landings')
        if aircraft.use_cycles:
            fields.insert(3, 'done_cycles')
        if aircraft.use_landings:
            fields.insert(3, 'done_landings')
        form_class = modelform_factory(MS_report, fields=fields,
                                       widgets={'done_date':AdminDateWidget(),
                                                'next_date':AdminDateWidget(),
                                                'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        form_class.base_fields['done_date'].initial = date.today()
        form_class.base_fields['done_hours'].initial = aircraft.hours_count
        if aircraft.use_landings:
            form_class.base_fields['done_landings'].initial = aircraft.landings_count
        if aircraft.use_cycles:
            form_class.base_fields['done_cycles'].initial = aircraft.cycles_count
        form_class.base_fields['next_date'].initial = aircraft.next_date()
        form_class.base_fields['next_hours'].initial = aircraft.next_hours()
        if aircraft.use_landings:
            form_class.base_fields['next_landings'].initial = aircraft.next_landings()
        if aircraft.use_cycles:
            form_class.base_fields['next_cycles'].initial = aircraft.next_cycles()
        return form_class

    def get_context_data(self, **kwargs):
        context = super(MSCreate, self).get_context_data(**kwargs)
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])

        context['page_title'] = 'Świadectwo MS'
        context['header_text'] = 'Nowe świadectwo MS dla %s' % aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = aircraft
        context['type'] = 'ms'

        return context

    def form_valid(self, form):
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        form.instance.aircraft = aircraft
        if aircraft.airframe():
            form.instance.fuselage = aircraft.airframe().serial_no
        if len(aircraft.engines()) > 0:
            form.instance.engine1 = aircraft.engines()[0].serial_no
        if len(aircraft.engines()) > 1:
            form.instance.engine2 = aircraft.engines()[1].serial_no

        return super(MSCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:ms-details', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class MSUpdate (UpdateView):
    model = MS_report
    template_name = 'camo/update_template.html'

    def get_form_class(self, **kwargs):
        fields = ['ms_ref', 'done_date', 'done_hours', 'crs_ref', 'crs_date', 'next_date', 'next_hours', 'remarks']
        if self.object.aircraft.use_cycles:
            fields.insert(7, 'next_cycles')
        if self.object.aircraft.use_landings:
            fields.insert(7, 'next_landings')
        if self.object.aircraft.use_cycles:
            fields.insert(3, 'done_cycles')
        if self.object.aircraft.use_landings:
            fields.insert(3, 'done_landings')
        form_class = modelform_factory(MS_report, fields=fields,
                                       widgets={'done_date':AdminDateWidget(),
                                                'next_date':AdminDateWidget(),
                                                'remarks':Textarea(attrs={'rows':2, 'cols':100})})

        # form_class.base_fields['done_hours'].widget.attrs['readonly'] = True
        # form_class.base_fields['done_landings'].widget.attrs['readonly'] = True

        return form_class

    def get_context_data(self, **kwargs):
        context = super(MSUpdate, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Aktualizacja świadectwa MS dla %s' % self.object.aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'ms'

        return context

    def get_success_url(self):
        return reverse('camo:ms-details', args=[self.object.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class MSDelete (DeleteView):
    model = MS_report
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(MSDelete, self).get_context_data(**kwargs)

        context['page_title'] = self.object
        context['header_text'] = 'Usunięcie świadectwa MS dla %s' % self.object.aircraft

        return context

    def get_success_url(self):
        return reverse('camo:aircraft-ms', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class OperDetails (DetailView):
    model = CAMO_operation
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(OperDetails, self).get_context_data(**kwargs)

        # Informacje nagłówkowe
        context['page_title'] = 'Operacja'
        context['header_text'] = 'Szczegóły operacji'
        context['header_width'] = '150px'
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'opers'


        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:oper-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('camo:oper-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        if self.object.pdt:
            field_list.append({'header': 'Numer PDT', 'value': "%06d" % self.object.pdt.pdt_ref,
                               'link': reverse('panel:pdt-info', args=[self.object.pdt.pk])})
        else:
            field_list.append({'header': 'Numer PDT', 'value': self.object.pdt_ref})
        field_list.append({'header': 'Data operacji', 'value': self.object.date})
        field_list.append({'header': 'Licznik początkowy', 'value': self.object.tth_start})
        field_list.append({'header': 'Licznik końcowy', 'value': self.object.tth_end})
        field_list.append({'header': 'Liczba lądowań', 'value': self.object.landings})
        if self.object.aircraft.use_cycles:
            field_list.append({'header': 'Liczba cykli', 'value': self.object.cycles})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list
        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class OperCreate (CreateView):
    model = CAMO_operation
    template_name = 'camo/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(OperCreate, self).get_context_data(**kwargs)
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])

        context['page_title'] = 'Rejestracja operacji'
        context['header_text'] = 'Rejestracja operacji dla %s' % aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = aircraft
        context['type'] = 'opers'

        return context

    def get_form_class(self, **kwargs):
        aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        fields = ['pdt_ref', 'date', 'tth_start', 'tth_end', 'landings', 'remarks']
        if aircraft.use_cycles:
            fields.insert(5, 'cycles')
        form_class = modelform_factory(CAMO_operation, fields=fields)

        class create_form(form_class):
            def clean_tth_end(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data['tth_end'] <= cleaned_data['tth_start']:
                    raise ValidationError('Licznik końcowy musi być większy niż początkowy!', code='tth_negative')
                # if cleaned_data['tth_end'] - cleaned_data['tth_start'] > 10:
                #     raise ValidationError('Operacja nie może trwać powyżej 10h!', code='tth_too_big')
                return cleaned_data['tth_end']

            def clean_landings(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data['landings'] < 0:
                    raise ValidationError('Liczba lądowań nie może być mniejsza od zera!', code='landings_zero')
                if cleaned_data['landings'] > 99:
                    raise ValidationError('Zbyt duża liczba lądowań!', code='landings_too_big')
                return cleaned_data['landings']

            def clean_cycles(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data['cycles'] < 0:
                    raise ValidationError('Liczba cykli nie może być mniejsza od zera!', code='cycles_zero')
                if cleaned_data['cycles'] > 99:
                    raise ValidationError('Zbyt duża liczba cykli!', code='cycles_too_big')
                return cleaned_data['cycles']

        create_form.base_fields['date'].initial = date.today()
        create_form.base_fields['date'].widget = AdminDateWidget()
        create_form.base_fields['tth_start'].initial = aircraft.tth
        create_form.base_fields['landings'].initial = 1
        if aircraft.use_cycles:
            create_form.base_fields['cycles'].initial = 0
        create_form.base_fields['remarks'].widget = Textarea(attrs={'rows':4, 'cols':100})
        return create_form

    def form_valid(self, form):
        form.instance.aircraft = get_object_or_404(Aircraft, pk=self.kwargs['aircraft_id'])
        return super(OperCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:aircraft-opers', args=[self.kwargs['aircraft_id']])


@class_view_decorator(permission_required('camo.camo_admin'))
class OperUpdate (UpdateView):
    model = CAMO_operation
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(OperUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Modyfikacja operacji'
        context['header_text'] = 'Modyfikacja operacji dla %s' % self.object.aircraft
        context['submenu_template'] = 'camo/aircraft_submenu.html'
        context['object'] = self.object.aircraft
        context['type'] = 'opers'

        return context

    def get_form_class(self, **kwargs):
        fields = ['pdt_ref', 'date', 'tth_start', 'tth_end', 'landings', 'remarks']
        if self.object.aircraft.use_cycles:
            fields.insert(5, 'cycles')
        form_class = modelform_factory(CAMO_operation, fields=fields)

        class update_form(form_class):
            def clean_tth_end(self):
                cleaned_data = super(update_form, self).clean()
                if cleaned_data.get('tth_start') and cleaned_data.get('tth_end'):
                    if cleaned_data['tth_end'] <= cleaned_data['tth_start']:
                        raise ValidationError(('Licznik końcowy musi być większy niż początkowy!'), code='tth_negative')
                    if cleaned_data['tth_end'] - cleaned_data['tth_start'] > 10:
                        raise ValidationError(('Operacja nie może trwać powyżej 10h!'), code='tth_too_big')
                return cleaned_data['tth_end']

            def clean_landings(self):
                cleaned_data = super(update_form, self).clean()
                if cleaned_data['landings'] < 0:
                    raise ValidationError(('Liczba lądowań nie może być mniejsza od zera!'), code='landings_zero')
                if cleaned_data['landings'] > 99:
                    raise ValidationError(('Zbyt duża liczba lądowań!'), code='landings_too_big')
                return cleaned_data['landings']

            def clean_cycles(self):
                cleaned_data = super(update_form, self).clean()
                if cleaned_data['cycles'] < 0:
                    raise ValidationError('Liczba cykli nie może być mniejsza od zera!', code='cycles_zero')
                if cleaned_data['cycles'] > 99:
                    raise ValidationError('Zbyt duża liczba cykli!', code='cycles_too_big')
                return cleaned_data['cycles']

        update_form.base_fields['date'].widget = AdminDateWidget()
        update_form.base_fields['remarks'].widget = Textarea(attrs={'rows':4, 'cols':100})
        return update_form

    def get_success_url(self):
        return reverse('camo:aircraft-opers', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class OperDelete (DeleteView):
    model = CAMO_operation
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(OperDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie operacji'
        context['header_text'] = 'Usunięcie operacji dla %s' % self.object.aircraft
        return context

    def get_success_url(self):
        return reverse('camo:aircraft-opers', args=[self.object.aircraft.pk])


@class_view_decorator(permission_required('camo.camo_reader'))
class PDTControlList (ListView):
    model = PDT
    template_name = 'camo/list_template.html'

    # Posortuj listę niezatwierdzonych PDT po datach
    def get_queryset(self):
        return PDT.objects.exclude(status='checked').order_by('-date', '-tth_start')

    def get_context_data(self, **kwargs):
        context = super(PDTControlList, self).get_context_data(**kwargs)
        context['page_title'] = 'Kontrola PDT'
        context['header_text'] = 'Lista niezatwierdzonych PDT'
        context['empty_text'] = 'Brak PDT do zatwierdzenia.'

        # Lokalne menu
        local_menu = []
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Statek\npowietrzny'})
        header_list.append({'header': 'PDT ref'})
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'Rodzaj lotu'})
        header_list.append({'header': 'PIC'})
        header_list.append({'header': 'SIC'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': 'Status'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'aircraft', 'value': object.aircraft, 'just': 'center'})
            fields.append({'name': 'pdt_ref', 'value': '{:0>6d}'.format(object.pdt_ref),
                           'link': reverse('camo:pdt-info', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'date', 'value': object.date})
            fields.append({'name': 'flight_type', 'value': object.flight_type_name})
            fields.append({'name': 'pic', 'value': object.pic})
            fields.append({'name': 'sic', 'value': object.sic})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'status', 'value': object.status_name(), 'just': 'center', 'color': object.status_color()})
            fields.append({'name': 'change', 'report_link': (reverse('panel:pdt-form', args=[object.pk]))})

            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_reader'))
class PDTControlInfo (DetailView):
    model = PDT
    template_name = 'camo/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTControlInfo, self).get_context_data(**kwargs)
        context['page_title'] = 'PDT'
        context['header_text'] = 'Informacje o PDT'
        context['type'] = 'info'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Drukuj', 'path': reverse('panel:pdt-form', args=[self.object.pk])})
        if self.request.user.has_perm('camo.camo_admin'):
            open_oper = self.object.operation_set.filter(status='open').first()
            if self.object.status == 'open' and not open_oper:
                local_menu.append({'text': 'Zamknij PDT', 'path': reverse('camo:pdt-close', args=[self.object.pk])})
            local_menu.append({'text': 'Aktualizuj', 'path': reverse('camo:pdt-update', args=[self.object.pk])})
            local_menu.append({'text': 'Usuń', 'path': reverse('camo:pdt-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Statek powietrzny', 'value': '%s / %s' % (self.object.aircraft, self.object.aircraft.type), 'bold': True})
        field_list.append({'header': 'Numer PDT', 'value': '{:0>6d}'.format(self.object.pdt_ref), 'bold': True})
        field_list.append({'header': 'Data PDT', 'value': self.object.date})
        field_list.append({'header': 'Typ lotu', 'value': self.object.flight_type_name()})
        field_list.append({'header': 'Pierwszy pilot', 'value': self.object.pic})
        field_list.append({'header': 'Drugi pilot', 'value': self.object.sic})
        field_list.append({'header': 'Suma czasu', 'value': '%.2d:%.2d' % (self.object.hours_sum()[1], self.object.hours_sum()[2])})
        field_list.append({'header': 'Suma TTH', 'value': self.object.tth_sum()})
        field_list.append({'header': 'Suma lądowań', 'value': self.object.landings_sum()})
        if self.object.aircraft.use_cycles:
            field_list.append({'header': 'Suma cykli', 'value': self.object.cycles_sum()})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        field_list.append({'header': 'Otwarty przez', 'value': '%s - %s UTC' % (self.object.open_user, self.object.open_time.strftime('%x %X'))})
        if self.object.close_user:
            field_list.append({'header': 'Zamknięty przez', 'value': '%s - %s UTC' % (self.object.close_user, self.object.close_time.strftime('%x %X'))})
        if self.object.check_user:
            field_list.append({'header': 'Sprawdzony przez', 'value': '%s - %s UTC' % (self.object.check_user, self.object.check_time.strftime('%x %X'))})

        context['field_list'] = field_list
        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class PDTControlUpdate (UpdateView):
    model = PDT
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTControlUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Aktualizacja PDT'
        context['header_text'] = 'Aktualizacja informacji na PDT'
        context['type'] = 'info'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object

        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(PDT, exclude=('aircraft', 'status', 'open_time', 'open_user',
                                                     'close_time', 'close_user', 'check_time', 'check_user'),
                                            widgets={'date':AdminDateWidget(), 'remarks':Textarea(attrs={'rows':2, 'cols':100}),
                                                     'failure_desc': Textarea(attrs={'rows': 2, 'cols': 100}),
                                                     'repair_desc': Textarea(attrs={'rows': 2, 'cols': 100}),
                                                     'ext_voucher':TextInput(attrs={'size':102}),
                                                     'service_remarks':Textarea(attrs={'rows':2, 'cols':100})})

        form_class.base_fields['date'].initial = date.today()

        ms_list = [(ms.pk, ms) for ms in MS_report.objects.filter(aircraft=self.object.aircraft)]
        form_class.base_fields['ms_report'].choices = [(None, '---------')] + ms_list

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in FuelTank.objects.filter(fuel_type=self.object.aircraft.fuel_type)]
        form_class.base_fields['fuel_after_source'].widget = forms.Select(choices= fuel_tanks + [("other", "-- Poza SALT --")])

        return form_class

    def get_success_url(self):
        return reverse('camo:pdt-info', args=(self.object.pk,))


@class_view_decorator(permission_required('camo.camo_admin'))
class PDTControlDelete (DeleteView):
    model = PDT
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTControlDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie PDT'
        context['header_text'] = 'Usunięcie PDT'
        context['type'] = 'info'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object
        return context

    def get_success_url(self):
        return reverse('camo:pdt-list')


@class_view_decorator(permission_required('camo.camo_reader'))
class PDTControlOperations (DetailView):
    model = PDT
    template_name = 'camo/list_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTControlOperations, self).get_context_data(**kwargs)
        context['page_title'] = 'PDT'
        context['header_text'] = 'Operacje na PDT'
        context['empty_text'] = 'Brak zarejestrowanych operacji.'
        context['type'] = 'oper'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object

        oper_list = self.object.operation_set.order_by('operation_no')

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Drukuj', 'path': reverse('panel:pdt-form', args=[self.object.pk])})
        last_open = self.object.operation_set.filter(status='open').first()
        if self.request.user.has_perm('camo.camo_admin') and not last_open:
            local_menu.append({'text': 'Dodaj nową operację', 'path': reverse("camo:pdt-oper-create", args=[self.object.pk])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nr.'})
        header_list.append({'header': 'Miejsce\nstartu'})
        header_list.append({'header': 'Miejsce\nlądowania'})
        header_list.append({'header': 'Czas\nstartu'})
        header_list.append({'header': 'Czas\nlądowania'})
        header_list.append({'header': 'TTH\nstartu'})
        header_list.append({'header': 'TTH\nlądowania'})
        header_list.append({'header': 'Liczba\nlądowań'})
        if self.object.aircraft.use_cycles:
            header_list.append({'header': 'Liczba\ncykli'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in oper_list:
            fields = []
            fields.append({'name': 'number', 'value': object.operation_no, 'just': 'center'})
            fields.append({'name': 'loc_start', 'value': object.loc_start, 'just': 'center'})
            fields.append({'name': 'loc_end', 'value': object.loc_end if object.loc_end else '---', 'just': 'center'})
            fields.append({'name': 'time_start', 'value': object.time_start.strftime('%H:%M') if object.time_start else '---', 'just': 'center'})
            fields.append({'name': 'time_end', 'value': object.time_end.strftime('%H:%M') if object.time_end else '---', 'just': 'center'})
            fields.append({'name': 'tth_start', 'value': object.tth_start, 'just': 'center'})
            fields.append({'name': 'tth_end', 'value': object.tth_end if object.tth_end else '---', 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings, 'just': 'center'})
            if self.object.aircraft.use_cycles:
                fields.append({'name': 'cycles', 'value': object.cycles, 'just': 'center'})
            if self.request.user.has_perm('camo.camo_admin'):
                fields.append({'name': 'change', 'edit_link': reverse('camo:pdt-oper-update', args=[object.pk]),
                               'delete_link': reverse('camo:pdt-oper-delete', args=[object.pk])})
            else:
                fields.append({'name': 'change', 'value': ''})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('camo.camo_admin'))
class PDTOperCreate (CreateView):
    model = Operation
    template_name = 'camo/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTOperCreate, self).get_context_data(**kwargs)
        pdt = get_object_or_404(PDT, pk=self.kwargs['pdt_id'])

        context['page_title'] = 'Nowa operacja'
        context['header_text'] = 'Nowa operacja na PDT %s' % pdt
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['type'] = 'oper'
        context['pdt'] = pdt

        return context

    def get_form_class(self, **kwargs):
        pdt = get_object_or_404(PDT, pk=self.kwargs['pdt_id'])

        fields = ['loc_start', 'loc_end', 'time_start', 'time_end', 'tth_start', 'tth_end', 'landings',
                  'fuel_available', 'fuel_used', 'fuel_refill', 'fuel_source', 'oil_refill', 'trans_oil_refill',
                  'hydr_oil_refill', 'pax', 'bags']
        if pdt.aircraft.use_cycles:
            fields.insert(7, 'cycles')

        form_class = modelform_factory(Operation, fields=fields)

        class create_form(form_class):
            def clean_tth_end(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data.get('tth_start') and cleaned_data.get('tth_end'):
                    if cleaned_data['tth_end'] <= cleaned_data['tth_start']:
                        raise ValidationError('Licznik końcowy musi być większy niż początkowy!', code='tth_negative')
                return cleaned_data['tth_end']

            def clean_landings(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data['landings'] < 0:
                    raise ValidationError('Liczba lądowań nie może być mniejsza od zera!', code='landings_zero')
                return cleaned_data['landings']

            def clean_cycles(self):
                cleaned_data = super(create_form, self).clean()
                if cleaned_data['cycles'] < 0:
                    raise ValidationError('Liczba cykli nie może być mniejsza od zera!', code='cycles_zero')
                return cleaned_data['cycles']

        create_form.base_fields['landings'].initial = 1
        if pdt.aircraft.use_cycles:
            create_form.base_fields['cycles'].initial = 0

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in
                      FuelTank.objects.filter(fuel_type=pdt.aircraft.fuel_type)]
        fuel_tanks += [("other", "-- Poza SALT --")]

        create_form.base_fields['loc_start'].required = True
        create_form.base_fields['loc_end'].required = True
        create_form.base_fields['time_start'].required = True
        create_form.base_fields['time_end'].required = True
        create_form.base_fields['tth_start'].required = True
        create_form.base_fields['tth_end'].required = True
        create_form.base_fields['fuel_used'].required = True
        create_form.base_fields['fuel_source'].widget = forms.Select(choices=fuel_tanks)

        return create_form

    def form_valid(self, form):
        pdt = get_object_or_404(PDT, pk=self.kwargs['pdt_id'])
        form.instance.pdt = pdt
        last_operation = pdt.operation_set.order_by('operation_no').last()
        if last_operation:
            form.instance.operation_no = last_operation.operation_no + 1
        else:
            form.instance.operation_no = 1
        form.instance.status = 'closed'
        return super(PDTOperCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:pdt-oper', args=[self.kwargs['pdt_id']])


@class_view_decorator(permission_required('camo.camo_admin'))
class PDTOperUpdate (UpdateView):
    model = Operation
    template_name = 'camo/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTOperUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Modyfikacja operacji'
        context['header_text'] = 'Modyfikacja operacji na PDT'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object.pdt
        context['type'] = 'oper'

        return context

    def get_form_class(self, **kwargs):
        fields = ['loc_start', 'loc_end', 'time_start', 'time_end', 'tth_start', 'tth_end', 'landings',
                  'fuel_available', 'fuel_used', 'fuel_refill', 'fuel_source', 'oil_refill', 'trans_oil_refill',
                  'hydr_oil_refill', 'pax', 'bags']
        if self.object.pdt.aircraft.use_cycles:
            fields.insert(7, 'cycles')

        fuel_tanks = [("SALT %d" % tank.pk, tank.name) for tank in
                      FuelTank.objects.filter(fuel_type=self.object.pdt.aircraft.fuel_type)]
        fuel_tanks += [("other", "-- Poza SALT --")]

        form_class = modelform_factory(Operation, fields=fields)

        form_class.base_fields['loc_start'].required = True
        form_class.base_fields['loc_end'].required = True
        form_class.base_fields['time_start'].required = True
        form_class.base_fields['time_end'].required = True
        form_class.base_fields['tth_start'].required = True
        form_class.base_fields['tth_end'].required = True
        form_class.base_fields['fuel_used'].required = True
        form_class.base_fields['fuel_source'].widget = forms.Select(choices=fuel_tanks)

        return form_class

    def form_valid(self, form):
        form.instance.status = 'closed'
        return super(PDTOperUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('camo:pdt-oper', args=[self.object.pdt.pk])


@class_view_decorator(permission_required('camo.camo_admin'))
class PDTOperDelete (DeleteView):
    model = Operation
    template_name = 'camo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PDTOperDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie operacji'
        context['header_text'] = 'Usunięcie operacji na PDT'
        context['submenu_template'] = 'camo/pdt_submenu.html'
        context['pdt'] = self.object.pdt
        context['type'] = 'oper'
        return context

    def get_success_url(self):
        return reverse('camo:pdt-oper', args=[self.object.pdt.pk])


@permission_required('camo.camo_admin')
def PDTCheck (request, pdt_id):

    pdt = PDT.objects.get(pk = pdt_id)

    PDTCheckForm = forms.Form
    form = PDTCheckForm(request.POST or None)

    # wspólne zmienne kontekstowe
    context = {}
    context['pdt'] = pdt
    context['submenu_template'] = 'camo/pdt_submenu.html'
    context['type'] = 'check'
    context['form'] = form

    # jeśli formularz został poprawnie wypełniony
    if form.is_valid():

        # Zatwierdzenie PDT
        pdt.status = 'checked'
        pdt.check_user = request.user.fbouser
        pdt.check_time = timezone.now()
        pdt.full_clean()
        pdt.save()

        # przejście do kolejnego formularza
        return HttpResponseRedirect(reverse('camo:pdt-list'))

    return render(request, 'camo/pdt_check.html', context)
