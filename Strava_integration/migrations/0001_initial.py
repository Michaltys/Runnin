# Generated by Django 2.1 on 2023-09-28 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh_token', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('expires_at', models.IntegerField()),
                ('athlete_id', models.IntegerField(unique=True)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=20)),
                ('sex', models.CharField(max_length=10)),
            ],
        ),
    ]
