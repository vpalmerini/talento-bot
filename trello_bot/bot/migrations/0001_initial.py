# Generated by Django 2.1.2 on 2018-12-20 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('card_id', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('FN', 'Financial'), ('CS', 'Consulting'), ('ID', 'Industry')], max_length=2)),
                ('status', models.CharField(blank=True, choices=[('CT', 'Contacted'), ('IT', 'Interested'), ('DC', 'Declined'), ('CL', 'Closed'), ('SG', 'Signed'), ('PD', 'Paid')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Hunter',
            fields=[
                ('email', models.EmailField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('list_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='hunter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.Hunter'),
        ),
    ]
