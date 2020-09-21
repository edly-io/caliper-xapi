# Generated by Django 2.2.16 on 2020-09-21 11:22

from django.db import migrations
import edx_analytics_transformers.utils.fields
import jsonfield.encoder


class Migration(migrations.Migration):

    dependencies = [
        ('edx_analytics_transformers_django', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routerconfiguration',
            name='configurations',
            field=edx_analytics_transformers.utils.fields.EncryptedJSONField(dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}),
        ),
    ]
