# -*- coding: utf-8 -*-

from django import forms
from django.forms import Textarea, CharField, HiddenInput
from ato.models import Exercise_oper
from django.core.exceptions import ValidationError

from salt.forms import duration_string

class ExercOperCreateForm(forms.ModelForm):
    class Meta:
        model = Exercise_oper
        exclude = ['exercise_inst']
        widgets = {'remarks': Textarea(attrs={'rows': 5, 'cols': 100}),}

    def __init__(self, *args, **kwargs):

        self.choices = kwargs.pop('choices', None)
        super(ExercOperCreateForm, self).__init__(*args, **kwargs)

        self.fields['operation'].choices = [(str(operation.pk), '%s - (%s %s): %s-%s' % (
            operation.pdt.aircraft, operation.pdt.date, operation.time_start.strftime('%H:%M'),
            operation.loc_start, operation.loc_end)) for operation in self.choices]

        self.fields['operation'].choices.insert(0, (0, '---------'))

        self.fields['time_oper0'] = CharField(initial='00:00', widget=HiddenInput(), required=False)
        self.fields['num_oper0'] = CharField(initial=0, widget=HiddenInput(), required=False)
        self.fields['solo_oper0'] = CharField(initial=False, widget=HiddenInput(), required=False)

        for operation in self.choices:
            self.fields['time_oper%d' % operation.pk] = CharField(initial=duration_string(operation.not_allocated_time()), widget=HiddenInput(), required=False)
            self.fields['num_oper%d' % operation.pk] = CharField(initial=operation.not_allocated_ldg(), widget=HiddenInput(), required=False)
            self.fields['solo_oper%d' % operation.pk] = CharField(initial=not operation.pdt.sic, widget=HiddenInput(), required=False)
        return

    def clean_time_allocated(self):
        cleaned_data = super(ExercOperCreateForm, self).clean()
        if not cleaned_data['time_allocated']:
            raise ValidationError('Podaj czas ćwiczenia.', code='no_time')
        if cleaned_data['time_allocated'].seconds == 0:
            raise ValidationError('Niepoprawny czas ćwiczenia!', code='zero_time')
        return cleaned_data['time_allocated']

    def clean_num_allocated(self):
        cleaned_data = super(ExercOperCreateForm, self).clean()
        if not cleaned_data['num_allocated']:
            raise ValidationError('Podaj liczbę powtórzeń.', code='no_num')
        if cleaned_data['num_allocated'] <= 0:
            raise ValidationError('Liczba powtórzeń musi być większa od zera!', code='zero_num')
        return cleaned_data['num_allocated']

    def clean(self):
        cleaned_data = super(ExercOperCreateForm, self).clean()
        if cleaned_data.get('operation'):
            if cleaned_data.get('time_allocated'):
                if cleaned_data['time_allocated'].seconds > cleaned_data['operation'].not_allocated_time().seconds:
                    raise ValidationError('Czas ćwiczenia jest dłuższy niż czas operacji!', code='wrong_time')
            if cleaned_data.get('num_allocated'):
                if cleaned_data['num_allocated'] > cleaned_data['operation'].not_allocated_ldg():
                    raise ValidationError('Liczba powtórzeń większa niż liczba lądowań!', code='wrong_num')
        return cleaned_data


