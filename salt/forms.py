from datetime import timedelta

from django import forms
from django.utils.dateparse import parse_duration
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms import Textarea

from fbo.models import Parameter

def duration_string(duration):

    if duration:
        seconds = duration.seconds
        days = duration.days

        minutes = seconds // 60

        hours = minutes // 60
        minutes = minutes % 60

        hours += days * 24

        string = '{:02d}:{:02d}'.format(hours, minutes)
    else:
        string = '00:00'

    return string


class MyDurationFormField(forms.Field):
    default_error_messages = {
        'invalid': _('Enter a valid duration.'),
    }

    def prepare_value(self, value):
        if isinstance(value, timedelta):
            return duration_string(value)
        return value

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, timedelta):
            return value
        value = parse_duration(value + ':00')
        if value is None:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class AdminPasswordChangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'] = forms.CharField(label="Podaj hasło", widget=forms.PasswordInput)
        self.fields['new_password2'] = forms.CharField(label="Powtórz hasło", widget=forms.PasswordInput)

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Podane hasła różnią się od siebie!", code='password_mismatch')
        return new_password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user

    # def _get_changed_data(self):
    #     data = super(AdminPasswordChangeForm, self).changed_data
    #     for name in self.fields.keys():
    #         if name not in data:
    #             return []
    #     return ['password']
    # changed_data = property(_get_changed_data)


class ParameterChangeForm(forms.ModelForm):

    class Meta:
        model = Parameter
        fields = ['info_priority', 'info_body']
        widgets = {'info_priority': Textarea(attrs={'rows': 3, 'cols': 100}),
                   'info_body': Textarea(attrs={'rows': 10, 'cols': 100})}
