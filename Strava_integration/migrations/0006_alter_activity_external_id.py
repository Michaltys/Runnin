# Generated by Django 4.2.7 on 2023-11-13 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Strava_integration', '0005_rename_friend_count_athlete_following_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='external_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
