import os
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import Site, Room, Event, Vote, MediaFile


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
    if site.roomsdistributed:
        rooms = Room.objects.filter(site=site)
        events = [Event.objects.filter(room=room).order_by("time") for room in rooms]
        return render(request, "site.html", {"site": site,
                                             "rooms_events": list(zip(rooms, events))})
    else:
        rooms = Room.objects.filter(site=site)
        events = [Event.objects.filter(room=room).order_by("time") for room in rooms]
        return render(request, "site.html", {"site": site,
                                             "rooms_events": list(zip(rooms, events))})


def event(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    event = [event for event in events if event.room.site == site]
    return render(request, "event.html", {"event": event, "site": site})


def room(request, site_name, room_name):
    site = get_object_or_404(Site, name=site_name)
    rooms = get_list_or_404(Room, name=room_name)
    room = [room for room in rooms if room.site == site]
    if room:
        room = room[0]
        events = Event.objects.filter(room=room).order_by("time")
        return render(request, "room.html", {"room": room,
                                             "events": events,
                                             "site": site})
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
