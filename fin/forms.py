from django import forms
from datetime import date
from fin.models import RentPackage
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import Textarea, TextInput
from django.core.exceptions import ValidationError


class PackageBuyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.contractor = kwargs.pop('contractor')
        super(PackageBuyForm, self).__init__(*args, **kwargs)
        choices = []
        for package in RentPackage.objects.all():
            label = ''
            label += '<td style="text-align: center"><b>%s</b></td>' % package.package_id
            label += '<td>%s</td>' % package.name
            label += '<td style="text-align: center">%s</td>' % package.ac_type
            label += '<td style="text-align: center">%d</td>' % package.hours
            label += '<td style="text-align: center">%.2f PLN</td>' % package.hour_price
            label += '<td>%s</td>' % package.remarks
            choices.append ((package.pk, label))

        self.fields['packages'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())
        self.fields['packages'].error_messages['required'] = 'Należy wybrać pakiet!'
        self.fields['packages'].error_messages['no_money'] = 'Brak środków na rachunku!'

        self.fields['date'] = forms.DateField(widget=AdminDateWidget())
        self.fields['date'].initial = date.today()

        self.fields['remarks'] = forms.CharField(widget=Textarea(attrs={'rows':2, 'cols':100}))
        self.fields['remarks'].required = False

    def clean_packages(self, **kwargs):
        cleaned_data = super(PackageBuyForm, self).clean()
        package = RentPackage.objects.get(pk = cleaned_data['packages'])
        if self.contractor.rent_balance < package.hours * package.hour_price:
            raise ValidationError(('Zbyt mało środków na rachunku!'), code='no_money')
        return cleaned_data['packages']

