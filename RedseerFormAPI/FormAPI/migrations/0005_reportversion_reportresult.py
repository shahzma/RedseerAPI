# Generated by Django 4.0.1 on 2022-01-30 19:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('FormAPI', '0004_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FormAPI.report')),
            ],
            options={
                'db_table': 'FormAPI_ReportVersion',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ReportResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.CharField(max_length=20)),
                ('parameter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FormAPI.parameter')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FormAPI.reportversion')),
            ],
            options={
                'db_table': 'FormAPI_ReportResult',
                'managed': True,
            },
        ),
    ]
