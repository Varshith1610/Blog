# Generated by Django 4.2.14 on 2025-01-08 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_blogmedia_media_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='codeblock',
            name='language',
            field=models.CharField(default='', max_length=20),
        ),
    ]
