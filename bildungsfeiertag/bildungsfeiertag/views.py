import os
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from models import Site, Room, Talk, Vote, MediaFile


def index(request):
    return render(request, "index.html")


def overview(request):
    sites = Site.objects.all()
    return render(request, "overview.html")


def site(request, id):
    site = get_object_or_404(Site, id=id)
    rooms = Room.objects.filter(site=site)
    talks = [Talk.objects.filter(room=room) for room in rooms]
    return render(request, "site.html", {"site": site,
                                         "rooms": rooms,
                                         "talks": talks})


def talk(request, id):
    if request.method == "POST":
        talk = get_object_or_404(Talk, id=id)
    return render(request, "talk.html", {"talk": talk})


def room(request, id):
    room = get_object_or_404(Room, id=id)
    talks = Talk.objects.filter(room=room).order_by("time")
    return render(request, "room.html", {"room": room, "talks": talks})


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
