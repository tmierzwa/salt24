# -*- coding: utf-8 -*-

import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

from ato.models import Training, Training_inst, Phase_inst, Exercise_inst

def to_duration(value):
    if value:
        return datetime.timedelta(seconds=value.hour*60*60 + value.minute*60)
    else:
        return None

def update_trainings(request):
    for training in Training.objects.all():
        for phase in training.phase_set.all():
            phase.new_min_time_instr = to_duration(phase.min_time_instr)
            phase.new_min_time_solo = to_duration(phase.min_time_solo)
            phase.full_clean()
            phase.save()
            for exercise in phase.exercise_set.all():
                exercise.new_min_time_instr = to_duration(exercise.min_time_instr)
                exercise.new_min_time_solo = to_duration(exercise.min_time_solo)
                exercise.full_clean()
                exercise.save()
    for training in Training_inst.objects.all():
        for phase in training.phase_inst_set.all():
            phase.new_min_time_instr = to_duration(phase.min_time_instr)
            phase.new_min_time_solo = to_duration(phase.min_time_solo)
            phase.full_clean()
            phase.save()
            for exercise in phase.exercise_inst_set.all():
                exercise.new_min_time_instr = to_duration(exercise.min_time_instr)
                exercise.new_min_time_solo = to_duration(exercise.min_time_solo)
                exercise.new_time_instr = to_duration(exercise.time_instr)
                exercise.new_time_solo = to_duration(exercise.time_solo)
                exercise.full_clean()
                exercise.save()

    return HttpResponseRedirect(reverse('ato:training-list'))


def update_phases(request):

    for training_inst in Training_inst.objects.all():

        # Usuń istniejące fazy i zadania
        for phase_inst in training_inst.phase_inst_set.all():
            for exercise_inst in phase_inst.exercise_inst_set.all():
                exercise_inst.delete()
            phase_inst.delete()

        # Skopiuj zadania według programu #
        for phase in training_inst.training.phase_set.all():
            phase_inst = Phase_inst(training_inst=training_inst,
                                    code=phase.code,
                                    name=phase.name,
                                    description=phase.description,
                                    min_time_instr=phase.min_time_instr,
                                    min_time_solo=phase.min_time_solo)
            phase_inst.full_clean()
            phase_inst.save()

            # Skopiuj ćwiczenia według programu #
            for exercise in phase.exercise_set.all():
                exercise_inst = Exercise_inst(phase_inst=phase_inst,
                                              code=exercise.code,
                                              name=exercise.name,
                                              description=exercise.description,
                                              restrictions=exercise.restrictions,
                                              min_time_instr=exercise.min_time_instr,
                                              min_time_solo=exercise.min_time_solo,
                                              min_num_instr=exercise.min_num_instr,
                                              min_num_solo=exercise.min_num_solo)
                exercise_inst.full_clean()
                exercise_inst.save()

            # Przypisz właściwe poprzedniki dla ćwiczeń #
            for exercise_inst in phase_inst.exercise_inst_set.all():
                exercise = phase.exercise_set.filter(code=exercise_inst.code).first()
                if exercise:
                    if exercise.predecessor:
                        new_predecessor = phase_inst.exercise_inst_set.filter(code=exercise.predecessor.code).first()
                        if new_predecessor:
                            exercise_inst.predecessor = new_predecessor
                            exercise_inst.full_clean()
                            exercise_inst.save()

        # Przypisz właściwe poprzedniki dla zadań #
        for phase_inst in training_inst.phase_inst_set.all():
            phase = training_inst.training.phase_set.filter(code=phase_inst.code).first()
            if phase:
                if phase.predecessor:
                    new_predecessor = training_inst.phase_inst_set.filter(code=phase.predecessor.code)
                    if new_predecessor:
                        phase_inst.predecessor = new_predecessor.first()
                        phase_inst.full_clean()
                        phase_inst.save()

    return HttpResponseRedirect(reverse('ato:training-inst-list'))
