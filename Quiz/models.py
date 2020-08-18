from django.db import models

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    date = models.CharField(max_length=16)
    album_id = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    tracks = models.CharField(max_length=2083)
    image_url = models.CharField(max_length=2083)


class Artist(models.Model):
    name = models.CharField(max_length=255)
    artist_id = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    image_url = models.CharField(max_length=2083)
