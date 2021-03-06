# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 21:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50, verbose_name='Typ SP')),
                ('registration', models.CharField(max_length=12, verbose_name='Rejestracja')),
                ('helicopter', models.BooleanField(default=False, verbose_name='Śmigłowiec')),
                ('status', models.CharField(choices=[('flying', 'W użytkowaniu'), ('damaged', 'Uszkodzony'), ('parked', 'Zaparkowany')], max_length=10, verbose_name='Status użytkowania')),
                ('production_date', models.DateField(verbose_name='Data producji')),
                ('mtow', models.IntegerField(verbose_name='MTOW')),
                ('insurance_date', models.DateField(blank=True, null=True, verbose_name='Ważność ubezp.')),
                ('wb_date', models.DateField(blank=True, null=True, verbose_name='Ważność W&B')),
                ('arc_date', models.DateField(blank=True, null=True, verbose_name='Ważność ARC')),
                ('radio_date', models.DateField(blank=True, null=True, verbose_name='Ważność radia')),
                ('hours_count', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Suma TTH')),
                ('landings_count', models.IntegerField(default=0, verbose_name='Suma lądowań')),
                ('use_landings', models.BooleanField(default=False, verbose_name='Używaj lądowań')),
                ('cycles_count', models.IntegerField(default=0, verbose_name='Suma cykli')),
                ('use_cycles', models.BooleanField(default=False, verbose_name='Używaj cykli')),
                ('tth', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Stan licznika na SP')),
                ('last_pdt_ref', models.IntegerField(default=0, verbose_name='Ostatni numer PDT')),
                ('fuel_type', models.CharField(choices=[('AVGAS', 'Avgas 100LL'), ('MOGAS', 'Benzyna samochodowa'), ('JETA1', 'Paliwo JET A-1')], max_length=5, verbose_name='Rodzaj paliwa')),
                ('fuel_capacity', models.DecimalField(decimal_places=1, default=0, max_digits=4, verbose_name='Zbiornik paliwa (L)')),
                ('fuel_consumption', models.DecimalField(decimal_places=1, default=0, max_digits=4, verbose_name='Zużycie paliwa (L/h)')),
                ('fuel_volume', models.DecimalField(decimal_places=1, default=0, max_digits=4, verbose_name='Szacowana ilość paliwa (L)')),
                ('rent_price', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Cena wynajmu (PLN/h)')),
                ('ms_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='MS do TTH')),
                ('ms_date', models.DateField(blank=True, null=True, verbose_name='MS do daty')),
                ('ms_landings', models.IntegerField(blank=True, null=True, verbose_name='MS do lądowań')),
                ('ms_cycles', models.IntegerField(blank=True, null=True, verbose_name='MS do cykli')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Uwagi')),
                ('scheduled', models.BooleanField(default=True, verbose_name='Podlega rezerwacjom')),
                ('info', models.TextField(blank=True, null=True, verbose_name='Informacje dla pilotów')),
                ('color', models.CharField(default='#ccffcc', max_length=7, verbose_name='Kolor wyświetlania')),
            ],
        ),
        migrations.CreateModel(
            name='ASO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('certificate', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Organizacje ASO',
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('crs', models.CharField(blank=True, max_length=200, null=True)),
                ('from_date', models.DateField()),
                ('from_hours', models.DecimalField(decimal_places=2, max_digits=7)),
                ('from_landings', models.IntegerField(default=0)),
                ('from_cycles', models.IntegerField(default=0)),
                ('to_date', models.DateField(blank=True, null=True)),
                ('to_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('to_landings', models.IntegerField(blank=True, null=True)),
                ('to_cycles', models.IntegerField(blank=True, null=True)),
                ('current', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ATA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter', models.CharField(max_length=5, verbose_name='Rozdział')),
                ('chapter_title', models.CharField(max_length=100, verbose_name='Tytuł rozdziału')),
                ('section', models.CharField(max_length=10, verbose_name='Sekcja')),
                ('section_title', models.CharField(max_length=100, verbose_name='Tytuł sekcji')),
                ('description', models.TextField(verbose_name='Opis')),
            ],
            options={
                'verbose_name_plural': 'Sekcje ATA',
            },
        ),
        migrations.CreateModel(
            name='CAMO_operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdt_ref', models.CharField(blank=True, max_length=20, null=True, verbose_name='Numer PDT')),
                ('date', models.DateField(verbose_name='Data operacji')),
                ('tth_start', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Licznik początkowy')),
                ('tth_end', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Licznik końcowy')),
                ('landings', models.IntegerField(default=0, verbose_name='Liczba lądowań')),
                ('cycles', models.IntegerField(default=0, verbose_name='Liczba cykli')),
                ('remarks', models.CharField(blank=True, max_length=350, null=True, verbose_name='Uwagi')),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Aircraft')),
            ],
        ),
        migrations.CreateModel(
            name='Modification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200, verbose_name='Opis')),
                ('done_date', models.DateField(verbose_name='Data wykonania')),
                ('done_hours', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='TTH wykonania')),
                ('done_landings', models.IntegerField(blank=True, null=True, verbose_name='Lądowania wykonania')),
                ('done_cycles', models.IntegerField(blank=True, null=True, verbose_name='Cykle wykonania')),
                ('aso', models.CharField(max_length=100, verbose_name='Organizacja')),
                ('done_crs', models.CharField(max_length=20, verbose_name='Numer CRS')),
                ('remarks', models.CharField(blank=True, max_length=500, null=True, verbose_name='Uwagi')),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Aircraft', verbose_name='Statek powietrzny')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.BooleanField()),
            ],
            options={
                'permissions': [('camo_reader', 'CAMO - Dostęp do odczytu'), ('camo_admin', 'CAMO - Dostęp pełny')],
            },
        ),
        migrations.CreateModel(
            name='MS_report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ms_ref', models.CharField(max_length=20, verbose_name='Numer MS')),
                ('fuselage', models.CharField(max_length=30, verbose_name='Numer płatowca')),
                ('engine1', models.CharField(max_length=30, verbose_name='Numer silnika L')),
                ('engine2', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numer silnika R')),
                ('done_date', models.DateField(verbose_name='Data MS')),
                ('done_hours', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Liczba godzin')),
                ('done_landings', models.IntegerField(default=0, verbose_name='Liczba lądowań')),
                ('done_cycles', models.IntegerField(default=0, verbose_name='Liczba cykli')),
                ('crs_ref', models.CharField(blank=True, max_length=20, null=True, verbose_name='Numer CRS')),
                ('crs_date', models.CharField(blank=True, max_length=21, null=True, verbose_name='Data CRS')),
                ('next_date', models.DateField(verbose_name='Ważne do daty')),
                ('next_hours', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Ważne do nalotu')),
                ('next_landings', models.IntegerField(blank=True, null=True, verbose_name='Ważne do liczby lądowań')),
                ('next_cycles', models.IntegerField(blank=True, null=True, verbose_name='Ważne do liczby cykli')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Uwagi')),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Aircraft', verbose_name='Statek powietrzny')),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maker', models.CharField(max_length=100, verbose_name='Producent')),
                ('part_no', models.CharField(max_length=35, verbose_name='Numer części (typ)')),
                ('serial_no', models.CharField(max_length=35, verbose_name='Numer seryjny')),
                ('name', models.CharField(max_length=200, verbose_name='Nazwa')),
                ('f1', models.CharField(blank=True, max_length=50, null=True, verbose_name='FORM-1')),
                ('lifecycle', models.CharField(choices=[('llp', 'Ograniczona żywotność (LLP)'), ('ovh', 'Podlegająca remontowi (OVH)'), ('oth', 'Według stanu')], default='oth', max_length=10, verbose_name='Cykl życia')),
                ('production_date', models.DateField(blank=True, null=True, verbose_name='Data produkcji')),
                ('install_date', models.DateField(blank=True, null=True, verbose_name='Data pierwszej instalacji')),
                ('hours_count', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Suma TTH')),
                ('landings_count', models.IntegerField(default=0, verbose_name='Suma lądowań')),
                ('cycles_count', models.IntegerField(default=0, verbose_name='Suma cykli')),
            ],
        ),
        migrations.CreateModel(
            name='POT_event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('POT_ref', models.CharField(max_length=100, verbose_name='POT Ref.')),
                ('name', models.TextField(verbose_name='Nazwa czynności')),
                ('done_crs', models.CharField(blank=True, max_length=20, null=True, verbose_name='Wykonano (CRS Ref.)')),
                ('done_date', models.DateField(blank=True, null=True, verbose_name='Wykonano (data)')),
                ('done_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Wykonano (TTH)')),
                ('done_landings', models.IntegerField(blank=True, null=True, verbose_name='Wykonano (lądowania)')),
                ('done_cycles', models.IntegerField(blank=True, null=True, verbose_name='Wykonano (cykle)')),
            ],
        ),
        migrations.CreateModel(
            name='POT_group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('POT_ref', models.CharField(max_length=100, verbose_name='POT ref.')),
                ('adsb_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='Numer AD/SB')),
                ('adsb_date', models.DateField(blank=True, null=True, verbose_name='Data AD/SB')),
                ('adsb_agency', models.CharField(blank=True, max_length=20, null=True, verbose_name='Organ wydający')),
                ('adsb_related', models.CharField(blank=True, max_length=50, null=True, verbose_name='Powiązanie AD/SB')),
                ('name', models.CharField(max_length=500, verbose_name='Opis')),
                ('type', models.CharField(choices=[('oth', 'Obsługa techniczna'), ('llp', 'Planowy demontaż'), ('ovh', 'Planowy remont'), ('ad', 'AD - Dyrektywa'), ('sb', 'SB - Biuletyn')], default='oth', max_length=10, verbose_name='Rodzaj czynności')),
                ('due_hours', models.IntegerField(blank=True, null=True, verbose_name='Limit TTH')),
                ('due_months', models.IntegerField(blank=True, null=True, verbose_name='Limit miesięcy')),
                ('due_landings', models.IntegerField(blank=True, null=True, verbose_name='Limit lądowań')),
                ('due_cycles', models.IntegerField(blank=True, null=True, verbose_name='Limit cykli')),
                ('cyclic', models.BooleanField(default=True, verbose_name='Czynność cykliczna')),
                ('parked', models.BooleanField(default=False, verbose_name='Czynność postojowa')),
                ('count_type', models.CharField(choices=[('production', 'Od produkcji/remontu'), ('install', 'Od instalacji')], default='production', max_length=10, verbose_name='Sposób liczenia')),
                ('applies', models.BooleanField(default=True, verbose_name='Dotyczy danej części')),
                ('optional', models.BooleanField(default=False, verbose_name='Czynność opcjonalna')),
                ('done_crs', models.CharField(blank=True, max_length=20, null=True, verbose_name='Wykonano (CRS Ref.)')),
                ('done_date', models.DateField(blank=True, null=True, verbose_name='Wykonano (data)')),
                ('done_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Wykonano (TTH)')),
                ('done_landings', models.IntegerField(blank=True, null=True, verbose_name='Wykonano (lądowania)')),
                ('done_cycles', models.IntegerField(blank=True, null=True, verbose_name='Wykonano (cykle)')),
                ('done_aso', models.CharField(blank=True, max_length=100, null=True, verbose_name='Wykonano (ASO)')),
                ('remarks', models.CharField(blank=True, max_length=500, null=True, verbose_name='Uwagi')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Part', verbose_name='Powiązana część')),
            ],
        ),
        migrations.CreateModel(
            name='WB_report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200, verbose_name='Opis')),
                ('doc_ref', models.CharField(blank=True, max_length=20, null=True, verbose_name='Numer dokumentu')),
                ('unit', models.CharField(choices=[('EU', 'EU'), ('USA', 'USA')], default='EU', max_length=3, verbose_name='Jednostki')),
                ('mass_change', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Zmiana masy')),
                ('empty_weight', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Masa pustego')),
                ('lon_cg', models.DecimalField(blank=True, decimal_places=3, max_digits=9, null=True, verbose_name='Longitudal C.G.')),
                ('lat_cg', models.DecimalField(blank=True, decimal_places=3, max_digits=9, null=True, verbose_name='Lateral C.G.')),
                ('done_date', models.DateField(verbose_name='Data wykonania')),
                ('done_hours', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='TTH wykonania')),
                ('done_landings', models.IntegerField(blank=True, null=True, verbose_name='Lądowania wykonania')),
                ('done_cycles', models.IntegerField(blank=True, null=True, verbose_name='Cykle wykonania')),
                ('aso', models.CharField(max_length=100, verbose_name='Organizacja')),
                ('done_doc', models.CharField(blank=True, max_length=20, null=True, verbose_name='Numer CRS')),
                ('remarks', models.CharField(blank=True, max_length=500, null=True, verbose_name='Uwagi')),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Aircraft', verbose_name='Statek powietrzny')),
            ],
        ),
        migrations.CreateModel(
            name='Work_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=25)),
                ('date', models.DateField()),
                ('aso', models.CharField(max_length=100)),
                ('open', models.BooleanField(default=True)),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Aircraft')),
            ],
        ),
        migrations.CreateModel(
            name='Work_order_line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(default=False)),
                ('done_date', models.DateField(blank=True, null=True)),
                ('done_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('done_landings', models.IntegerField(blank=True, null=True)),
                ('done_cycles', models.IntegerField(blank=True, null=True)),
                ('done_crs', models.CharField(blank=True, max_length=20, null=True)),
                ('pot_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.POT_group')),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.Work_order')),
            ],
        ),
        migrations.AddField(
            model_name='pot_event',
            name='POT_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camo.POT_group'),
        ),
    ]
