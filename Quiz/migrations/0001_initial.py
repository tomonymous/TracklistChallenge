# Generated by Django 3.1 on 2020-08-19 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255)),
                ('date', models.CharField(max_length=16)),
                ('album_id', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('tracks', models.CharField(max_length=2083)),
                ('image_url', models.CharField(max_length=2083)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('artist_id', models.CharField(max_length=255)),
                ('area', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('image_url', models.CharField(max_length=2083)),
            ],
        ),
    ]