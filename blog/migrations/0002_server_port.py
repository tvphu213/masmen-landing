# Generated by Django 3.2.9 on 2021-11-23 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='port',
            field=models.IntegerField(default=0),
        ),
    ]
