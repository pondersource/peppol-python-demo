# Generated by Django 3.2.3 on 2021-06-07 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('website', models.URLField()),
                ('first_name', models.CharField(max_length=140)),
                ('last_name', models.CharField(max_length=50)),
            ],
        ),
    ]
