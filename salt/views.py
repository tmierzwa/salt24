# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.views import LoginView as login, PasswordChangeView as password_change
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from panel.models import FBOUser
from fbo.models import Parameter
from salt.forms import AdminPasswordChangeForm, ParameterChangeForm

def class_view_decorator(function_decorator):

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator


# TODO - zablokować logowanie dla nieaktywnych
def salt_login(request, *args, **kwargs):
    if request.device['is_mobile']:
        kwargs['template_name'] = 'registration/mlogin.html'
    else:
        kwargs['template_name'] = 'registration/login.html'
    return login(request, *args, **kwargs)


def salt_password_change(request, *args, **kwargs):
    kwargs['template_name'] = 'registration/pwd_change.html'
    return password_change(request, *args, **kwargs)


@user_passes_test(lambda u: u.is_staff)
def admin_password_change(request, user_id):

    user = FBOUser.objects.get(pk=user_id).user
    form = AdminPasswordChangeForm(request.POST or None, user=user)

    context = {}
    context['form'] = form
    context['page_title'] = 'Zmiana hasła'
    context['header_text'] = 'Zmiana hasła dla użytkownika %s' % user

    # Jeśli formularz został poprawnie wypełniony
    if form.is_valid():

        form.save()
        if user == request.user:
            update_session_auth_hash(request, user)

        return HttpResponseRedirect(reverse('fbo:user-list'))

    return render(request, 'registration/pwd_change.html', context)


def dispatcher(request):

    params = Parameter.objects.last()
    context = {'mobile': request.device['is_mobile']}

    if params:
        context['infopriority'] = params.info_priority
        context['info'] = params.info_body
    else:
        context['infopriority'] = 0
        context['info'] = ''

    context['infocontact'] = '\n<u>W razie problemów skontaktuj się z:</u>\n\n' +\
                             '<table><tr><td style="padding-right: 50px"><b>Agnieszka Pęksa</b></td>' + \
                             '<td><b>Michał Szamborski</b></td></tr>' + \
                             '<tr><td><a href="mailto:a.peksa@salt.aero">a.peksa@salt.aero</a></td>' +\
                             '<td><a href="mailto:michal.szamborski@salt.aero">michal.szamborski@salt.aero</a></td></tr>' +\
                             '<tr><td>509 054635</td>' +\
                             '<td>601 282808</td></tr></table>'
    if context['mobile']:
        return render(request, 'mdispatcher.html', context)
    else:
        return render(request, 'dispatcher.html', context)


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class ParamsList (ListView):
    model = Parameter
    template_name = 'fbo/list_template.html'

    def get_queryset(self):
        return Parameter.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ParamsList, self).get_context_data(**kwargs)
        context['page_title'] = 'Parametry'
        context['header_text'] = 'Parametry systemowe'
        context['empty_text'] = 'Brak parametrów.'

        # Lokalne menu
        local_menu = []
        local_menu.append({'text': 'Zmiana parametrów', 'path': reverse("fbo:parameters-update", args=[1])})
        context['local_menu'] = local_menu

        # Nagłówki tabeli
        header_list = []
        header_list.append({'header': 'Nazwa parametru'})
        header_list.append({'header': 'Wartość parametru'})
        context['header_list'] = header_list

        row_list = []
        object = self.object_list.last()
        for model_field in Parameter._meta.get_fields():
            fields = []
            if model_field.name != 'id':
                fields.append({'name': model_field.name, 'value': model_field.verbose_name, 'bold': True})
                fields.append({'name': model_field.name, 'value': getattr(object, model_field.name)})
                row_list.append({'fields': fields})
        context['row_list'] = row_list
        context['no_paging'] = True

        return context


@class_view_decorator(user_passes_test(lambda u: u.is_staff))
class ParamsUpdate (UpdateView):
    model = Parameter
    template_name = 'fbo/params_template.html'

    def get_context_data(self, **kwargs):
        context = super(ParamsUpdate, self).get_context_data(**kwargs)
        context['page_title'] = 'Parametry systemu'
        context['header_text'] = 'Modyfikacja parametrów systemowych'
        return context

    def get_form_class(self, **kwargs):
        form_class = ParameterChangeForm
        return form_class

    def get_success_url(self):
        return reverse('fbo:parameters')