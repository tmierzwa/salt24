# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from salt.models import MyDurationField


class Module(models.Model):

    class Meta:
        permissions = [('ato_reader', 'ATO - Dostęp do odczytu'),
                       ('ato_admin', 'ATO - Dostęp pełny')]

    module = models.BooleanField()


class Training(models.Model):
    code = models.CharField(max_length=10, verbose_name='Kod szkolenia')
    name = models.CharField(max_length=100, verbose_name='Nazwa szkolenia')
    date = models.DateField(blank=True, null=True, verbose_name='Data wprowadenia programu')
    description = models.TextField(blank=True, null=True, verbose_name='Opis szkolenia')

    def __str__(self):
        return self.code


class Phase(models.Model):
    training = models.ForeignKey(Training, verbose_name='Szkolenie', on_delete=models.CASCADE)
    code = models.CharField(max_length=12, verbose_name='Kod zadania/fazy')
    name = models.CharField(max_length=120, verbose_name='Nazwa zadania/fazy')
    description = models.TextField(blank=True, null=True, verbose_name='Opis zadania/fazy')
    predecessor = models.ForeignKey('Phase', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Wymagane poprzednie zdanie/faza')
    min_time_instr = MyDurationField(blank=True, null=True, verbose_name='Min. czas z instr.')
    min_time_solo = MyDurationField(blank=True, null=True, verbose_name='Min. czas solo')

    def __str__(self):
        return "%s / %s" % (self.training.code, self.code)


class Exercise(models.Model):
    phase = models.ForeignKey(Phase, verbose_name='Zadanie/faza', on_delete=models.CASCADE)
    code = models.CharField(max_length=12, verbose_name='Kod ćwiczenia')
    name = models.CharField(max_length=150, verbose_name='Nazwa ćwiczenia')
    description = models.TextField(blank=True, null=True, verbose_name='Opis ćwiczenia')
    restrictions = models.CharField(max_length=3, choices=[('TAK','TAK'), ('NIE','NIE')], default='NIE', verbose_name='Restrykcje na instruktora')
    predecessor = models.ForeignKey('Exercise', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Wymagane poprzednie ćwiczenie')
    min_time_instr = MyDurationField(blank=True, null=True, verbose_name='Min. czas z instr.')
    min_time_solo = MyDurationField(blank=True, null=True, verbose_name='Min. czas solo')
    min_num_instr = models.IntegerField(blank=True, null=True, verbose_name='Min. liczba powtórzeń z instr.')
    min_num_solo  = models.IntegerField(blank=True, null=True, verbose_name='Min. liczba powtórzeń solo')

    def __str__(self):
        return "%s / %s" % (self.phase, self.code)


class Student(models.Model):
    pilot = models.OneToOneField('panel.Pilot', on_delete=models.CASCADE, verbose_name='Pilot')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return self.pilot.__str__()


class Instructor(models.Model):
    pilot = models.OneToOneField('panel.Pilot', on_delete=models.CASCADE, verbose_name='Pilot')
    restrictions = models.CharField(max_length=3, choices=[('TAK','TAK'), ('NIE','NIE')], default='NIE', verbose_name='Restrykcje')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return self.pilot.__str__()


class Training_inst(models.Model):
    training = models.ForeignKey(Training, verbose_name='Szkolenie', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name='Student', on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, verbose_name='Instruktor prowadzący', on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Data rozpoczęcia')
    passed = models.CharField(max_length=3, choices=[('TAK','TAK'), ('NIE','NIE')], default='NIE', verbose_name='Ukończone')
    pass_date = models.DateField(blank=True, null=True, verbose_name='Data ukończenia')
    open =  models.BooleanField(default=True, verbose_name='Czy otwarte')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return u'%s dla %s' % (self.training.code, self.student)

    def time_instr(self):
        time_instr = datetime.timedelta(seconds=0)
        for phase in self.phase_inst_set.all():
            if phase.time_instr():
                time_instr += phase.time_instr()
        return time_instr

    def time_solo(self):
        time_solo = datetime.timedelta(seconds=0)
        for phase in self.phase_inst_set.all():
            if phase.time_solo():
                time_solo += phase.time_solo()
        return time_solo

    def status(self):
        num_passed, num = 0, 0
        for phase_inst in self.phase_inst_set.all():
            for exercise_inst in phase_inst.exercise_inst_set.all():
                num += 1
                num_passed += (1 if exercise_inst.passed=='TAK' else 0)

        if self.open:
            if self.passed == 'TAK':
                return "Ukończone"
            else:
                if num_passed == 0:
                    return "Nowe"
                elif num != 0:
                    return "W trakcie (%.1f%%)" % (num_passed*100/num)
                else:
                    return "W trakcie"
        else:
            return "Zamknięte"


class Phase_inst(models.Model):
    training_inst = models.ForeignKey(Training_inst, verbose_name='Szkolenie', on_delete=models.CASCADE)
    code = models.CharField(max_length=12, verbose_name='Kod zadania/fazy')
    name = models.CharField(max_length=120, verbose_name='Nazwa zadania/fazy')
    description = models.TextField(blank=True, null=True, verbose_name='Opis zadania/fazy')
    predecessor = models.ForeignKey('Phase_inst', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Wymagane poprzednie zdanie/faza')
    min_time_instr = MyDurationField(blank=True, null=True, verbose_name='Min. czas z instr.')
    min_time_solo = MyDurationField(blank=True, null=True, verbose_name='Min. czas solo')
    passed = models.CharField(max_length=3, choices=[('TAK','TAK'), ('NIE','NIE')], default='NIE', verbose_name='Zaliczenie')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return "%s / %s" % (self.training_inst.training.code, self.code)

    def time_instr(self):
        time_instr = datetime.timedelta(seconds=0)
        for exercise in self.exercise_inst_set.all():
            if exercise.time_instr:
                time_instr += exercise.time_instr
        return time_instr

    def time_solo(self):
        time_solo = datetime.timedelta(seconds=0)
        for exercise in self.exercise_inst_set.all():
            if exercise.time_solo:
                time_solo += exercise.time_solo
        return time_solo


class Exercise_inst(models.Model):
    phase_inst = models.ForeignKey(Phase_inst, verbose_name='Zadanie/faza', on_delete=models.CASCADE)
    code = models.CharField(max_length=12, verbose_name='Kod ćwiczenia')
    name = models.CharField(max_length=150, verbose_name='Nazwa ćwiczenia')
    description = models.TextField(blank=True, null=True, verbose_name='Opis ćwiczenia')
    restrictions = models.CharField(max_length=3, choices=[('TAK', 'TAK'), ('NIE', 'NIE')], default='NIE',
                                    verbose_name='Restrykcje na instruktora')
    predecessor = models.ForeignKey('Exercise_inst', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Wymagane poprzednie ćwiczenie')
    min_time_instr = MyDurationField(blank=True, null=True, verbose_name='Min. czas z instr.')
    min_time_solo = MyDurationField(blank=True, null=True, verbose_name='Min. czas solo')
    min_num_instr = models.IntegerField(blank=True, null=True, verbose_name='Min. liczba powtórzeń z instr.')
    min_num_solo  = models.IntegerField(blank=True, null=True, verbose_name='Min. liczba powtórzeń solo')
    time_instr = MyDurationField(blank=True, null=True, verbose_name='Czas z instr.')
    time_solo = MyDurationField(blank=True, null=True, verbose_name='Czas solo')
    num_instr = models.IntegerField(default=0, verbose_name='Liczba powtórzeń z instr.')
    num_solo  = models.IntegerField(default=0, verbose_name='Liczba powtórzeń solo')
    passed = models.CharField(max_length=3, choices=[('TAK','TAK'), ('NIE','NIE')], default='NIE', verbose_name='Zaliczenie')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return "%s / %s" % (self.phase_inst, self.code)


class Exercise_oper(models.Model):
    exercise_inst = models.ForeignKey(Exercise_inst, verbose_name='Cwiczenie', on_delete=models.CASCADE)
    operation = models.ForeignKey('panel.Operation', verbose_name='Operacja', on_delete=models.CASCADE)
    solo = models.BooleanField(default=False, verbose_name='Lot solo')
    time_allocated = MyDurationField(default=datetime.timedelta(seconds=0), verbose_name='Czas ćwiczenia')
    num_allocated = models.IntegerField(default=0, verbose_name='Liczba powtórzeń ćwiczenia')
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')

    def __str__(self):
        return "Operacja z dnia: %s, %s - %s" % (self.operation.pdt.date, self.operation.loc_start, self.operation.loc_end)

    def save(self, *args, **kwargs):
        # sprawdź czy nowy rekord czy zmiana istniejącego #
        try:
            existing = Exercise_oper.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj liczniki w ćwiczeniu #
        if existing:
            if existing.solo:
                self.exercise_inst.time_solo -= existing.time_allocated
                self.exercise_inst.num_solo -= existing.num_allocated
            else:
                self.exercise_inst.time_instr -= existing.time_allocated
                self.exercise_inst.num_instr -= existing.num_allocated
        if self.solo:
            self.exercise_inst.time_solo = (self.exercise_inst.time_solo or datetime.timedelta(seconds=0)) + self.time_allocated
            self.exercise_inst.num_solo = (self.exercise_inst.num_solo or 0) + self.num_allocated
        else:
            self.exercise_inst.time_instr = (self.exercise_inst.time_instr or datetime.timedelta(seconds=0)) + self.time_allocated
            self.exercise_inst.num_instr = (self.exercise_inst.num_instr or 0) + self.num_allocated

        self.exercise_inst.full_clean()
        self.exercise_inst.save()
        return super(Exercise_oper, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # zaktualizuj liczniki w ćwiczeniu #
        self.exercise_inst.time_instr -= self.time_allocated
        self.exercise_inst.num_instr -= self.num_allocated

        self.exercise_inst.full_clean()
        self.exercise_inst.save()
        return super(Exercise_oper, self).delete(*args, **kwargs)


class Card_entry(models.Model):
    training_inst = models.ForeignKey(Training_inst, verbose_name='Szkolenie', on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, verbose_name='Instruktor', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Data lotów')
    pdt_num = models.CharField(max_length=12, blank=True, null=True, verbose_name='Numer PDT')
    exercise_inst = models.ForeignKey(Exercise_inst, verbose_name='Cwiczenie', on_delete=models.CASCADE)
    dual_time = MyDurationField(default=datetime.timedelta(seconds=0), verbose_name='Czas dwuster')
    dual_num = models.IntegerField(default=0, verbose_name='Liczba powtórzeń dwuster')
    solo_time = MyDurationField(default=datetime.timedelta(seconds=0), verbose_name='Czas solo')
    solo_num = models.IntegerField(default=0, verbose_name='Liczba powtórzeń solo')
    passed = models.IntegerField(choices=[(0, 'Kontynuacja'), (1, 'Zaliczenie')], default=0, verbose_name="Zaliczenie")
    remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi')
    internal_remarks = models.TextField(blank=True, null=True, verbose_name='Uwagi dla instruktorów')

    def __str__(self):
        return "Wpis z dnia %s" % self.date

    def save(self, *args, **kwargs):
        # sprawdź czy nowy rekord czy zmiana istniejącego #
        try:
            existing = Card_entry.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            existing = None

        # zaktualizuj liczniki w ćwiczeniu #
        if existing:
            existing.exercise_inst.time_instr -= existing.dual_time
            existing.exercise_inst.num_instr -= existing.dual_num
            existing.exercise_inst.time_solo -= existing.solo_time
            existing.exercise_inst.num_solo -= existing.solo_num
            existing.exercise_inst.full_clean()
            existing.exercise_inst.save()
            self.exercise_inst.refresh_from_db()

        self.exercise_inst.time_instr = (self.exercise_inst.time_instr or datetime.timedelta(seconds=0)) + self.dual_time
        self.exercise_inst.num_instr = (self.exercise_inst.num_instr or 0) + self.dual_num
        self.exercise_inst.time_solo = (self.exercise_inst.time_solo or datetime.timedelta(seconds=0)) + self.solo_time
        self.exercise_inst.num_solo = (self.exercise_inst.num_solo or 0) + self.solo_num

        # zaktualizuj status zaliczenia ćwiczenia #
        if self.exercise_inst.passed == 'NIE' and self.passed == 1:
            self.exercise_inst.passed = 'TAK'

        self.exercise_inst.full_clean()
        self.exercise_inst.save()
        return super(Card_entry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # zaktualizuj liczniki w ćwiczeniu #
        self.exercise_inst.time_instr -= self.dual_time
        self.exercise_inst.num_instr -= self.dual_num
        self.exercise_inst.time_solo -= self.solo_time
        self.exercise_inst.num_solo -= self.solo_num

        self.exercise_inst.full_clean()
        self.exercise_inst.save()
        return super(Card_entry, self).delete(*args, **kwargs)
