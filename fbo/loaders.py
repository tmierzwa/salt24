import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Permission

from panel.models import FBOUser, PDT, Duty, FlightTypes
from camo.models import Aircraft
from fbo.models import Parameter

def create_fbouser(request):
    if not hasattr(request.user, 'fbouser'):
        fbouser = FBOUser(user=request.user, first_name=request.user.first_name, second_name=request.user.last_name,
                          email=request.user.email)
        fbouser.full_clean()
        fbouser.save()

    return HttpResponseRedirect(reverse('dispatcher'))


def update_auth(request):

    for fbouser in FBOUser.objects.all():
        fbouser.save()

    return HttpResponseRedirect(reverse('dispatcher'))


def update_duties(request):

    for duty in Duty.objects.all():
        if str(duty.remarks)[9:12] == 'PDT' and not duty.pdt:
            try:
                aircraft = Aircraft.objects.get(registration=duty.remarks[0:6])
                pdt_ref = int(duty.remarks[13:])
                pdt = PDT.objects.get(aircraft=aircraft, pdt_ref=pdt_ref)
            except:
                pdt = None

            if pdt:
                duty.delete()
                pdt.save()

    return HttpResponseRedirect(reverse('dispatcher'))


def new_params(request):

    parameter = Parameter (
                info_priority = 'Uwaga! Od 14.03.2017 r. wprowadziliśmy nowy format e-PDT.\n',
                info_body = 'Na niektórych komputerach po załadowaniu strony otwierającej e-PDT\n' + \
                          'może być konieczne jednorazowe wciśnięcie CTRL+F5 w celu poprawnego przeładowania.\n')
    parameter.save()

    return HttpResponseRedirect(reverse('dispatcher'))


def orderpdt(request):

    for aircraft in Aircraft.objects.all():
        prev_pdt = None
        for pdt in aircraft.pdt_set.order_by('date', 'tth_start', 'pdt_ref', 'open_time').reverse():
            pdt.next_pdt = prev_pdt
            pdt.save()
            prev_pdt = pdt

