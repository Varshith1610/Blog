# Generated by Django 4.2.14 on 2024-12-14 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_blog_last_date_alter_blog_published_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='istemp',
            field=models.BooleanField(default=False),
        ),
    ]
