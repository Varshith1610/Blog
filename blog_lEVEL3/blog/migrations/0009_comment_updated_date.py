# Generated by Django 4.2.14 on 2024-12-20 13:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_comment_super_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='updated_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
