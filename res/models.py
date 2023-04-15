import babel.dates
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from salt.models import MyDurationField
from salt.utils import SendMessage

from camo.models import Aircraft
from panel.models import FBOUser, Pilot, FlightTypes


class Module(models.Model):

    class Meta:
        permissions = [('res_user', 'REZERWACJE - Dostęp do modułu'),
                       ('res_admin', 'REZERWACJE - Zarządzanie')]

    module = models.BooleanField()


# Rezerwacja SP
class Reservation(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    owner = models.ForeignKey(Pilot, related_name='res_owner_set', verbose_name='Właściciel rezerwacji', on_delete=models.CASCADE)
    participant = models.ForeignKey(Pilot, related_name='res_participant_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Uczestnik rezerwacji')
    start_time = models.DateTimeField(verbose_name='Termin rozpoczęcia')
    end_time = models.DateTimeField(verbose_name='Termin zakończenia')
    planned_type = models.CharField(max_length=3, choices=FlightTypes().items(), verbose_name='Planowany rodzaj lotu')
    planned_time = MyDurationField(verbose_name='Planowany czas lotu')
    loc_start = models.TextField(blank=True, null=True, default='EPMO', verbose_name='Lotnisko startu')
    loc_stop = models.TextField(blank=True, null=True, verbose_name='Pierwszy odcinek')
    loc_end = models.TextField(blank=True, null=True, verbose_name='Dalsze odcinki')
    pax = models.TextField(blank=True, null=True, verbose_name='Lista pasażerów')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    internal_remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi SALT')
    status = models.CharField(max_length=12, choices=[('Nowa', 'Nowa'), ('Potwierdzona', 'Potwierdzona'), ('Zrealizowana', 'Zrealizowana')],
                              default='Nowa', verbose_name='Status rezerwacji')
    open_user = models.ForeignKey(FBOUser, related_name='res_open_by_set', verbose_name='Utworzona przez', on_delete=models.CASCADE)
    open_time = models.DateTimeField(auto_now_add=True, verbose_name='Termin otwarcia')
    change_user = models.ForeignKey(FBOUser, related_name='res_changed_by_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zmodyfikowana przez')
    change_time = models.DateTimeField(auto_now=True, verbose_name='Termin ostatniej modyfikacji')

    def __str__(self):
        return '%s %s - %s' % (self.aircraft, '{:%Y-%m-%d %H:%M}'.format(self.start_time), '{:%Y-%m-%d %H:%M}'.format(self.end_time))

    def save(self, *args, **kwargs):

        send_to = []

        # Sprawdzenie, czy rezerwacja już istnieje
        try:
            existing = Reservation.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # Skomponowanie wiadomości
        if existing:
            if existing.aircraft != self.aircraft or existing.owner != self.owner or \
               existing.participant != self.participant or existing.start_time != self.start_time or \
               existing.end_time != self.end_time or existing.planned_type != self.planned_type or \
               existing.planned_time != self.planned_time or existing.loc_start != self.loc_start or \
               existing.loc_stop != self.loc_stop or existing.loc_end != self.loc_end or \
               existing.remarks != self.remarks or existing.status != self.status:

                # Jeśli zmieniło się coś istotnego
                if self.owner and self.owner.fbouser != self.change_user:
                    send_to.append(self.owner.fbouser)
                if self.participant and self.participant.fbouser != self.change_user:
                    send_to.append(self.participant.fbouser)

            message = 'Rezerwacja %s z twoim udziałem rozpoczynająca się w %s o %s została zmieniona przez %s.' % \
                      (self.aircraft, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                       self.start_time.strftime("%H:%M"), self.change_user.__str__())
        else:
            if self.owner and self.owner.fbouser != self.open_user:
                send_to.append(self.owner.fbouser)
            if self.participant and self.participant.fbouser != self.open_user:
                send_to.append(self.participant.fbouser)

            message = 'Rezerwacja %s z twoim udziałem rozpoczynająca się w %s o %s została dodana przez %s.' % \
                      (self.aircraft, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                       self.start_time.strftime("%H:%M"), self.open_user.__str__())

        # Zmiana rezerwacji
        res = super(Reservation, self).save(*args, **kwargs)

        # Wysłanie wiadomości do wszystkich adresatów
        for fbouser in send_to:
            SendMessage(fbouser, message)

        return res

    def delete(self, *args, **kwargs):

        send_to = []

        # Skomponowanie wiadomości
        if self.owner and self.owner.fbouser != self.change_user:
            send_to.append(self.owner.fbouser)
        if self.participant and self.participant.fbouser != self.change_user:
            send_to.append(self.participant.fbouser)

        people = " Właściciel: %s." % self.owner.fbouser.__str__()
        if self.participant:
            people += " Uczestnik: %s." % self.participant.fbouser.__str__()

        remarks = ''
        if self.remarks:
            remarks = " Uwagi: %s" % self.remarks

        message = 'Rezerwacja %s rozpoczynająca się w %s o %s została usunięta przez %s.' % \
                  (self.aircraft, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                   self.start_time.strftime("%H:%M"), self.change_user.__str__())
        message += people
        message += remarks

        # Usunięcie rezerwacji
        res = super(Reservation, self).delete(*args, **kwargs)

        # Wysłanie wiadomości do wszystkich adresatów
        for fbouser in send_to:
            SendMessage(fbouser, message)

        return res


# Niedostępność
class Blackout(models.Model):
    aircraft = models.ForeignKey(Aircraft, verbose_name='Statek powietrzny', on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name='Termin rozpoczęcia')
    end_time = models.DateTimeField(verbose_name='Termin zakończenia')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    open_user = models.ForeignKey(FBOUser, verbose_name='Utworzone przez', on_delete=models.CASCADE)
    open_time = models.DateTimeField(auto_now_add=True, verbose_name='Termin utworzenia')

    def __str__(self):
        return '%s %s - %s' % (self.aircraft, '{:%Y-%m-%d %H:%M}'.format(self.start_time), '{:%Y-%m-%d %H:%M}'.format(self.end_time))


# Zasób FBO
class ResourceFBO(models.Model):
    name = models.CharField(unique=True, max_length=20, verbose_name='Nazwa zasobu')
    description = models.TextField(blank=True, null=True, verbose_name='Opis zasobu')
    scheduled = models.BooleanField(default=True, verbose_name='Podlega rezerwacjom')
    info = models.TextField(blank=True, null=True, verbose_name='Informacje dla użytkowników')
    color = models.CharField(max_length=7, default='#cdcdcd', verbose_name='Kolor wyświetlania')

    def __str__(self):
        return self.name


# Rezerwacja FBO
class ReservationFBO(models.Model):
    resource = models.ForeignKey(ResourceFBO, verbose_name='Rezerwowany zasób', on_delete=models.CASCADE)
    owner = models.ForeignKey(FBOUser, related_name='resfbo_owner_set', verbose_name='Właściciel rezerwacji', on_delete=models.CASCADE)
    participant = models.ForeignKey(FBOUser, related_name='resfbo_participant_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Uczestnik rezerwacji')
    start_time = models.DateTimeField(verbose_name='Termin rozpoczęcia')
    end_time = models.DateTimeField(verbose_name='Termin zakończenia')
    title = models.CharField(max_length=30, verbose_name='Tytuł rezerwacji')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    open_user = models.ForeignKey(FBOUser, related_name='resfbo_open_by_set', verbose_name='Utworzona przez', on_delete=models.CASCADE)
    open_time = models.DateTimeField(auto_now_add=True, verbose_name='Termin otwarcia')
    change_user = models.ForeignKey(FBOUser, related_name='resfbo_changed_by_set', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Zmodyfikowana przez')
    change_time = models.DateTimeField(auto_now=True, verbose_name='Termin ostatniej modyfikacji')

    def __str__(self):
        return '%s %s - %s' % (self.resource, '{:%Y-%m-%d %H:%M}'.format(self.start_time), '{:%Y-%m-%d %H:%M}'.format(self.end_time))

    def save(self, *args, **kwargs):

        send_to = []

        # Sprawdzenie, czy rezerwacja już istnieje
        try:
            existing = ReservationFBO.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # Skomponowanie wiadomości
        if existing:
            if existing.resource != self.resource or existing.owner != self.owner or \
               existing.participant != self.participant or existing.start_time != self.start_time or \
               existing.end_time != self.end_time or existing.title != self.title or \
               existing.remarks != self.remarks:

                # Jeśli zmieniło się coś istotnego
                if self.owner and self.owner != self.change_user:
                    send_to.append(self.owner)
                if self.participant and self.participant != self.change_user:
                    send_to.append(self.participant)

            message = 'Rezerwacja %s z twoim udziałem rozpoczynająca się w %s o %s została zmieniona przez %s.' % \
                      (self.resource, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                       self.start_time.strftime("%H:%M"), self.change_user.__str__())
        else:
            if self.owner and self.owner != self.open_user:
                send_to.append(self.owner)
            if self.participant and self.participant != self.open_user:
                send_to.append(self.participant)

            message = 'Rezerwacja %s z twoim udziałem rozpoczynająca się w %s o %s została dodana przez %s.' % \
                      (self.resource, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                       self.start_time.strftime("%H:%M"), self.open_user.__str__())

        # Zmiana rezerwacji
        res = super(ReservationFBO, self).save(*args, **kwargs)

        # Jeśli nie 'INFOS' to wysłanie wiadomości do wszystkich adresatów
        if self.resource.name != 'INFOS':
            for fbouser in send_to:
                SendMessage(fbouser, message)

        return res

    def delete(self, *args, **kwargs):

        send_to = []

        # Skomponowanie wiadomości
        if self.owner and self.owner != self.change_user:
            send_to.append(self.owner)
        if self.participant and self.participant != self.change_user:
            send_to.append(self.participant)

        message = 'Rezerwacja %s z twoim udziałem rozpoczynająca się w %s o %s została usunięta przez %s.' % \
                  (self.resource, babel.dates.format_date(self.start_time, "EEE d MMMM", locale='pl_PL'),
                   self.start_time.strftime("%H:%M"), self.change_user.__str__())

        # Usunięcie rezerwacji
        res = super(ReservationFBO, self).delete(*args, **kwargs)

        # Wysłanie wiadomości do wszystkich adresatów
        for fbouser in send_to:
            SendMessage(fbouser, message)

        return res
