# -*- coding: utf-8 -*-

import datetime
from datetime import date
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.forms.models import modelform_factory
from django.forms import Textarea, TextInput, Form
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test

from django.utils.decorators import method_decorator
def class_view_decorator(function_decorator):

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator

from salt.forms import duration_string

from ato.models import Training, Phase, Exercise, Instructor, Student
from ato.models import Training_inst, Phase_inst, Exercise_inst, Exercise_oper, Card_entry
from panel.models import PDT, Operation, Pilot
from ato.forms import ExercOperCreateForm

@class_view_decorator(permission_required('ato.ato_reader'))
class TrainingList (ListView):
    model = Training
    template_name = 'ato/list_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingList, self).get_context_data(**kwargs)
        context['page_title'] = 'Programy'
        context['header_text'] = 'Programy szkoleń SALT'
        context['empty_text'] = 'Brak programów szkoleń.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowy program', 'path': reverse("ato:training-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Kod'})
        header_list.append({'header': 'Nazwa', 'width': '220px'})
        header_list.append({'header': 'Data\nwprowadz.'})
        header_list.append({'header': 'Opis'})
        header_list.append({'header': '...', 'width': '40px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'code', 'value': object.code, 'link': reverse('ato:training-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'name', 'value': object.name})
            fields.append({'name': 'name', 'value': object.date, 'just': 'center'})
            fields.append({'name': 'description', 'value': object.description})
            fields.append({'name': 'change', 'edit_link': reverse('ato:training-update', args=[object.pk]),
                           'delete_link': (reverse('ato:training-delete', args=[object.pk]) if not object.training_inst_set.all() else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_reader'))
class TrainingDetails (DetailView):
    model = Training
    template_name = 'ato/training_details.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły programu szkolenia'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:training-update', args=[self.object.pk])})
        # Jeśli nie ma realizowanych szkoleń tego rodzaju to można usunąć
        if not self.object.training_inst_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('ato:training-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod szkolenia', 'value': self.object.code, 'bold': True})
        field_list.append({'header': 'Nazwa szkolenia', 'value': self.object.name})
        field_list.append({'header': 'Data wprowadzenia', 'value': self.object.date})
        field_list.append({'header': 'Opis szkolenia', 'value': self.object.description})
        context['field_list'] = field_list
        context['header_width'] = '140px'

        # Subsekcja z fazami
        context['phase_header_text'] = 'Zadania/fazy w ramach %s' % self.object
        context['phase_create_path'] = reverse('ato:phase-create', args=[self.object.pk])
        context['phase_create_text'] = 'Nowe zadanie/faza'
        context['phase_empty_text'] = 'Brak zadań/faz dla szkolenia.'

        phase_header_list = []
        phase_header_list.append({'header': 'Kod'})
        phase_header_list.append({'header': 'Nazwa'})
        # phase_header_list.append({'header': 'Opis'})
        phase_header_list.append({'header': 'Poprzednik'})
        phase_header_list.append({'header': 'Min. godzin\nz instr.'})
        phase_header_list.append({'header': 'Min. godzin\n solo'})
        phase_header_list.append({'header': '...'})
        context['phase_header_list'] = phase_header_list

        row_list = []
        for phase in self.object.phase_set.order_by('code'):
            fields = []
            fields.append({'name': 'code', 'value': phase.code, 'link': reverse('ato:phase-details', args=[phase.pk]), 'just': 'center'})
            fields.append({'name': 'name', 'value': phase.name})
            # fields.append({'name': 'description', 'value': phase.description})
            fields.append({'name': 'predecessor', 'value': (phase.predecessor or '---')})
            fields.append({'name': 'min_time_instr', 'value': duration_string(phase.min_time_instr) if phase.min_time_instr else '---', 'just': 'center'})
            fields.append({'name': 'min_time_solo', 'value': duration_string(phase.min_time_solo) if phase.min_time_solo else '---', 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('ato:phase-update', args=[phase.pk]),
                           'delete_link': reverse('ato:phase-delete', args=[phase.pk])})
            row_list.append({'fields': fields})
        context['phase_row_list'] = row_list
        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class TrainingCreate (CreateView):
    model = Training
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowy program'
        context['header_text'] = 'Utworzenie nowego programu'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Training, fields='__all__',
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        return form_class

    def get_success_url(self):
        return reverse('ato:training-list')


@class_view_decorator(permission_required('ato.ato_admin'))
class TrainingUpdate (UpdateView):
    model = Training
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana programu'
        context['header_text'] = 'Zmiana programu szkolenia'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Training, fields='__all__',
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        return form_class

    def get_success_url(self):
        return reverse('ato:training-list')


@class_view_decorator(permission_required('ato.ato_admin'))
class TrainingDelete (DeleteView):
    model = Training
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie programu'
        context['header_text'] = 'Usunięcie programu szkolenia'
        return context

    def get_success_url(self):
        return reverse('ato:training-list')


@class_view_decorator(permission_required('ato.ato_reader'))
class PhaseDetails (DetailView):
    model = Phase
    template_name = 'ato/phase_details.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły zadania/fazy dla %s' % self.object.training

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:phase-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:phase-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod szkolenia', 'value': self.object.training.code, 'bold': True})
        field_list.append({'header': 'Kod zadania/fazy', 'value': self.object.code, 'bold': True})
        field_list.append({'header': 'Nazwa zadania/fazy', 'value': self.object.name})
        field_list.append({'header': 'Opis zadania/fazy', 'value': self.object.description})
        field_list.append({'header': 'Poprzednik', 'value': self.object.predecessor})
        field_list.append({'header': 'Min. godzin z instr.', 'value': duration_string(self.object.min_time_instr) if self.object.min_time_instr else ''})
        field_list.append({'header': 'Min. godzin solo', 'value': duration_string(self.object.min_time_solo) if self.object.min_time_solo else ''})
        context['field_list'] = field_list
        context['header_width'] = '130px'

        context['exercise_header_text'] = 'Cwiczenia w ramach %s' % self.object
        context['exercise_create_path'] = reverse('ato:exercise-create', args=[self.object.pk])
        context['exercise_create_text'] = 'Nowe ćwiczenie'
        context['exercise_empty_text'] = 'Brak ćwiczeń dla zadania/fazy.'

        exercise_header_list = []
        exercise_header_list.append({'header': 'Kod'})
        exercise_header_list.append({'header': 'Nazwa'})
        # exercise_header_list.append({'header': 'Opis'})
        exercise_header_list.append({'header': 'Poprzednik'})
        exercise_header_list.append({'header': 'Restrykcje'})
        exercise_header_list.append({'header': 'Min. godzin\nz instr.'})
        exercise_header_list.append({'header': 'Min. godzin\n solo'})
        exercise_header_list.append({'header': 'Min. lotów\nz instr.'})
        exercise_header_list.append({'header': 'Min. lotów\n solo'})
        exercise_header_list.append({'header': '...'})
        context['exercise_header_list'] = exercise_header_list

        row_list = []
        for exercise in self.object.exercise_set.order_by('code'):
            fields = []
            fields.append({'name': 'code', 'value': exercise.code, 'link': reverse('ato:exercise-details', args=[exercise.pk]), 'just': 'center'})
            fields.append({'name': 'name', 'value': exercise.name})
            fields.append({'name': 'predecessor', 'value': (exercise.predecessor or '---')})
            fields.append({'name': 'restrictions', 'value': exercise.restrictions, 'just': 'center'})
            fields.append({'name': 'min_time_instr', 'value': duration_string(exercise.min_time_instr) if exercise.min_time_instr else '---', 'just': 'center'})
            fields.append({'name': 'min_time_solo', 'value': duration_string(exercise.min_time_solo) if exercise.min_time_solo else '---', 'just': 'center'})
            fields.append({'name': 'min_num_instr', 'value': (exercise.min_num_instr or '---'), 'just': 'center'})
            fields.append({'name': 'min_num_solo', 'value': (exercise.min_num_solo or '---'), 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('ato:exercise-update', args=[exercise.pk]),
                           'delete_link': reverse('ato:exercise-delete', args=[exercise.pk])})
            row_list.append({'fields': fields})
        context['exercise_row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseCreate(CreateView):
    model = Phase
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseCreate, self).get_context_data(**kwargs)
        training = get_object_or_404(Training, pk=self.kwargs['training_id'])
        context['page_title'] = 'Nowe zadanie/faza'
        context['header_text'] = 'Utworzenie nowego zadania/fazy dla %s' % training
        return context

    def get_form_class(self, **kwargs):
        phases = Phase.objects.filter(training = self.kwargs['training_id'])
        form_class = modelform_factory(Phase, exclude=['training'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        form_class.base_fields['predecessor'].choices = [(str(phase.pk), phase) for phase in phases]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def form_valid(self, form):
        form.instance.training = get_object_or_404(Training, pk=self.kwargs['training_id'])
        return super(PhaseCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('ato:training-details', args=[self.kwargs['training_id']])


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseUpdate (UpdateView):
    model = Phase
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana zadania/fazy'
        context['header_text'] = 'Zmiana zadania/fazy dla %s' % self.object.training
        return context

    def get_form_class(self, **kwargs):
        phases = Phase.objects.filter(training = self.object.training).exclude(pk = self.object.pk)
        form_class = modelform_factory(Phase, exclude=['training'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        form_class.base_fields['predecessor'].choices = [(str(phase.pk), phase) for phase in phases]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def get_success_url(self):
        return reverse('ato:training-details', args=[self.object.training.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseDelete (DeleteView):
    model = Phase
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie zadania/fazy'
        context['header_text'] = 'Usunięcie zadania/fazy dla %s' % self.object.training
        return context

    def get_success_url(self):
        return reverse('ato:training-details', args=[self.object.training.pk])


@class_view_decorator(permission_required('ato.ato_reader'))
class ExerciseDetails (DetailView):
    model = Exercise
    template_name = 'ato/details_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły ćwiczenia dla %s' % self.object.phase

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:exercise-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:exercise-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod zadania/fazy', 'value': self.object.phase, 'bold': True})
        field_list.append({'header': 'Kod ćwiczenia', 'value': self.object.code, 'bold': True})
        field_list.append({'header': 'Nazwa ćwiczenia', 'value': self.object.name})
        field_list.append({'header': 'Opis ćwiczenia', 'value': self.object.description})
        field_list.append({'header': 'Poprzednik', 'value': self.object.predecessor})
        field_list.append({'header': 'Restrykcje', 'value': self.object.restrictions})
        field_list.append({'header': 'Min. godzin z instr.', 'value': duration_string(self.object.min_time_instr) if self.object.min_time_instr else ''})
        field_list.append({'header': 'Min. godzin solo', 'value': duration_string(self.object.min_time_solo) if self.object.min_time_solo else ''})
        field_list.append({'header': 'Min. lotów z instr.', 'value': self.object.min_num_instr})
        field_list.append({'header': 'Min. lotów solo', 'value': self.object.min_num_solo})
        context['field_list'] = field_list
        context['header_width'] = '125px'
        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseCreate(CreateView):
    model = Exercise
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseCreate, self).get_context_data(**kwargs)
        phase = get_object_or_404(Phase, pk=self.kwargs['phase_id'])
        context['page_title'] = 'Nowe ćwiczenie'
        context['header_text'] = 'Utworzenie nowego ćwiczenia dla %s' % phase
        return context

    def get_form_class(self, **kwargs):
        exercises = Exercise.objects.filter(phase = self.kwargs['phase_id'])
        form_class = modelform_factory(Exercise, exclude=['phase'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        form_class.base_fields['predecessor'].choices = [(str(exercise.pk), exercise) for exercise in exercises]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def form_valid(self, form):
        form.instance.phase = get_object_or_404(Phase, pk=self.kwargs['phase_id'])
        return super(ExerciseCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('ato:phase-details', args=[self.kwargs['phase_id']])


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseUpdate (UpdateView):
    model = Exercise
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana ćwiczenia'
        context['header_text'] = 'Zmiana ćwiczenia dla %s' % self.object.phase
        return context

    def get_form_class(self, **kwargs):
        exercises = Exercise.objects.filter(phase = self.object.phase).exclude(pk = self.object.pk)
        form_class = modelform_factory(Exercise, exclude=['phase'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100})})
        form_class.base_fields['predecessor'].choices = [(str(exercise.pk), exercise) for exercise in exercises]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def get_success_url(self):
        return reverse('ato:phase-details', args=[self.object.phase.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseDelete (DeleteView):
    model = Exercise
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie ćwiczenia'
        context['header_text'] = 'Usunięcie ćwiczenia dla %s' % self.object.phase
        return context

    def get_success_url(self):
        return reverse('ato:phase-details', args=[self.object.phase.pk])


@class_view_decorator(permission_required('ato.ato_reader'))
class InstructorList (ListView):
    model = Instructor
    template_name = 'ato/list_template.html'

    def get_context_data(self, **kwargs):
        context = super(InstructorList, self).get_context_data(**kwargs)
        context['page_title'] = 'Instruktorzy'
        context['header_text'] = 'Lista instruktorów'
        context['empty_text'] = 'Brak zarejestrowanych instruktorów.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Zarejestruj nowego instruktora', 'path': reverse("ato:instr-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nazwisko\ni imię'})
        header_list.append({'header': 'Numer\ntelefonu'})
        header_list.append({'header': 'Adres\ne-mail'})
        header_list.append({'header': 'Restrykcje'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'name', 'value': object, 'link': reverse('ato:instr-info', args=[object.pk])})
            fields.append({'name': 'telephone', 'value': object.pilot.fbouser.telephone})
            fields.append({'name': 'email', 'value': object.pilot.fbouser.email, 'email': object.pilot.fbouser.email})
            fields.append({'name': 'restrictons', 'value': object.restrictions, 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:instr-update', args=[object.pk]),
                           'delete_link': (reverse('ato:instr-delete', args=[object.pk]) if not object.training_inst_set.all() else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list
        return context


@class_view_decorator(login_required())
class InstructorInfo (DetailView):
    model = Instructor
    template_name = 'ato/details_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(InstructorInfo, self).get_object()
        if not (self.request.user.is_staff or self.request.user.has_perm('ato.ato_reader')):
            obj = self.request.user.fbouser.pilot.instructor
        return obj

    def get_context_data(self, **kwargs):
        context = super(InstructorInfo, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o instruktorze %s' % self.object
        context['type'] = 'info'
        context['submenu_template'] = 'ato/instr_submenu.html'
        context['instructor'] = self.object

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:instr-update', args=[self.object.pk])})
        # Jeśli nie ma przypisanych szkoleń to można usunąć
        if not self.object.training_inst_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('ato:instr-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Nazwisko i imię', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Numer telefonu', 'value': self.object.pilot.fbouser.telephone})
        field_list.append({'header': 'Adres e-mail', 'value': self.object.pilot.fbouser.email, 'email': self.object.pilot.fbouser.email})
        field_list.append({'header': 'Restrykcje', 'value': self.object.restrictions})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        return context


@class_view_decorator(login_required())
class InstructorFlights (DetailView):
    model = Instructor
    template_name = 'ato/list_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(InstructorFlights, self).get_object()
        if not (self.request.user.is_staff or self.request.user.has_perm('ato.ato_reader')):
            obj = self.request.user.fbouser.pilot.instructor
        return obj

    def get_context_data(self, **kwargs):
        context = super(InstructorFlights, self).get_context_data(**kwargs)
        context['page_title'] = 'Loty szkoleniowe'
        context['header_text'] = 'Loty szkoleniowe instruktora %s' % self.object
        context['empty_text'] = 'Brak zarejestrowanych lotów.'
        context['type'] = 'flights'
        context['submenu_template'] = 'ato/instr_submenu.html'
        context['fbouser'] = self.object.pilot.fbouser

        flight_list = PDT.objects.filter(instructor=self.object.pk, flight_type__in=['03A','03B','03C']).exclude(status='open').order_by('-date')

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Otwórz nowy PDT', 'path': reverse("panel:pdt-open")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'SP'})
        header_list.append({'header': 'PDT'})
        header_list.append({'header': 'Szkolenie'})
        header_list.append({'header': 'Uczeń'})
        header_list.append({'header': 'TTH'})
        header_list.append({'header': 'Ldg.'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in flight_list:
            fields = []
            fields.append({'name': 'date', 'value': object.date})
            fields.append({'name': 'aircraft', 'value': object.aircraft})
            fields.append({'name': 'pdt', 'value': '{:0>6d}'.format(object.pdt_ref), 'link': reverse('panel:pdt-info', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'training', 'value': object.training.training.code, 'link': reverse('ato:training-inst-details', args=[object.training.pk]), 'just': 'center'})
            fields.append({'name': 'student', 'value': object.training.student})
            fields.append({'name': 'tth', 'value': '%.1f' % (object.tth_end() - object.tth_start), 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings_sum(), 'just': 'center'})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(login_required())
class InstructorTrainings (DetailView):
    model = Instructor
    template_name = 'ato/list_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(InstructorTrainings, self).get_object()
        if not (self.request.user.is_staff or self.request.user.has_perm('ato.ato_reader')):
            obj = self.request.user.fbouser.pilot.instructor
        return obj

    def get_context_data(self, **kwargs):
        context = super(InstructorTrainings, self).get_context_data(**kwargs)
        open = (self.kwargs['type'] == 'open')

        context['page_title'] = 'Loty szkoleniowe'
        context['header_text'] = '%s szkolenia instruktora %s' % ('Aktualne' if open else 'Zakończone', self.object)
        context['empty_text'] = 'Brak szkoleń.'
        context['type'] = 'traininigs'
        context['submenu_template'] = 'ato/instr_submenu.html'
        context['fbouser'] = self.object.pilot.fbouser

        trainings_list = Training_inst.objects.filter(instructor=self.object.pk, open=open).order_by('-start_date')

        # Lokalne menu
        local_menu = []
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Kod'})
        header_list.append({'header': 'Student'})
        header_list.append({'header': 'Data\nrozpoczęcia'})
        if not open:
            header_list.append({'header': 'Data\nzakończenia'})
        header_list.append({'header': 'Godzin\nz instr.'})
        header_list.append({'header': 'Godzin\nsolo'})
        header_list.append({'header': 'Status'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in trainings_list:
            fields = []
            fields.append({'name': 'code', 'value': object.training.code, 'link': reverse('ato:training-inst-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'student', 'value': object.student, 'link': reverse('ato:student-info', args=[object.student.pk])})
            fields.append({'name': 'date', 'value': object.start_date, 'just': 'center'})
            if not open:
                fields.append({'name': 'date', 'value': object.pass_date, 'just': 'center'})
            fields.append({'name': 'time_instr', 'value': duration_string(object.time_instr()) if object.time_instr() else '', 'just': 'center'})
            fields.append({'name': 'time_solo', 'value': duration_string(object.time_solo()) if object.time_solo() else '', 'just': 'center'})
            fields.append({'name': 'status', 'value': object.status(), 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:training-inst-update', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class InstructorCreate (CreateView):
    model = Instructor
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(InstructorCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowy instruktor'
        context['header_text'] = 'Rejestracja nowego instruktora'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Instructor, fields='__all__',
                                       widgets={'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        pilots = [(pilot.pk, pilot) for pilot in Pilot.objects.filter(instructor=None)]
        form_class.base_fields['pilot'].choices = [(None, '---------')] + pilots
        return form_class

    def get_success_url(self):
        return reverse('ato:instr-info', args=[self.object.pk])


@class_view_decorator(login_required())
class InstructorUpdate (UpdateView):
    model = Instructor
    template_name = 'ato/update_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(InstructorUpdate, self).get_object()
        if not (self.request.user.is_staff or self.request.user.has_perm('ato.ato_reader')):
            obj = self.request.user.fbouser.pilot.instructor
        return obj

    def get_context_data(self, **kwargs):
        context = super(InstructorUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Aktualizacja instruktora'
        context['header_text'] = 'Aktualizacja danych instruktora %s' % self.object
        context['type'] = 'info'
        context['submenu_template'] = 'ato/instr_submenu.html'
        context['instructor'] = self.object
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Instructor, exclude=['pilot'],
                                       widgets={'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        return form_class

    def get_success_url(self):
        return reverse('ato:instr-info', args=[self.object.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class InstructorDelete (DeleteView):
    model = Instructor
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(InstructorDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie instruktora'
        context['header_text'] = 'Usunięcie instruktora %s' % self.object
        context['description'] = 'Instruktor i związane z nim informacje zostąną usunięte!'
        context['type'] = 'info'
        context['submenu_template'] = 'ato/instr_submenu.html'
        context['instructor'] = self.object
        return context

    def get_success_url(self):
        return reverse('ato:instr-list')


@class_view_decorator(permission_required('ato.ato_reader'))
class StudentList (ListView):
    model = Student
    template_name = 'ato/list_template.html'

    def get_context_data(self, **kwargs):
        context = super(StudentList, self).get_context_data(**kwargs)
        context['page_title'] = 'Studenci'
        context['header_text'] = 'Lista studentów'
        context['empty_text'] = 'Brak zarejestrowanych studentów.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Zarejestruj nowego studenta', 'path': reverse("ato:student-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nazwisko\ni imię'})
        header_list.append({'header': 'PESEL'})
        header_list.append({'header': 'Numer\ntelefonu'})
        header_list.append({'header': 'Adres\ne-mail'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'name', 'value': object, 'link': reverse('ato:student-info', args=[object.pk])})
            fields.append({'name': 'pesel', 'value': object.pilot.fbouser.pesel, 'just': 'center'})
            fields.append({'name': 'telephone', 'value': object.pilot.fbouser.telephone})
            fields.append({'name': 'email', 'value': object.pilot.fbouser.email, 'email': object.pilot.fbouser.email})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:student-update', args=[object.pk]),
                           'delete_link': (reverse('ato:student-delete', args=[object.pk]) if not object.training_inst_set.all() else None)})
            row_list.append({'fields': fields})
        context['row_list'] = row_list
        return context


@class_view_decorator(login_required())
class StudentInfo (DetailView):
    model = Student
    template_name = 'ato/details_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(StudentInfo, self).get_object()
        if not self.request.user.has_perm('ato.ato_reader'):
            instructor = hasattr(self.request.user.fbouser.pilot, 'instructor') if self.request.user.fbouser.pilot else None
            if not (self.request.user.is_staff or instructor):
                obj = self.request.user.fbouser.pilot.student
        return obj

    def get_context_data(self, **kwargs):
        context = super(StudentInfo, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o studencie %s' % self.object
        context['type'] = 'info'
        context['submenu_template'] = 'ato/student_submenu.html'
        context['student'] = self.object

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:student-update', args=[self.object.pk])})
        # Jeśli nie ma przypisanych szkoleń to można usunąć
        if not self.object.training_inst_set.all():
            local_menu.append({'text': 'Usuń', 'path': reverse('ato:student-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Nazwisko i imię', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Data urodzenia', 'value': self.object.pilot.fbouser.birth_date})
        field_list.append({'header': 'PESEL', 'value': self.object.pilot.fbouser.pesel})
        field_list.append({'header': 'Numer telefonu', 'value': self.object.pilot.fbouser.telephone})
        field_list.append({'header': 'Adres e-mail', 'value': self.object.pilot.fbouser.email, 'email': self.object.pilot.fbouser.email})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        return context


@class_view_decorator(login_required())
class StudentFlights (DetailView):
    model = Student
    template_name = 'ato/list_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(StudentFlights, self).get_object()
        if not self.request.user.has_perm('ato.ato_reader'):
            instructor = hasattr(self.request.user.fbouser.pilot, 'instructor') if self.request.user.fbouser.pilot else None
            if not (self.request.user.is_staff or instructor):
                obj = self.request.user.fbouser.pilot.student
        return obj

    def get_context_data(self, **kwargs):
        context = super(StudentFlights, self).get_context_data(**kwargs)
        context['page_title'] = 'Loty szkoleniowe'
        context['header_text'] = 'Loty szkoleniowe ucznia %s' % self.object
        context['empty_text'] = 'Brak zarejestrowanych lotów.'
        context['type'] = 'flights'
        context['submenu_template'] = 'ato/student_submenu.html'
        context['fbouser'] = self.object.pilot.fbouser

        flight_list = (PDT.objects.filter(pic=self.object.pilot.pk, flight_type__in=['03A','03B','03C','03D','03E']).exclude(training__isnull=True) |
                      (PDT.objects.filter(sic=self.object.pilot.pk, flight_type__in=['03A','03B','03C','03D','03E']).exclude(training__isnull=True))).order_by('-date')

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Otwórz nowy PDT', 'path': reverse("panel:pdt-open")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'SP'})
        header_list.append({'header': 'PDT'})
        header_list.append({'header': 'Szkolenie'})
        header_list.append({'header': 'Instruktor'})
        header_list.append({'header': 'TTH'})
        header_list.append({'header': 'Ldg.'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in flight_list:
            fields = []
            fields.append({'name': 'date', 'value': object.date})
            fields.append({'name': 'aircraft', 'value': object.aircraft})
            fields.append({'name': 'pdt', 'value': '{:0>6d}'.format(object.pdt_ref), 'link': reverse('panel:pdt-info', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'training', 'value': object.training.training.code, 'link': reverse('ato:training-inst-details', args=[object.training.pk]), 'just': 'center'})
            fields.append({'name': 'instructor', 'value': object.instructor})
            fields.append({'name': 'tth', 'value': '%.1f' % (object.tth_end() - object.tth_start), 'just': 'center'})
            fields.append({'name': 'landings', 'value': object.landings_sum(), 'just': 'center'})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(login_required())
class StudentTrainings (DetailView):
    model = Student
    template_name = 'ato/list_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(StudentTrainings, self).get_object()
        if not self.request.user.has_perm('ato.ato_reader'):
            instructor = hasattr(self.request.user.fbouser.pilot, 'instructor') if self.request.user.fbouser.pilot else None
            if not (self.request.user.is_staff or instructor):
                obj = self.request.user.fbouser.pilot.student
        return obj

    def get_context_data(self, **kwargs):
        context = super(StudentTrainings, self).get_context_data(**kwargs)
        open = (self.kwargs['type'] == 'open')

        context['page_title'] = 'Loty szkoleniowe'
        context['header_text'] = '%s szkolenia ucznia %s' % ('Aktualne' if open else 'Zakończone', self.object)
        context['empty_text'] = 'Brak szkoleń.'
        context['type'] = 'traininigs'
        context['submenu_template'] = 'ato/student_submenu.html'
        context['fbouser'] = self.object.pilot.fbouser

        trainings_list = Training_inst.objects.filter(student=self.object.pk, open=open).order_by('-start_date')

        # Lokalne menu
        local_menu = []
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Kod'})
        header_list.append({'header': 'Instruktor'})
        header_list.append({'header': 'Data\nrozpoczęcia'})
        if not open:
            header_list.append({'header': 'Data\nzakończenia'})
        header_list.append({'header': 'Godzin\nz instr.'})
        header_list.append({'header': 'Godzin\nsolo'})
        header_list.append({'header': 'Status'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in trainings_list:
            fields = []
            fields.append({'name': 'code', 'value': object.training.code, 'link': reverse('ato:training-inst-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'instructor', 'value': object.instructor, 'link': reverse('ato:instr-info', args=[object.instructor.pk])})
            fields.append({'name': 'date', 'value': object.start_date, 'just': 'center'})
            if not open:
                fields.append({'name': 'date', 'value': object.pass_date, 'just': 'center'})
            fields.append({'name': 'time_instr', 'value': duration_string(object.time_instr()) if object.time_instr() else '', 'just': 'center'})
            fields.append({'name': 'time_solo', 'value': duration_string(object.time_solo()) if object.time_solo() else '', 'just': 'center'})
            fields.append({'name': 'status', 'value': object.status(), 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:training-inst-update', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class StudentCreate (CreateView):
    model = Student
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(StudentCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowy student'
        context['header_text'] = 'Rejestracja nowego studenta'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Student, fields='__all__',
                                       widgets={'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        pilots = [(pilot.pk, pilot) for pilot in Pilot.objects.filter(student=None)]
        form_class.base_fields['pilot'].choices = [(None, '---------')] + pilots
        return form_class

    def get_success_url(self):
        return reverse('ato:student-info', args=[self.object.pk])


@class_view_decorator(login_required())
class StudentUpdate (UpdateView):
    model = Student
    template_name = 'ato/update_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(StudentUpdate, self).get_object()
        if not self.request.user.has_perm('ato.ato_reader'):
            instructor = hasattr(self.request.user.fbouser.pilot, 'instructor') if self.request.user.fbouser.pilot else None
            if not (self.request.user.is_staff or instructor):
                obj = self.request.user.fbouser.pilot.student
        return obj

    def get_context_data(self, **kwargs):
        context = super(StudentUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Aktualizacja studenta'
        context['header_text'] = 'Aktualizacja danych studenta %s' % self.object
        context['type'] = 'info'
        context['submenu_template'] = 'ato/student_submenu.html'
        context['student'] = self.object
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Student, exclude=['pilot'],
                                       widgets={'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        return form_class

    def get_success_url(self):
        return reverse('ato:student-info', args=[self.object.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class StudentDelete (DeleteView):
    model = Student
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(StudentDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie studenta'
        context['header_text'] = 'Usunięcie studenta %s' % self.object
        context['description'] = 'Student i związane z nim informacje zostąną usunięte!'
        context['type'] = 'info'
        context['submenu_template'] = 'ato/student_submenu.html'
        context['student'] = self.object
        return context

    def get_success_url(self):
        return reverse('ato:student-list')


@class_view_decorator(permission_required('ato.ato_reader'))
class TrainingInstList (ListView):
    model = Training_inst
    template_name = 'ato/list_template.html'

    # Posortuj listę inicjalnie po datach rozpoczęcia
    def get_queryset(self):
        return Training_inst.objects.order_by('-open', '-start_date')

    def get_context_data(self, **kwargs):
        context = super(TrainingInstList, self).get_context_data(**kwargs)
        context['page_title'] = 'Szkolenia'
        context['header_text'] = 'Realizowane szkolenia'
        context['empty_text'] = 'Brak szkoleń.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowe szkolenie', 'path': reverse("ato:training-inst-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Kod'})
        header_list.append({'header': 'Student'})
        header_list.append({'header': 'Instruktor\nprowadzący'})
        header_list.append({'header': 'Otwarte'})
        header_list.append({'header': 'Ostatni\nlot'})
        header_list.append({'header': 'Ostatnie\nzadanie'})
        header_list.append({'header': 'Godzin\nz instr.'})
        header_list.append({'header': 'Godzin\nsolo'})
        header_list.append({'header': 'Status'})
        header_list.append({'header': 'Uwagi'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            if object.card_entry_set.last():
                last_flight_date = object.card_entry_set.last().date
                current_exercise = object.card_entry_set.last().exercise_inst
                current_exercise_code = "%s / %s" % (current_exercise.phase_inst.code, current_exercise.code)
                current_exercise_link = reverse('ato:exercise-inst-details', args=[current_exercise.pk])
            else:
                last_flight_date = "Brak"
                current_exercise = None
                current_exercise_code = "Brak"
                current_exercise_link = ""

            fields = []
            fields.append({'name': 'code', 'value': object.training.code, 'link': reverse('ato:training-inst-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'student', 'value': object.student, 'link': reverse('ato:student-info', args=[object.student.pk])})
            fields.append({'name': 'instructor', 'value': object.instructor, 'link': reverse('ato:instr-info', args=[object.instructor.pk])})
            fields.append({'name': 'open', 'value': 'TAK' if object.open else 'NIE', 'just': 'center'})
            fields.append({'name': 'last_flight_date', 'value': last_flight_date, 'just': 'center'})
            fields.append({'name': 'current_exercise', 'value': current_exercise_code, 'link': current_exercise_link, 'just': 'center'})
            fields.append({'name': 'time_instr', 'value': duration_string(object.time_instr()) if object.time_instr() else '', 'just': 'center'})
            fields.append({'name': 'time_solo', 'value': duration_string(object.time_solo()) if object.time_solo() else '', 'just': 'center'})
            fields.append({'name': 'status', 'value': object.status(), 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            fields.append({'name': 'change', 'report_link': reverse('ato:card-entry-list', args=[object.pk]),
                           'edit_link': reverse('ato:training-inst-update', args=[object.pk]),
                           'delete_link': reverse('ato:training-inst-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_reader'))
class TrainingInstDetails (DetailView):
    model = Training_inst
    template_name = 'ato/training_details.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingInstDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły szkolenia %s' % self.object

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:training-inst-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:training-inst-delete', args=[self.object.pk])})
        if (self.object.passed == 'NIE') and all(phase.passed == 'TAK' for phase in self.object.phase_inst_set.all()):
            local_menu.append({'text': 'Zalicz', 'path': reverse('ato:training-inst-pass', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod szkolenia', 'value': self.object.training.code, 'bold': True})
        field_list.append({'header': 'Nazwa szkolenia', 'value': self.object.training.name})
        field_list.append({'header': 'Student', 'value': self.object.student, 'bold': True})
        field_list.append({'header': 'Instruktor', 'value': self.object.instructor, 'bold': True})
        field_list.append({'header': 'Data rozpoczęcia', 'value': self.object.start_date})
        field_list.append({'header': 'Status', 'value': self.object.status()})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        context['field_list'] = field_list

        context['phase_header_text'] = 'Zadania/fazy w ramach szkolenia'
        context['phase_create_path'] = reverse('ato:phase-inst-create', args=[self.object.pk])
        context['phase_card_text'] = 'Karta szkolenia'
        context['phase_card_path'] = reverse('ato:card-entry-list', args=[self.object.pk])
        context['phase_create_text'] = 'Nowe zadanie/faza'
        context['phase_empty_text'] = 'Brak zadań/faz dla szkolenia.'

        phase_header_list = []
        phase_header_list.append({'header': 'Kod', 'width': '80px'})
        phase_header_list.append({'header': 'Nazwa'})
        phase_header_list.append({'header': 'Poprzednik'})
        phase_header_list.append({'header': 'Godzin\nz instr.'})
        phase_header_list.append({'header': 'Godzin\n solo'})
        phase_header_list.append({'header': 'Zaliczone'})
        phase_header_list.append({'header': '...', 'width': '33px'})
        context['phase_header_list'] = phase_header_list

        row_list = []
        for phase_inst in self.object.phase_inst_set.order_by('code'):
            if phase_inst.passed == 'TAK':
                color = 'lightgreen'
            else:
                color = None
            fields = []
            fields.append({'name': 'code', 'color': color, 'value': phase_inst.code, 'link': reverse('ato:phase-inst-details', args=[phase_inst.pk]), 'just': 'center'})
            fields.append({'name': 'name', 'color': color, 'value': phase_inst.name})
            fields.append({'name': 'predecessor', 'color': color, 'value': phase_inst.predecessor})
            fields.append({'name': 'time_instr', 'color': color, 'value': (duration_string(phase_inst.time_instr()) if phase_inst.time_instr() else '') +
                                                                       (' (min. %s)' % duration_string(phase_inst.min_time_instr) if phase_inst.min_time_instr else ''), 'just': 'center'})
            fields.append({'name': 'time_solo', 'color': color, 'value': (duration_string(phase_inst.time_solo()) if phase_inst.time_solo() else '') +
                                                                       (' (min. %s)' % duration_string(phase_inst.min_time_solo) if phase_inst.min_time_solo else ''), 'just': 'center'})
            fields.append({'name': 'passed', 'color': color, 'value': phase_inst.passed, 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('ato:phase-inst-update', args=[phase_inst.pk]), 'color': color,
                           'delete_link': reverse('ato:phase-inst-delete', args=[phase_inst.pk])})
            row_list.append({'fields': fields})
        context['phase_row_list'] = row_list

        return context


@permission_required('ato.ato_admin')
def TrainingInstCreate (request):
    context = {}
    context['page_title'] = 'Nowe szkolenie'
    context['header_text'] = 'Utworzenie nowego szkolenia'

    form_class = modelform_factory(Training_inst, exclude=['description', 'passed', 'pass_date', 'open'],
                                   widgets = {'start_date': AdminDateWidget(), 'remarks':Textarea(attrs={'rows':15, 'cols':100})})
    form_class.base_fields['start_date'].initial = date.today()

    form = form_class(request.POST or None)
    context['form'] = form

    if form.is_valid():
        training_inst = Training_inst(training = form.cleaned_data['training'],
                                      student = form.cleaned_data['student'],
                                      instructor = form.cleaned_data['instructor'],
                                      start_date = form.cleaned_data['start_date'],
                                      remarks = form.cleaned_data['remarks'])
        training_inst.full_clean()
        training_inst.save()

        # Skopiuj zadania według programu #
        for phase in training_inst.training.phase_set.order_by('code'):
            phase_inst = Phase_inst(training_inst = training_inst,
                                    code = phase.code,
                                    name = phase.name,
                                    description = phase.description,
                                    min_time_instr = phase.min_time_instr,
                                    min_time_solo = phase.min_time_solo)
            phase_inst.full_clean()
            phase_inst.save()

            # Skopiuj ćwiczenia według programu #
            for exercise in phase.exercise_set.order_by('code'):
                exercise_inst = Exercise_inst(phase_inst = phase_inst,
                                              code = exercise.code,
                                              name = exercise.name,
                                              description = exercise.description,
                                              restrictions = exercise.restrictions,
                                              min_time_instr = exercise.min_time_instr,
                                              min_time_solo = exercise.min_time_solo,
                                              min_num_instr = exercise.min_num_instr,
                                              min_num_solo = exercise.min_num_solo)
                exercise_inst.full_clean()
                exercise_inst.save()

            # Przypisz właściwe poprzedniki dla ćwiczeń #
            for exercise_inst in phase_inst.exercise_inst_set.all():
                exercise = phase.exercise_set.filter(code=exercise_inst.code).first()
                if exercise:
                    if exercise.predecessor:
                        new_predecessor = phase_inst.exercise_inst_set.filter(code = exercise.predecessor.code).first()
                        if new_predecessor:
                            exercise_inst.predecessor = new_predecessor
                            exercise_inst.full_clean()
                            exercise_inst.save()

        # Przypisz właściwe poprzedniki dla zadań #
        for phase_inst in training_inst.phase_inst_set.all():
            phase = training_inst.training.phase_set.filter(code = phase_inst.code).first()
            if phase:
                if phase.predecessor:
                    new_predecessor = training_inst.phase_inst_set.filter(code = phase.predecessor.code)
                    if new_predecessor:
                        phase_inst.predecessor = new_predecessor.first()
                        phase_inst.full_clean()
                        phase_inst.save()

        return HttpResponseRedirect(reverse('ato:training-inst-details', args=[training_inst.pk]))
    return render(request, 'ato/create_template.html', context)


@class_view_decorator(permission_required('ato.ato_admin'))
class TrainingInstUpdate (UpdateView):
    model = Training_inst
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingInstUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana szkolenia'
        context['header_text'] = 'Zmiana informacji o szkoleniu %s' % self.object
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Training_inst, exclude=['training', 'student'],
                                       widgets={'start_date':AdminDateWidget,
                                                'pass_date':AdminDateWidget,
                                                'remarks':Textarea(attrs={'rows':15, 'cols':100})})
        class update_form(form_class):
            def clean_passed(self):
                cleaned_data = super(update_form, self).clean()
                if cleaned_data['passed'] == 'TAK':
                    for phase_inst in self.instance.phase_inst_set.all():
                        if phase_inst.passed == 'NIE':
                            raise ValidationError(('Nie wszystkie zadania/fazy zostały zaliczone!'), code='not_passed')
                return cleaned_data['passed']

        return update_form

    def get_success_url(self):
        return reverse('ato:training-inst-details', args=[self.object.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class TrainingInstDelete (DeleteView):
    model = Training_inst
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(TrainingInstDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Zamknięcie szkolenia'
        context['header_text'] = 'Zamknięcie szkolenia'
        return context

    def get_success_url(self):
        return reverse('ato:training-inst-list')


permission_required('ato.ato_admin')
def TrainingInstPass(request, pk):

    context = {}
    training_inst = get_object_or_404(Training_inst, pk=pk)
    context['page_title'] = 'Zaliczenie szkolenia'
    context['header_text'] = 'Zaliczenie szkolenia %s' % training_inst
    context['object'] = training_inst

    form = Form(request.POST or None)
    context['form'] = form

    if form.is_valid():
        training_inst.passed = 'TAK'
        training_inst.pass_date = date.today()
        training_inst.open = False
        training_inst.full_clean()
        training_inst.save()

        return HttpResponseRedirect(reverse('ato:training-inst-details', args=[pk]))
    return render(request, 'ato/pass_template.html', context)


@class_view_decorator(permission_required('ato.ato_reader'))
class PhaseInstDetails (DetailView):
    model = Phase_inst
    template_name = 'ato/phase_details.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseInstDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły zadania/fazy %s dla %s' % (self.object, self.object.training_inst.student)

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:phase-inst-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:phase-inst-delete', args=[self.object.pk])})
        if (self.object.passed == 'NIE') and (not self.object.predecessor or self.object.predecessor.passed == 'TAK') and \
            all(exercise.passed == 'TAK' for exercise in self.object.exercise_inst_set.all()):
            local_menu.append({'text': 'Zalicz', 'path': reverse('ato:phase-inst-pass', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod zadania/fazy', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Nazwa zadania/fazy', 'value': self.object.name})
        field_list.append({'header': 'Opis zadania/fazy', 'value': self.object.description})
        field_list.append({'header': 'Poprzednik', 'value': self.object.predecessor})
        field_list.append({'header': 'Godzin z instr.', 'value': (duration_string(self.object.time_instr()) if self.object.time_instr() else '') +
                                                                 (' (min. %s)' % duration_string(self.object.min_time_instr) if self.object.min_time_instr else '')})
        field_list.append({'header': 'Godzin solo', 'value': (duration_string(self.object.time_solo()) if self.object.time_solo() else '') +
                                                             (' (min. %s)' % duration_string(self.object.min_time_solo) if self.object.min_time_solo else '')})
        field_list.append({'header': 'Zaliczone', 'value': self.object.passed})
        context['field_list'] = field_list
        context['header_width'] = '135px'

        context['exercise_header_text'] = 'Cwiczenia w ramach %s' % self.object
        context['exercise_create_path'] = reverse('ato:exercise-inst-create', args=[self.object.pk])
        context['exercise_card_text'] = 'Karta szkolenia'
        context['exercise_card_path'] = reverse('ato:card-entry-list', args=[self.object.training_inst.pk])
        context['exercise_create_text'] = 'Nowe ćwiczenie'
        context['exercise_empty_text'] = 'Brak ćwiczeń dla zadania/fazy.'

        exercise_header_list = []
        exercise_header_list.append({'header': 'Kod', 'width': '90px'})
        exercise_header_list.append({'header': 'Nazwa'})
        exercise_header_list.append({'header': 'Poprzednik'})
        exercise_header_list.append({'header': 'Restrykcje'})
        exercise_header_list.append({'header': 'Godzin\nz instr.'})
        exercise_header_list.append({'header': 'Godzin\nsolo'})
        exercise_header_list.append({'header': 'Lotów\nz instr.'})
        exercise_header_list.append({'header': 'Lotów\nsolo'})
        exercise_header_list.append({'header': 'Zaliczone'})
        exercise_header_list.append({'header': '...', 'width': '33px'})
        context['exercise_header_list'] = exercise_header_list

        row_list = []
        for exercise_inst in self.object.exercise_inst_set.order_by('code'):
            if exercise_inst.passed == 'TAK':
                color = 'lightgreen'
            else:
                color = None
            fields = []
            fields.append({'name': 'code', 'color': color, 'value': exercise_inst.code, 'link': reverse('ato:exercise-inst-details', args=[exercise_inst.pk]), 'just': 'center'})
            fields.append({'name': 'name', 'color': color, 'value': exercise_inst.name})
            fields.append({'name': 'predecessor', 'color': color, 'value': exercise_inst.predecessor})
            fields.append({'name': 'restrictions', 'color': color, 'value': exercise_inst.restrictions, 'just': 'center'})
            fields.append({'name': 'time_instr', 'color': color, 'value': (duration_string(exercise_inst.time_instr) if exercise_inst.time_instr else '') +
                                                                          (' (min. %s)' % duration_string(exercise_inst.min_time_instr) if exercise_inst.min_time_instr else ''), 'just': 'center'})
            fields.append({'name': 'time_solo', 'color': color, 'value': (duration_string(exercise_inst.time_solo) if exercise_inst.time_solo else '') +
                                                                         (' (min. %s)' % duration_string(exercise_inst.min_time_solo) if exercise_inst.min_time_solo else ''), 'just': 'center'})
            fields.append({'name': 'num_instr', 'color': color, 'value': '%d' % exercise_inst.num_instr + (' (min. %d)' % exercise_inst.min_num_instr if exercise_inst.min_num_instr else ''), 'just': 'center'})
            fields.append({'name': 'num_solo', 'color': color, 'value': '%d' % exercise_inst.num_solo + (' (min. %d)' % exercise_inst.min_num_solo if exercise_inst.min_num_solo else ''), 'just': 'center'})
            fields.append({'name': 'passed', 'color': color, 'value': exercise_inst.passed, 'just': 'center'})
            fields.append({'name': 'change', 'edit_link': reverse('ato:exercise-inst-update', args=[exercise_inst.pk]), 'color': color,
                           'delete_link': reverse('ato:exercise-inst-delete', args=[exercise_inst.pk])})
            row_list.append({'fields': fields})
        context['exercise_row_list'] = row_list
        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseInstCreate(CreateView):
    model = Phase_inst
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseInstCreate, self).get_context_data(**kwargs)
        training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])
        context['page_title'] = 'Nowe zadanie/faza'
        context['header_text'] = 'Utworzenie nowego zadania/fazy dla %s' % training_inst
        return context

    def get_form_class(self, **kwargs):
        phases = Phase_inst.objects.filter(training_inst = self.kwargs['training_inst_id'])
        form_class = modelform_factory(Phase_inst, exclude=['training_inst', 'passed'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100}),
                                                'remarks': Textarea(attrs={'rows': 5, 'cols': 100})})
        form_class.base_fields['predecessor'].choices = [(str(phase.pk), phase) for phase in phases]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def form_valid(self, form):
        form.instance.training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])
        return super(PhaseInstCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('ato:training-inst-details', args=[self.kwargs['training_inst_id']])


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseInstUpdate (UpdateView):
    model = Phase_inst
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseInstUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana zadania/fazy'
        context['header_text'] = 'Zmiana zadania/fazy %s' % self.object
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Phase_inst, exclude=['training_inst', 'phase'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100}),
                                                'remarks':Textarea(attrs={'rows':5, 'cols':100})})
        class update_form(form_class):
            def clean_passed(self):
                cleaned_data = super(update_form, self).clean()
                if cleaned_data['passed'] == 'TAK':
                    for exercise_inst in self.instance.exercise_inst_set.all():
                        if exercise_inst.passed == 'NIE':
                            raise ValidationError(('Nie wszystkie ćwiczenia zostały zaliczone!'), code='not_passed')
                return cleaned_data['passed']

        phases = Phase_inst.objects.filter(training_inst = self.object.training_inst).exclude(pk = self.object.pk)
        update_form.base_fields['predecessor'].choices = [(str(phase.pk), phase) for phase in phases]
        update_form.base_fields['predecessor'].choices.insert (0, ('', '---------'))

        return update_form

    def get_success_url(self):
        return reverse('ato:training-inst-details', args=[self.object.training_inst.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class PhaseInstDelete (DeleteView):
    model = Phase_inst
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PhaseInstDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie zadania/fazy'
        context['header_text'] = 'Usunięcie zadania/fazy dla %s' % self.object.training_inst.training
        return context

    def get_success_url(self):
        return reverse('ato:training-inst-details', args=[self.object.training_inst.pk])


permission_required('ato.ato_admin')
def PhaseInstPass(request, pk):

    context = {}
    phase_inst = get_object_or_404(Phase_inst, pk=pk)
    context['page_title'] = 'Zaliczenie zadania/fazy'
    context['header_text'] = 'Zaliczenie zadania/fazy %s' % phase_inst
    context['object'] = phase_inst

    form = Form(request.POST or None)
    context['form'] = form

    if form.is_valid():
        phase_inst.passed = 'TAK'
        phase_inst.full_clean()
        phase_inst.save()

        return HttpResponseRedirect(reverse('ato:training-inst-details', args=[phase_inst.training_inst_id]))
    return render(request, 'ato/pass_template.html', context)


@class_view_decorator(permission_required('ato.ato_reader'))
class ExerciseInstDetails (DetailView):
    model = Exercise_inst
    template_name = 'ato/exercise_details.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseInstDetails, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = u'Szczegóły ćwiczenia %s dla %s' % (self.object, self.object.phase_inst.training_inst.student)

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:exercise-inst-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:exercise-inst-delete', args=[self.object.pk])})
        if (self.object.passed == 'NIE') and (not self.object.predecessor or self.object.predecessor.passed == 'TAK') and \
           (not self.object.min_time_instr or (self.object.time_instr or datetime.timedelta(seconds=0) >= self.object.min_time_instr)) and \
           (not self.object.min_time_solo or (self.object.time_solo  or datetime.timedelta(seconds=0) >= self.object.min_time_solo)) and \
           (not self.object.min_num_instr or (self.object.num_instr or 0 >= self.object.min_num_instr)) and \
           (not self.object.min_num_solo or (self.object.num_solo or 0 >= self.object.min_num_solo)):
            local_menu.append({'text': 'Zalicz', 'path': reverse('ato:exercise-inst-pass', args=[self.object.pk])})

        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Kod ćwiczenia', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Nazwa ćwiczenia', 'value': self.object.name})
        field_list.append({'header': 'Opis ćwiczenia', 'value': self.object.description})
        field_list.append({'header': 'Poprzednik', 'value': self.object.predecessor})
        field_list.append({'header': 'Restrykcje', 'value': self.object.restrictions})
        field_list.append({'header': 'Godzin z instr.', 'value': (duration_string(self.object.time_instr) if self.object.time_instr else '') +
                                                                 (' (min. %s)' % duration_string(self.object.min_time_instr) if self.object.min_time_instr else '')})
        field_list.append({'header': 'Godzin solo', 'value': (duration_string(self.object.time_solo) if self.object.time_solo else '') +
                                                             (' (min. %s)' % duration_string(self.object.min_time_solo) if self.object.min_time_solo else '')})
        field_list.append({'header': 'Lotów z instr.', 'value': '%d' % self.object.num_instr + (' (min. %d)' % self.object.min_num_instr if self.object.min_num_instr else '')})
        field_list.append({'header': 'Lotów solo', 'value': '%d' % self.object.num_solo + (' (min. %d)' % self.object.min_num_solo if self.object.min_num_solo else '')})
        field_list.append({'header': 'Zaliczone', 'value': self.object.passed})
        context['field_list'] = field_list
        context['header_width'] = '135px'

        context['operations_header_text'] = 'Operacje w ramach %s' % self.object
        context['operations_create_path'] = reverse('ato:exercise-oper-create', args=[self.object.pk])
        context['operations_create_text'] = 'Nowa operacja'
        context['operations_empty_text'] = 'Brak operacji dla ćwiczenia.'
        context['exercise_card_text'] = 'Karta szkolenia'
        context['exercise_card_path'] = reverse('ato:card-entry-list', args=[self.object.phase_inst.training_inst.pk])

        # operations_header_list = []
        # operations_header_list.append({'header': 'Data'})
        # operations_header_list.append({'header': 'SP'})
        # operations_header_list.append({'header': 'Lotnisko\nstartu'})
        # operations_header_list.append({'header': 'Lotnisko\nlądowania'})
        # operations_header_list.append({'header': 'Godzina\nstartu.'})
        # operations_header_list.append({'header': 'Godzina\nlądowania'})
        # operations_header_list.append({'header': 'Solo'})
        # operations_header_list.append({'header': 'Czas\nćwiczenia'})
        # operations_header_list.append({'header': 'Powt.\nćwiczenia'})
        # operations_header_list.append({'header': 'Uwagi'})
        # operations_header_list.append({'header': '...', 'width': '33px'})
        # context['operations_header_list'] = operations_header_list
        #
        # row_list = []
        # ex_oper_set = self.object.exercise_oper_set.all()
        # for ex_oper in ex_oper_set:
        #     fields = []
        #     fields.append({'name': 'date', 'value': ex_oper.operation.pdt.date, 'just': 'center'})
        #     fields.append({'name': 'sp', 'value': ex_oper.operation.pdt.aircraft, 'just': 'center'})
        #     fields.append({'name': 'loc_start', 'value': ex_oper.operation.loc_start, 'just': 'center'})
        #     fields.append({'name': 'loc_end', 'value': ex_oper.operation.loc_end, 'just': 'center'})
        #     fields.append({'name': 'time_start', 'value': ex_oper.operation.time_start.strftime('%H:%M'), 'just': 'center'})
        #     fields.append({'name': 'time_end', 'value': ex_oper.operation.time_end.strftime('%H:%M'), 'just': 'center'})
        #     fields.append({'name': 'solo', 'value': 'TAK' if ex_oper.solo else 'NIE', 'just': 'center'})
        #     fields.append({'name': 'allocated_time', 'value': (duration_string(ex_oper.time_allocated) if ex_oper.time_allocated else ''), 'just': 'center'})
        #     fields.append({'name': 'allocated_ldg', 'value': ex_oper.num_allocated, 'just': 'center'})
        #     fields.append({'name': 'remarks', 'value': ex_oper.remarks})
        #     fields.append({'name': 'change', 'edit_link': reverse('ato:exercise-oper-update', args=[ex_oper.pk]),
        #                            'delete_link': reverse('ato:exercise-oper-delete', args=[ex_oper.pk])})
        #     row_list.append({'fields': fields})

        operations_header_list = []
        operations_header_list.append({'header': 'Data'})
        operations_header_list.append({'header': 'Instruktor'})
        operations_header_list.append({'header': 'Zadanie'})
        operations_header_list.append({'header': 'Ćwiczenie'})
        operations_header_list.append({'header': 'Czas\ndwuster'})
        operations_header_list.append({'header': 'Powt.\ndwuster'})
        operations_header_list.append({'header': 'Czas\nsolo'})
        operations_header_list.append({'header': 'Powt.\nsolo'})
        operations_header_list.append({'header': 'Zaliczenie'})
        operations_header_list.append({'header': 'Uwagi'})
        operations_header_list.append({'header': '...', 'width': '33px'})
        context['operations_header_list'] = operations_header_list

        row_list = []
        ex_oper_set = self.object.card_entry_set.all()
        for ex_oper in ex_oper_set:
            fields = []
            fields.append({'name': 'date', 'value': ex_oper.date, 'link': reverse('ato:card-entry-details', args=[ex_oper.pk]), 'just': 'center'})
            fields.append({'name': 'instructor', 'value': ex_oper.instructor, 'link': reverse('ato:instr-info', args=[ex_oper.instructor.pk])})
            fields.append({'name': 'phase', 'value': ex_oper.exercise_inst.phase_inst.code,
                           'link': reverse('ato:phase-inst-details', args=[ex_oper.exercise_inst.phase_inst.pk]), 'just': 'center'})
            fields.append({'name': 'exercise', 'value': ex_oper.exercise_inst.code,
                           'link': reverse('ato:exercise-inst-details', args=[ex_oper.exercise_inst.pk]), 'just': 'center'})
            fields.append({'name': 'time_instr', 'value': duration_string(ex_oper.dual_time) if ex_oper.dual_time else '', 'just': 'center'})
            fields.append({'name': 'num_instr', 'value': ex_oper.dual_num if ex_oper.dual_num else '', 'just': 'center'})
            fields.append({'name': 'time_solo', 'value': duration_string(ex_oper.solo_time) if ex_oper.solo_time else '', 'just': 'center'})
            fields.append({'name': 'num_solo', 'value': ex_oper.solo_num if ex_oper.solo_num else '', 'just': 'center'})
            fields.append({'name': 'pass', 'value': 'ZAL' if ex_oper.passed == 1 else 'K', 'just': 'center'})
            fields.append({'name': 'remarks', 'value': ex_oper.remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:card-entry-update', args=[ex_oper.pk]),
                           'delete_link': reverse('ato:card-entry-delete', args=[ex_oper.pk])})
            row_list.append({'fields': fields})

        context['operations_row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseInstCreate(CreateView):
    model = Exercise_inst
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseInstCreate, self).get_context_data(**kwargs)
        phase_inst = get_object_or_404(Phase_inst, pk=self.kwargs['phase_inst_id'])
        context['page_title'] = 'Nowe ćwiczenie'
        context['header_text'] = 'Utworzenie nowego ćwiczenia dla %s' % phase_inst
        return context

    def get_form_class(self, **kwargs):
        exercises = Exercise_inst.objects.filter(phase_inst = self.kwargs['phase_inst_id'])
        form_class = modelform_factory(Exercise_inst, exclude=['phase_inst', 'time_instr', 'time_solo', 'num_instr',
                                                               'num_solo', 'passed'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100}),
                                                'remarks': Textarea(attrs={'rows': 5, 'cols': 100})})
        form_class.base_fields['predecessor'].choices = [(str(exercise.pk), exercise) for exercise in exercises]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def form_valid(self, form):
        form.instance.phase_inst = get_object_or_404(Phase_inst, pk=self.kwargs['phase_inst_id'])
        return super(ExerciseInstCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('ato:phase-inst-details', args=[self.kwargs['phase_inst_id']])


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseInstUpdate (UpdateView):
    model = Exercise_inst
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseInstUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana ćwiczenia'
        context['header_text'] = 'Zmiana ćwiczenia %s' % self.object
        return context

    def get_form_class(self, **kwargs):
        exercises = Exercise_inst.objects.filter(phase_inst = self.object.phase_inst).exclude(pk = self.object.pk)
        form_class = modelform_factory(Exercise_inst, exclude=['phase_inst', 'exercise'],
                                       widgets={'name':TextInput(attrs={'size':103}),
                                                'description':Textarea(attrs={'rows':15, 'cols':100}),
                                                'remarks':Textarea(attrs={'rows':5, 'cols':100})})
        form_class.base_fields['predecessor'].choices = [(str(exercise.pk), exercise) for exercise in exercises]
        form_class.base_fields['predecessor'].choices.insert (0, ('', '---------'))
        return form_class

    def get_success_url(self):
        return reverse('ato:phase-inst-details', args=[self.object.phase_inst.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseInstDelete (DeleteView):
    model = Exercise_inst
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseInstDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie ćwiczenia'
        context['header_text'] = 'Usunięcie ćwiczenia %s' % self.object
        return context

    def get_success_url(self):
        return reverse('ato:phase-inst-details', args=[self.object.phase_inst.pk])


permission_required('ato.ato_admin')
def ExerciseOperCreate(request, exercise_inst_id):

    context = {}
    exercise_inst = get_object_or_404(Exercise_inst, pk=exercise_inst_id)
    context['page_title'] = 'Nowa operacja'
    context['header_text'] = 'Utworzenie nowej operacji dla %s' % exercise_inst

    training = exercise_inst.phase_inst.training_inst
    operations = Operation.objects.filter(pdt__training=training, pdt__status='closed')

    # Pozwól wybrać spośród zamkniętych operacji dowiązanych do szkolenia z niezerowymi licznikami
    choices = [operation for operation in operations if operation.not_allocated_time().seconds > 0]
    form = ExercOperCreateForm(request.POST or None, choices=choices)
    context['form'] = form

    if form.is_valid():
        exercise_oper = Exercise_oper(exercise_inst=exercise_inst,
                                      operation=form.cleaned_data['operation'],
                                      solo=form.cleaned_data['solo'],
                                      time_allocated=form.cleaned_data['time_allocated'],
                                      num_allocated=form.cleaned_data['num_allocated'],
                                      remarks=form.cleaned_data['remarks'])
        exercise_oper.full_clean()
        exercise_oper.save()

        return HttpResponseRedirect(reverse('ato:exercise-inst-details', args=[exercise_inst_id]))
    return render(request, 'ato/ex_oper_create.html', context)


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseOperUpdate (UpdateView):
    model = Exercise_oper
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseOperUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana operacji'
        context['header_text'] = 'Zmiana operacji dla ćwiczenia %s' % self.object.exercise_inst
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Exercise_oper, exclude=['exercise_inst'],
                                       widgets={'remarks':Textarea(attrs={'rows':5, 'cols':100})})
        operation = self.object.operation
        form_class.base_fields['operation'].choices = [(str(operation.pk), '%s - (%s %s): %s-%s' % (operation.pdt.aircraft, operation.pdt.date,
                                                                                                    operation.time_start.strftime('%H:%M'),
                                                                                                    operation.loc_start, operation.loc_end))]
        form_class.base_fields['operation'].widget.attrs['disabled'] = True
        form_class.base_fields['operation'].required = False
        return form_class

    def get_success_url(self):
        return reverse('ato:exercise-inst-details', args=[self.object.exercise_inst.pk])


@class_view_decorator(permission_required('ato.ato_admin'))
class ExerciseOperDelete (DeleteView):
    model = Exercise_oper
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(ExerciseOperDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie operacji z ćwiczenia'
        context['header_text'] = 'Usunięcie operacji %s z ćwiczenia %s' % (self.object.operation, self.object.exercise_inst)
        return context

    def get_success_url(self):
        return reverse('ato:exercise-inst-details', args=[self.object.exercise_inst.pk])


permission_required('ato.ato_admin')
def ExerciseInstPass(request, pk):

    context = {}
    exercise_inst = get_object_or_404(Exercise_inst, pk=pk)
    context['page_title'] = u'Zaliczenie ćwiczenia'
    context['header_text'] = u'Zaliczenie ćwiczenia %s' % exercise_inst
    context['object'] = exercise_inst

    form = Form(request.POST or None)
    context['form'] = form

    if form.is_valid():
        exercise_inst.passed = 'TAK'
        exercise_inst.full_clean()
        exercise_inst.save()

        return HttpResponseRedirect(reverse('ato:phase-inst-details', args=[exercise_inst.phase_inst_id]))
    return render(request, 'ato/pass_template.html', context)


@class_view_decorator(permission_required('ato.ato_reader'))
class CardEntryList (ListView):
    model = Card_entry
    template_name = 'ato/list_template.html'

    # Posortuj listę inicjalnie po datach rozpoczęcia
    def get_queryset(self):
        training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])
        return Card_entry.objects.filter(training_inst=training_inst).order_by('-date', '-pk')

    def get_context_data(self, **kwargs):
        training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])

        context = super(CardEntryList, self).get_context_data(**kwargs)
        context['page_title'] = 'Karta szkolenia'
        context['header_text'] = 'Pozycje karty szkolenia %s' % training_inst.__str__()
        context['empty_text'] = 'Karta jest pusta.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nową pozycję',
                           'path': reverse("ato:card-entry-create", args=[self.kwargs['training_inst_id']])})
        local_menu.append({'text': 'Wydruk karty',
                           'path': reverse("ato:card-report", args=[self.kwargs['training_inst_id']])})
        local_menu.append({'text': 'Powrót do szkolenia',
                           'path': reverse("ato:training-inst-details", args=[self.kwargs['training_inst_id']])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Data'})
        header_list.append({'header': 'PDT'})
        header_list.append({'header': 'Instruktor'})
        header_list.append({'header': 'Zadanie'})
        header_list.append({'header': 'Ćwiczenie'})
        header_list.append({'header': 'Czas\ndwuster'})
        header_list.append({'header': 'Powt.\ndwuster'})
        header_list.append({'header': 'Czas\nsolo'})
        header_list.append({'header': 'Powt.\nsolo'})
        header_list.append({'header': 'Zaliczenie'})
        header_list.append({'header': 'Uwagi'})
        if self.request.user.fbouser and hasattr(self.request.user.fbouser, 'pilot') and \
           hasattr(self.request.user.fbouser.pilot, 'instructor'):
            header_list.append({'header': 'Uwagi dla\ninstruktora'})
        header_list.append({'header': '...'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'date', 'value': object.date, 'link': reverse('ato:card-entry-details', args=[object.pk]), 'just': 'center'})
            fields.append({'name': 'pdt', 'value': object.pdt_num})
            fields.append({'name': 'instructor', 'value': object.instructor, 'link': reverse('ato:instr-info', args=[object.instructor.pk])})
            fields.append({'name': 'phase', 'value': object.exercise_inst.phase_inst.code, 'link': reverse('ato:phase-inst-details', args=[object.exercise_inst.phase_inst.pk]), 'just': 'center'})
            fields.append({'name': 'exercise', 'value': object.exercise_inst.code, 'link': reverse('ato:exercise-inst-details', args=[object.exercise_inst.pk]), 'just': 'center'})
            fields.append({'name': 'time_instr', 'value': duration_string(object.dual_time) if object.dual_time else '', 'just': 'center'})
            fields.append({'name': 'num_instr', 'value': object.dual_num if object.dual_num else '', 'just': 'center'})
            fields.append({'name': 'time_solo', 'value': duration_string(object.solo_time) if object.solo_time else '', 'just': 'center'})
            fields.append({'name': 'num_solo', 'value': object.solo_num if object.solo_num else '', 'just': 'center'})
            fields.append({'name': 'pass', 'value': 'ZAL' if object.passed == 1 else 'K', 'just': 'center'})
            fields.append({'name': 'remarks', 'value': object.remarks})
            if self.request.user.fbouser and hasattr(self.request.user.fbouser, 'pilot') and hasattr(self.request.user.fbouser.pilot, 'instructor'):
                fields.append({'name': 'remarks', 'value': object.internal_remarks})
            fields.append({'name': 'change', 'edit_link': reverse('ato:card-entry-update', args=[object.pk]),
                           'delete_link': reverse('ato:card-entry-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_reader'))
class CardReport (ListView):
    model = Card_entry
    template_name = 'ato/card.html'

    # Posortuj listę inicjalnie po datach rozpoczęcia
    def get_queryset(self):
        training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])
        return Card_entry.objects.filter(training_inst=training_inst).order_by('date', 'pk')

    # Kontekst dla wydruku karty szkolenia #
    def get_context_data(self, **kwargs):
        training_inst = get_object_or_404(Training_inst, pk=self.kwargs['training_inst_id'])

        context = super(CardReport, self).get_context_data(**kwargs)

        context['page_title'] = 'Karta szkolenia'
        context['header_text'] = 'Pozycje karty szkolenia %s' % training_inst.__str__()
        context['empty_text'] = 'Karta jest pusta.'
        context['training_inst'] = training_inst

        # Zawartość kary
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'just': 'center', 'value': object.date})
            fields.append({'just': 'left',   'value': object.instructor})
            fields.append({'just': 'center', 'value': object.exercise_inst.phase_inst.code})
            fields.append({'just': 'center', 'value': object.exercise_inst.code})
            fields.append({'just': 'center', 'value': object.dual_num if object.dual_num else ''})
            fields.append({'just': 'center', 'value': duration_string(object.dual_time) if object.dual_time else ''})
            fields.append({'just': 'center', 'value': object.solo_num if object.solo_num else ''})
            fields.append({'just': 'center', 'value': duration_string(object.solo_time) if object.solo_time else ''})
            fields.append({'just': 'center', 'value': 'ZAL' if object.passed == 1 else 'K'})
            fields.append({'just': 'left',   'value': object.remarks})

            dual_num_sum = 0
            solo_num_sum = 0
            dual_time_sum = datetime.timedelta(seconds=0)
            solo_time_sum = datetime.timedelta(seconds=0)

            for entry in self.object_list:
                if entry.exercise_inst.pk == object.exercise_inst.pk:
                    dual_num_sum += entry.dual_num
                    solo_num_sum += entry.solo_num
                    dual_time_sum += entry.dual_time
                    solo_time_sum += entry.solo_time
                if entry.pk == object.pk:
                    break

            sums = []
            sums.append({'value': dual_num_sum})
            sums.append({'value': duration_string(dual_time_sum)})
            sums.append({'value': solo_num_sum})
            sums.append({'value': duration_string(solo_time_sum)})

            row_list.append({'fields': fields, 'sums': sums})
        context['row_list'] = row_list

        return context


@class_view_decorator(permission_required('ato.ato_reader'))
class CardEntryDetails (DetailView):
    model = Card_entry
    template_name = 'ato/training_details.html'

    def get_context_data(self, **kwargs):
        context = super(CardEntryDetails, self).get_context_data(**kwargs)
        context['page_title'] = 'Pozycja karty szkolenia'
        context['header_text'] = 'Pozycja karty szkolenia %s' % self.object.training_inst.__str__()

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('ato:card-entry-update', args=[self.object.pk])})
        local_menu.append({'text': 'Usuń', 'path': reverse('ato:card-entry-delete', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Data lotu', 'value': self.object.date, 'bold': True})
        field_list.append({'header': 'PDT lotu', 'value': self.object.pdt_num, 'bold': True})
        field_list.append({'header': 'Instruktor', 'value': self.object.instructor, 'bold': True})
        field_list.append({'header': 'Zadanie', 'value': self.object.exercise_inst.phase_inst.code})
        field_list.append({'header': 'Ćwiczenie', 'value': self.object.exercise_inst.code})
        field_list.append({'header': 'Czas dwuster', 'value': duration_string(self.object.dual_time)})
        field_list.append({'header': 'Liczba powt. dwuster', 'value': self.object.dual_num})
        field_list.append({'header': 'Czas solo', 'value': duration_string(self.object.solo_time)})
        field_list.append({'header': 'Liczba powt. solo', 'value': self.object.solo_num})
        field_list.append({'header': 'Zaliczenie', 'value': 'ZAL' if self.object.passed == 1 else 'K'})
        field_list.append({'header': 'Uwagi', 'value': self.object.remarks})
        if self.request.user.fbouser and hasattr(self.request.user.fbouser, 'pilot') and \
                hasattr(self.request.user.fbouser.pilot, 'instructor'):
            field_list.append({'header': 'Uwagi dla instr.', 'value': self.object.internal_remarks})
        context['field_list'] = field_list

        return context


@class_view_decorator(user_passes_test(lambda u: u.fbouser and hasattr(u.fbouser, 'pilot') and hasattr(u.fbouser.pilot, 'instructor')))
class CardEntryCreate (CreateView):
    model = Card_entry
    template_name = 'ato/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(CardEntryCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowa pozycja'
        context['header_text'] = 'Utworzenie nowej pozycji dla %s' % Training_inst.objects.get(pk=self.kwargs['training_inst_id'])
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Card_entry, exclude=['training_inst'],
                                       widgets={'remarks': Textarea(attrs={'rows': 5, 'cols': 100}),
                                                'internal_remarks': Textarea(attrs={'rows': 5, 'cols': 100})})

        form_class.base_fields['date'].initial = date.today()
        instructors = list((instructor.pk, instructor.__str__())
                      for instructor in Instructor.objects.order_by('pilot__fbouser__second_name'))

        form_class.base_fields['instructor'].choices = instructors

        form_class.base_fields['instructor'].initial = self.request.user.fbouser.pilot.instructor.pk

        exercises = list((exercise_inst.pk, exercise_inst.__str__())
                         for exercise_inst in Exercise_inst.objects.filter(phase_inst__training_inst=self.kwargs['training_inst_id']).order_by('pk'))
        form_class.base_fields['exercise_inst'].choices = exercises
        last_entry = Card_entry.objects.filter(training_inst=self.kwargs['training_inst_id']).last()
        if last_entry:
            form_class.base_fields['exercise_inst'].initial = last_entry.exercise_inst.pk

        return form_class

    def form_valid(self, form):
        form.instance.training_inst = Training_inst.objects.get(pk=self.kwargs['training_inst_id'])
        return super(CardEntryCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('ato:card-entry-list', args=[self.kwargs['training_inst_id']])


@class_view_decorator(user_passes_test(lambda u: u.fbouser and hasattr(u.fbouser, 'pilot') and hasattr(u.fbouser.pilot, 'instructor')))
class CardEntryUpdate (UpdateView):
    model = Card_entry
    template_name = 'ato/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(CardEntryUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana pozycji'
        context['header_text'] = 'Zmiana pozycji karty szkolenia'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Card_entry, exclude=['training_inst'],
                                       widgets={'remarks': Textarea(attrs={'rows': 5, 'cols': 100}),
                                                'internal_remarks': Textarea(attrs={'rows': 5, 'cols': 100})})
        exercises = list((exercise_inst.pk, exercise_inst.__str__())
                         for exercise_inst in Exercise_inst.objects.filter(phase_inst__training_inst=self.object.exercise_inst.phase_inst.training_inst_id))
        form_class.base_fields['exercise_inst'].choices = exercises

        return form_class

    def get_success_url(self):
        return reverse('ato:card-entry-list', args=[self.object.exercise_inst.phase_inst.training_inst.pk])


@class_view_decorator(user_passes_test(lambda u: u.fbouser and hasattr(u.fbouser, 'pilot') and hasattr(u.fbouser.pilot, 'instructor')))
class CardEntryDelete (DeleteView):
    model = Card_entry
    template_name = 'ato/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(CardEntryDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie pozycji'
        context['header_text'] = 'Usunięcie pozycji karty szkolenia'
        return context

    def get_success_url(self):
        return reverse('ato:card-entry-list', args=[self.object.training_inst.pk])
