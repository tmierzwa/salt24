# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.forms.models import modelform_factory, ModelForm
from django.forms.forms import NON_FIELD_ERRORS
from django.forms import TextInput, Textarea
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

def class_view_decorator(function_decorator):

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator

from panel.models import FBOUser, Pilot


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class FBOUserList (ListView):
    model = FBOUser
    template_name = 'fbo/list_template.html'

    # Posortuj listę inicjalnie po statusie aktywności
    def get_queryset(self):
        return FBOUser.objects.order_by('second_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super(FBOUserList, self).get_context_data(**kwargs)
        context['page_title'] = 'Użytkownicy'
        context['header_text'] = 'Lista użytkowników systemu'
        context['empty_text'] = 'Brak zarejestrowanych użytkowników.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowego użytkownika', 'path': reverse("fbo:user-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Login'})
        header_list.append({'header': 'Aktywny'})
        header_list.append({'header': 'Nazwisko\ni imię'})
        header_list.append({'header': 'Adres\nemail'})
        header_list.append({'header': 'Numer\ntelefonu'})
        header_list.append({'header': 'INFOS'})
        header_list.append({'header': 'Pilot'})
        header_list.append({'header': 'Instruktor'})
        header_list.append({'header': 'Uczeń'})
        header_list.append({'header': 'Kontrahent'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'login', 'value': object.user.username, 'link': reverse('fbo:user-info', args=[object.pk])})
            fields.append({'name': 'active', 'value': ('TAK' if object.active else 'NIE'), 'just': 'center'})
            fields.append({'name': 'last_name', 'value': '%s' % object})
            fields.append({'name': 'email', 'value': object.email, 'email': object.email})
            fields.append({'name': 'telephone', 'value': object.telephone})
            fields.append({'name': 'infos', 'value': 'TAK' if object.infos else 'NIE', 'just': 'center'})
            if hasattr(object, 'pilot'):
                fields.append({'name': 'pilot', 'profile_link': reverse('panel:pilot-info', args=[object.pilot.pk]), 'just': 'center'})
            else:
                fields.append({'name': 'pilot', 'value': ''})
            if hasattr(object, 'pilot') and hasattr(object.pilot, 'instructor'):
                fields.append({'name': 'instructor', 'profile_link': reverse('ato:instr-info', args=[object.pilot.instructor.pk]), 'just': 'center'})
            else:
                fields.append({'name': 'instructor', 'value': ''})
            if hasattr(object, 'pilot') and hasattr(object.pilot, 'student'):
                fields.append({'name': 'student', 'profile_link': reverse('ato:student-info', args=[object.pilot.student.pk]), 'just': 'center'})
            else:
                fields.append({'name': 'student', 'value': ''})
            if object.contractor:
                fields.append({'name': 'contractor', 'profile_link': reverse('fin:contr-info', args=[object.contractor.pk]), 'just': 'center'})
            else:
                fields.append({'name': 'contractor', 'value': ''})
            fields.append({'name': 'change', 'edit_link': reverse('fbo:user-update', args=[object.pk]),
                           'tools_link': reverse('admin-pwd-change', args=[object.pk]),
                           'delete_link': (reverse('fbo:user-delete', args=[object.pk]) if object.active else '')})
            row_list.append({'fields': fields})
        context['row_list'] = row_list

        return context


@class_view_decorator(login_required())
class FBOUserInfo (DetailView):
    model = FBOUser
    template_name = 'panel/details_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(FBOUserInfo, self).get_object()
        if not self.request.user.is_staff:
            obj = self.request.user.fbouser
        return obj

    def get_context_data(self, **kwargs):
        context = super(FBOUserInfo, self).get_context_data(**kwargs)
        context['page_title'] = self.object
        context['header_text'] = 'Informacje o uzytkowniku %s' % self.object.user.username
        context['type'] = 'info'
        context['submenu_template'] = 'panel/user_submenu.html'
        context['fbouser'] = self.object
        context['logged'] = self.request.user.fbouser

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Aktualizuj', 'path': reverse('fbo:user-update', args=[self.object.pk])})
        if self.request.user.is_staff:
            if self.object.active:
                local_menu.append({'text': 'Deaktywuj', 'path': reverse('fbo:user-delete', args=[self.object.pk])})
            else:
                local_menu.append({'text': 'Aktywuj', 'path': reverse('fbo:user-activate', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Nazwisko i imię', 'value': self.object, 'bold': True})
        field_list.append({'header': 'Status', 'value': ('Aktywny' if self.object.active else 'Nieaktywny'), 'bold': True})
        field_list.append({'header': 'Adres email', 'value': self.object.email})
        field_list.append({'header': 'Numer telefonu', 'value': self.object.telephone})
        field_list.append({'header': 'Adres zamieszkania', 'value': self.object.address1})
        if self.object.address2:
            field_list.append({'header': '', 'value': self.object.address2})
        field_list.append({'header': 'Data urodzenia', 'value': self.object.birth_date})
        field_list.append({'header': 'PESEL', 'value': self.object.pesel})
        field_list.append({'header': 'Numer dowodu', 'value': self.object.id_number})
        field_list.append({'header': 'INFOS', 'value': 'TAK' if self.object.infos else 'NIE'})
        field_list.append({'header': 'Mechanik', 'value': 'TAK' if self.object.mechanic else 'NIE'})
        field_list.append({'header': 'NCR', 'value': 'TAK' if self.object.ncr_user else 'NIE'})

        context['field_list'] = field_list

        return context


@class_view_decorator(login_required())
class FBOUserModules (DetailView):
    model = FBOUser
    template_name = 'panel/details_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(FBOUserModules, self).get_object()
        if not self.request.user.is_staff:
            obj = self.request.user.fbouser
        return obj

    def get_context_data(self, **kwargs):
        context = super(FBOUserModules, self).get_context_data(**kwargs)
        context['page_title'] = 'Uprawnienia'
        context['header_text'] = 'Uprawnienia użytkownika %s' % self.object.user.username
        context['type'] = 'modules'
        context['submenu_template'] = 'panel/user_submenu.html'
        context['fbouser'] = self.object
        context['logged'] = self.request.user.fbouser

        # Lokalne menu
        local_menu = []
        if self.request.user.is_staff:
            local_menu.append({'text': 'Zmień uprawnienia', 'path': reverse('fbo:user-auth', args=[self.object.pk])})
        context['local_menu'] = local_menu

        field_list = []
        field_list.append({'header': 'Moduł ATO',  'value': dict(FBOUser._meta.get_field('module_ato').choices)[self.object.module_ato]})
        field_list.append({'header': 'Moduł CAMO', 'value': dict(FBOUser._meta.get_field('module_camo').choices)[self.object.module_camo]})
        field_list.append({'header': 'Moduł SMS',  'value': dict(FBOUser._meta.get_field('module_sms').choices)[self.object.module_sms]})
        field_list.append({'header': 'Moduł FIN',  'value': dict(FBOUser._meta.get_field('module_fin').choices)[self.object.module_fin]})
        field_list.append({'header': 'Moduł RES',  'value': dict(FBOUser._meta.get_field('module_res').choices)[self.object.module_res]})

        context['field_list'] = field_list

        return context


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class FBOUserCreate (CreateView):

    model = FBOUser
    template_name = 'fbo/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(FBOUserCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Nowy użytkownik'
        context['header_text'] = 'Nowy użytkownik systemu'
        return context

    def get_form_class(self, **kwargs):

        class my_user_form(ModelForm):
            class Meta:
                model = FBOUser
                fields = ['login', 'password', 'password1', 'first_name', 'second_name', 'email', 'telephone',
                          'address1', 'address2', 'birth_date', 'pesel', 'id_number', 'infos', 'mechanic',
                          'ncr_user', 'contractor']
                widgets = {'birth_date': AdminDateWidget(),
                           'address1': TextInput(attrs={'size':50}),
                           'address2': TextInput(attrs={'size':50})}

            login = forms.CharField(label='Login')
            login.widget = forms.TextInput()
            password = forms.CharField(label='Hasło')
            password.widget = forms.PasswordInput()
            password1 = forms.CharField(label='Powtórz hasło')
            password1.widget = forms.PasswordInput()

            def clean_password(self):
                if self.data['password'] != self.data['password1']:
                    raise ValidationError(('Oba hasła muszą się zgadzać!'), code='pass_mismatch')
                if len(self.data['password']) < 5:
                    raise ValidationError(('Hasło jest zbyt krótkie!'), code='pass_short')
                return self.data['password']

        return my_user_form

    def form_valid(self, form):

        try:
            user = User.objects.create_user(form.cleaned_data['login'], password=form.cleaned_data['password'], email=form.cleaned_data['email'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['second_name']
            user.save()
        except:
            user = None
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Nie można utworzyć użytkownika!'])
            return super(FBOUserCreate, self).form_invalid(form)

        form.instance.user = user
        return super(FBOUserCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('fbo:user-list')


@class_view_decorator(login_required())
class FBOUserUpdate (UpdateView):
    model = FBOUser
    template_name = 'fbo/update_template.html'

    # jeśli nie superuser to ustaw na zalogowanego
    def get_object(self, queryset=None):
        obj = super(FBOUserUpdate, self).get_object()
        if not self.request.user.is_staff:
            obj = self.request.user.fbouser
        return obj

    def get_context_data(self, **kwargs):
        context = super(FBOUserUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana użytkownika'
        context['header_text'] = 'Zmiana danych użytkownika %s' % self.object.user.username
        context['type'] = 'info'
        context['submenu_template'] = 'panel/user_submenu.html'
        context['fbouser'] = self.object
        context['logged'] = self.request.user.fbouser

        return context

    def get_form_class(self, **kwargs):
        user_form = modelform_factory(FBOUser, fields=['first_name', 'second_name', 'email', 'telephone', 'address1',
                                                       'address2', 'birth_date', 'pesel', 'id_number', 'infos', 'mechanic',
                                                       'ncr_user', 'contractor'],
                                               widgets={'birth_date': AdminDateWidget(),
                                                        'address1': TextInput(attrs={'size':50}),
                                                        'address2': TextInput(attrs={'size':50})})
        if not self.request.user.is_staff:
            user_form.base_fields['contractor'].widget.attrs = {'disabled': 'true'}

        return user_form

    def form_valid(self, form):
        user = self.object.user
        user.first_name = self.object.first_name
        user.last_name = self.object.second_name
        user.email = self.object.email
        user.save()
        return super(FBOUserUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('fbo:user-info', args=[self.object.pk])


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class FBOUserAuth (UpdateView):
    model = FBOUser
    template_name = 'panel/update_template.html'

    def get_context_data(self, **kwargs):
        context = super(FBOUserAuth, self).get_context_data(**kwargs)
        context['page_title'] = 'Zmiana upawnień'
        context['header_text'] = 'Zmiana uprawnień użytkownika %s' % self.object.user.username
        context['type'] = 'modules'
        context['submenu_template'] = 'panel/user_submenu.html'
        context['fbouser'] = self.object
        context['logged'] = self.request.user.fbouser

        return context

    def get_form_class(self, **kwargs):
        user_form = modelform_factory(FBOUser, fields=['module_ato', 'module_camo', 'module_sms', 'module_fin', 'module_res'])
        return user_form

    def get_success_url(self):
        return reverse('fbo:user-modules', args=[self.object.pk])


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class FBOUserDeactivate (DeleteView):
    model = FBOUser
    template_name = 'fbo/activate_template.html'

    def get_context_data(self, **kwargs):
        context = super(FBOUserDeactivate, self).get_context_data(**kwargs)
        context['page_title'] = 'Deaktywacja użytkownika'
        context['header_text'] = 'Deaktywacja użytkownika %s' % self.object.user.username
        context['description'] = 'Użytkownik zostanie oznaczony jako nieaktywny.'
        context['change_text'] = 'deaktywację'
        context['button_text'] = 'Deaktywuj'
        return context

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        object.active = False
        object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('fbo:user-info', args=[self.get_object().pk])


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class FBOUserActivate (DeleteView):
    model = FBOUser
    template_name = 'fbo/activate_template.html'

    def get_context_data(self, **kwargs):
        context = super(FBOUserActivate, self).get_context_data(**kwargs)
        context['page_title'] = 'Aktywacja użytkownika'
        context['header_text'] = 'Aktywacja użytkownika %s' % self.object.user.username
        context['description'] = 'Użytkownik zostanie oznaczony jako aktywny.'
        context['change_text'] = 'aktywację'
        context['button_text'] = 'Aktywuj'
        return context

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        object.active = True
        object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('fbo:user-info', args=[self.get_object().pk])


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class PilotList (ListView):
    model = Pilot
    template_name = 'fbo/list_template.html'

    # Posortuj listę po nazwiskach
    def get_queryset(self):
        return Pilot.objects.order_by('fbouser__second_name')

    def get_context_data(self, **kwargs):
        context = super(PilotList, self).get_context_data(**kwargs)
        context['page_title'] = 'Lista pilotów'
        context['header_text'] = 'Lista pilotów'
        context['empty_text'] = 'Brak zarejestrowanych pilotów.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Utwórz nowego pilota', 'path': reverse("fbo:pilot-create")})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nazwisko\ni imię'})
        header_list.append({'header': 'Naumer\nlicencji'})
        header_list.append({'header': 'Upowaznienie\nSALT'})
        header_list.append({'header': 'Adres\ne-mail'})
        header_list.append({'header': 'Numer\ntelefonu'})
        header_list.append({'header': 'Czas\npracy'})
        header_list.append({'header': '...', 'width': '33px'})
        context['header_list'] = header_list

        # Zawartość tabeli
        row_list = []
        for object in self.object_list:
            fields = []
            fields.append({'name': 'name', 'value': "%s" % object.fbouser, 'link': reverse('panel:pilot-info', args=[object.pk])})
            fields.append({'name': 'licencce', 'value': object.licence})
            fields.append({'name': 'clearance', 'value': object.clearance})
            fields.append({'name': 'email', 'value': object.fbouser.email, 'email': object.fbouser.email})
            fields.append({'name': 'telephone', 'value': object.fbouser.telephone})
            fields.append({'name': 'employee', 'value': ("TAK" if object.employee else "NIE"), 'just': 'center' })
            fields.append({'name': 'change', 'edit_link': reverse('panel:pilot-update', args=[object.pk]),
                           'delete_link': reverse('fbo:pilot-delete', args=[object.pk])})
            row_list.append({'fields': fields})
        context['row_list'] = row_list
        return context


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class PilotCreate (CreateView):
    model = Pilot
    template_name = 'fbo/create_template.html'

    def get_context_data(self, **kwargs):
        context = super(PilotCreate, self).get_context_data(**kwargs)
        context['page_title'] = 'Rejestracja pilota'
        context['header_text'] = 'Rejestracja nowego pilota'
        return context

    def get_form_class(self, **kwargs):
        form_class = modelform_factory(Pilot, fields='__all__', widgets = {'licence_date': AdminDateWidget(),
                                                                           'medical_date': AdminDateWidget(),
                                                                           'remarks':Textarea(attrs={'rows':2, 'cols':100})})
        users = [(user.pk, user) for user in FBOUser.objects.filter(pilot=None).order_by('second_name', 'first_name')]
        form_class.base_fields['fbouser'].choices = [(None, '---------')] + users
        return form_class

    def get_success_url(self):
        return reverse('panel:pilot-info', args=(self.object.pk,))


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class PilotDelete (DeleteView):
    model = Pilot
    template_name = 'fbo/delete_template.html'

    def get_context_data(self, **kwargs):
        context = super(PilotDelete, self).get_context_data(**kwargs)
        context['page_title'] = 'Usunięcie pilota'
        context['header_text'] = 'Usunięcie pilota %s' % self.object
        context['description'] = 'Pilot i związane z nim informacje zostąną usunięte!'
        return context

    def get_success_url(self):
        return reverse('fbo:pilot-list')
