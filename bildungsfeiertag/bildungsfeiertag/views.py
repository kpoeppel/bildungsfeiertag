import os
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import Site, Room, Event, Vote, MediaFile
from django_registration.forms import RegistrationForm
from .forms import ProfileForm, EventForm

def index(request):
    sites = Site.objects.all()
    return render(request, "index.html", {"sites": sites})


def about(request):
    return render(request, "about.html", {"description": "This is a preliminary description text."})


def overview(request):
    sites = Site.objects.all()
    return render(request, "overview.html", {"sites": sites})


def site(request, site_name):
    site = get_object_or_404(Site, name=site_name)
    user = request.user
    if site.roomsdistributed:
        rooms = Room.objects.filter(site=site)
        sched_events = [ScheduledEvent.objects.filter(room=room).order_by("time") for room in rooms]
        return render(request, "site.html", {"site": site,
                                             "rooms_events": list(zip(rooms, sched_events)),
                                             "user": user})
    else:
        events = Event.objects.filter(site=site).order_by("submit_date")
        return render(request, "site.html", {"site": site,
                                             "events": events,
                                             "user": user})


def event(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    event = [event for event in events if event.site == site]
    user = request.user
    return render(request, "event.html", {"event": event, "site": site, "user": user})


def room(request, site_name, room_name):
    site = get_object_or_404(Site, name=site_name)
    rooms = get_list_or_404(Room, name=room_name)
    room = [room for room in rooms if room.site == site]
    user = request.user
    if room:
        room = room[0]
        events = Event.objects.filter(room=room).order_by("time")
        return render(request, "room.html", {"room": room,
                                             "events": events,
                                             "site": site,
                                             "user": user})
    else:
        raise Http404("Room does not exist.")

def media(request):
    if request.method == "POST":
        if "delete" in request.POST:
            media = MediaFile.objects.get(name=request.POST["name"])
            try:
                os.remove(media.mediafile.path)
            except FileNotFoundError: pass
            media.delete()
            return redirect("/media/")
        try:
            MediaFile.objects.create(
             name=request.POST["name"], mediafile=request.FILES["file"]
            )
        except IntegrityError:
            return render(request, "media.html", {
             "error": "There is already media with that name",
             "media": MediaFile.objects.all()
            })
        return redirect("/media/")
    return render(request, "media.html", {
     "media": MediaFile.objects.all()
})


def register(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegistrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print("Hello")
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('accounts/register/complete')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegistrationForm()
    return render(request,
                  'registration/registration_form.html',
                  {'form': form})


def profile(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProfileForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('accounts/profile')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProfileForm()
    return render(request,
                  'profile.html',
                  {'form': form})
