from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _

EVENT_DURATIONS = (('30', _("short") + " (15 + 10 min)"),
                   ('60', _("long") + " (35 + 15 min)"),
                   ('90', _("very long") + " (65 + 20 min)"))

EVENT_DEFAULT_DURATION = EVENT_DURATIONS[0]


class User(AbstractUser):
    # add additional fields in here
    phone_number = PhoneNumberField(blank=True)
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Site(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    # image = models.CharField(max_length=128)
    callforeventsclosed = models.BooleanField()
    votingclosed = models.BooleanField()
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
    EVENT_TYPES = ((TALK,  _("Talk")),
                   (WORKSHOP, _("Workshop")),
                   (EXCURSION, _("Excursion")),
                   (DISCUSSION, _("Discussion")))
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
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE)
    time = models.DateTimeField()
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "\"{}\" by {}".format(self.event.title, str(self.event.speaker))


class Vote(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

class Interest(models.Model):
    scheduled_event = models.ForeignKey(
        ScheduledEvent,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

class Registration(models.Model):
    scheduled_event = models.ForeignKey(
        ScheduledEvent,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class Helper(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
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
