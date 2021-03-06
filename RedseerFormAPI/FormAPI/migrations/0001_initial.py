# Generated by Django 4.0.1 on 2022-03-28 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormapiParameter',
            fields=[
                ('parameter_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_name', models.CharField(blank=True, max_length=80, null=True)),
                ('unit', models.CharField(blank=True, max_length=20, null=True)),
                ('parent_parameter', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'formapi_parameter',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MainData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('date_created', models.DateField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'main_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('parameter_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_name', models.CharField(blank=True, max_length=80, null=True)),
                ('unit', models.CharField(blank=True, max_length=20, null=True)),
                ('parent_parameter', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'parameter',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ParameterTree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=255)),
                ('summate', models.BooleanField(default=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('player_id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('player_name', models.CharField(max_length=45)),
                ('industry_id', models.IntegerField(default=3)),
            ],
            options={
                'db_table': 'player',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('frequency', models.TextField(choices=[(1, 'Weekly'), (2, 'Monthly'), (3, 'Quarterly')])),
                ('cutoff', models.IntegerField(default=15)),
                ('question_count', models.IntegerField(default=24)),
            ],
            options={
                'db_table': 'report',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ReportVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('company', models.CharField(default='testCompany', max_length=255)),
                ('filled_count', models.IntegerField(default=0)),
                ('is_submitted', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'reportversion',
                'managed': False,
            },
        ),
    ]
