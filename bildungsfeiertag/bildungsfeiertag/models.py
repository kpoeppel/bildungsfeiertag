import docupy
from datetime import datetime
from django.db import models
import bildungsfeiertag.settings as settings


class Site(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    image = models.CharField(max_length=128)

    def __str__(self):
        return "{}".format(name)

class Room(models.Model):
    site = models.ForeignKey('Site',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()

    def __str__(self):
        return "Room {}".format(self.name)


class Talk(models.Model):
    title = models.TextField()
    date = models.DateField()
    description = models.TextField()
    room = models.ForeignKey('Room',
                             on_delete=models.CASCADE)
    speaker = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    duration = models.DurationField()
    time = models.TimeField()
    accepted = models.BooleanField()
    image = models.CharField(max_length=128)

    def __str__(self):
        return "\"{}\" by {}".format(self.title, self.speaker.name)


class Vote(models.Model):
    talk = models.OneToOneField(
        Talk,
        on_delete=models.CASCADE,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class MediaFile(models.Model):
    def create_filename(instance, filename):
        extension = "." + filename.split(".")[-1] if "." in filename else ""
        return datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S") + extension

    def media_lookup():
        return {
         media.name: media.mediafile.url for media in MediaFile.objects.all()
        }

    name = models.TextField(primary_key=True)
    mediafile = models.FileField(upload_to=create_filename)

    def __str__(self):
        return "MediaFile ({})".format(self.name)
