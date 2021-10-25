from django.db import models

# Parametry konfiguracyjne
class Parameter(models.Model):
    info_priority = models.TextField(blank=True, null=True, verbose_name='Ważne informacje')
    info_body = models.TextField(blank=True, null=True, verbose_name='Pozostałe informacje')
