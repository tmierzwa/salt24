from django.db import models
from salt.forms import MyDurationFormField


class MyDurationField(models.DurationField):

    description = 'Simplified Duration Field'

    def formfield(self, **kwargs):
        defaults = {'form_class': MyDurationFormField}
        defaults.update(kwargs)
        return super(MyDurationField, self).formfield(**defaults)
