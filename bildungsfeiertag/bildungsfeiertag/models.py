import docupy
from datetime import datetime
from django.db import models
import django.contrib.auth.models
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator

EVENT_DURATIONS = (('30', "kurz (15 + 10 min)"),
                   ('60', "lang (35 + 15 min)"),
                   ('90', "sehr lang (65 + 20 min)"))

EVENT_DEFAULT_DURATION = EVENT_DURATIONS[0]


User = django.contrib.auth.models.User

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
    submit_date = models.DateTimeField()
    title = models.TextField()
    # date = models.DateField()
    description = models.TextField()
    site = models.ForeignKey('Site',
                             on_delete=models.CASCADE)
    speaker = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    duration = models.CharField(max_length=128,
                                choices=EVENT_DURATIONS,
                                default=EVENT_DEFAULT_DURATION)
    active = models.BooleanField()
    accepted = models.BooleanField()
    max_participants = models.IntegerField(validators=[MinValueValidator(5),
                                                       MaxValueValidator(1000)],
                                           default=1000)
    # image = models.CharField(max_length=128)
    type = models.CharField(max_length=128,
                            choices=EVENT_TYPES,
                            default=TALK)
    expenses = MoneyField(max_digits=4,
                          decimal_places=2,
                          default_currency='EUR',
                          default=0,
                          validators=[
                            MinMoneyValidator(0),
                            MaxMoneyValidator(20)])


class ScheduledEvent(models.Model):
    room = models.ForeignKey('Room',
                             on_delete=models.CASCADE)
    time = models.TimeField()
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "\"{}\" by {}".format(self.event.title, str(self.event.speaker))


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
        ScheduledEvent,
        on_delete=models.CASCADE,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

class Registration(models.Model):
    event = models.OneToOneField(
        ScheduledEvent,
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
