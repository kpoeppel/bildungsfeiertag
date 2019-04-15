import docupy
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField


class Site(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    # image = models.CharField(max_length=128)
    callforeventsclosed = models.BooleanField()
    roomsdistributed = models.BooleanField()
    organizer = models.ForeignKey(User,
                                  on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.name)


class Room(models.Model):
    site = models.ForeignKey('Site',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()

    def __str__(self):
        return "Room {}".format(self.name)


class Event(models.Model):
    TALK = 'Talk'
    WORKSHOP = 'Workshop'
    EXCURSION = 'Excursion'
    DISCUSSION = 'Discussion'
    EVENT_TYPES = ((TALK, 'Vortrag'),
                   (WORKSHOP, 'Workshop'),
                   (EXCURSION, 'Exkusion'),
                   (DISCUSSION, 'Diskussion'))
    title = models.TextField()
    date = models.DateField()
    description = models.TextField()
    room = models.ForeignKey('Room',
                             on_delete=models.CASCADE)
    site = models.ForeignKey('Site',
                             on_delete=models.CASCADE)
    speaker = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    duration = models.DurationField()
    time = models.TimeField()
    active = models.BooleanField()
    accepted = models.BooleanField()
    scheduled = models.BooleanField()
    max_participants = models.PositiveIntegerField()
    # image = models.CharField(max_length=128)
    type = models.CharField(max_length=128,
                            choices=EVENT_TYPES,
                            default=TALK)
    expenses = MoneyField(max_digits=4, decimal_places=2, default_currency='USD')


    def __str__(self):
        return "\"{}\" by {}".format(self.title, str(self.speaker))


class Vote(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

class Interest(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

class Registration(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
    )
    user = models.OneToOneField(
        User,
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
