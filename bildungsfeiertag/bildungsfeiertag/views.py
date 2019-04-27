import os
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import Site, Room, Event, Vote, MediaFile, User, Helper
from .models import EVENT_DEFAULT_DURATION
from django_registration.forms import RegistrationForm
from .forms import ProfileForm, EventForm
import datetime
from django.contrib import messages

def index_view(request):
    sites = Site.objects.all()
    return render(request, "index.html", {"sites": sites})


def about_view(request):
    return render(request, "about.html", {"description": "This is a preliminary description text."})


def overview_view(request):
    sites = Site.objects.all()
    return render(request, "overview.html", {"sites": sites})


def site_view(request, site_name):
    site = get_object_or_404(Site, name=site_name)
    user = request.user
    if site.roomsdistributed:
        rooms = Room.objects.filter(site=site)
        sched_events = [ScheduledEvent.objects.filter(room=room).order_by("time") for room in rooms]
        return render(request, "site.html", {"site": site,
                                             "rooms_events": list(zip(rooms, sched_events)),
                                             "user": user})
    else:
        events = Event.objects.filter(site=site, active=True).order_by("submit_date")
        return render(request, "site.html", {"site": site,
                                             "events": events,
                                             "user": user})


def event_view(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    event = [event for event in events if event.site == site]
    user = request.user
    if event:
        event = event[0]
        if request.method == 'POST':
            vote = Vote.objects.filter(user=user, event=event)
            if vote:
                vote[0].delete()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'You unvoted for '+event.title+".")
            else:
                vote = Vote(user=user, event=event)
                vote.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'You voted for '+event.title+".")
        if user.is_authenticated:
            votes = len(Vote.objects.filter(event=event))
            vote = Vote.objects.filter(user=user, event=event)
        else:
            votes = []
            vote = None
        return render(request, "event.html", {"event": event, "site": site, "user": user, "votes": votes, "vote": vote})
    else:
        raise Http404("Event does not exist.")


def room_view(request, site_name, room_name):
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

def helper_check_view(request, site_name):
    site = get_object_or_404(Site, name=site_name)
    user = request.user
    helper = Helper.objects.filter(user=user, site=site)
    if request.method == 'POST':
        if not helper:
            helper = Helper(site=site, user=user)
            helper.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Thank you for registering as helper for '+site.name+".")
            return HttpResponseRedirect('')
        else:
            helper[0].delete()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'We are sorry that you are not helper for '+site.name+" anymore.")
            return HttpResponseRedirect('')
    return render(request, "helper-check.html", {"site": site,
                                                 "user": user,
                                                 "helper": helper})


def media_view(request):
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


def event_create_view(request, site_name):
    site = get_object_or_404(Site, name=site_name)
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = EventForm(data=request.POST)
            # check whether it's valid:
            if form.is_valid():
                event = form.save(commit=False)
                event.submit_date = datetime.datetime.now()
                event.speaker = user
                event.site = site
                event.accepted = False
                otherevents = Event.objects.filter(title=event.title, site=site)
                if not otherevents:
                    event.save()
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Title already exists.')
                    return HttpResponseRedirect('')
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Changes successfully saved.')
                return HttpResponseRedirect('event/'+event.title)
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Form was badly filled.')
                return HttpResponseRedirect('')
        else:
            form = EventForm(initial={'title': "",
                                      'description': "",
                                      'type': Event.TALK,
                                      'duration': EVENT_DEFAULT_DURATION})
            return render(request, "event-create.html", {"form": form,
                                                         "site": site,
                                                         "user": request.user,
                                                         "create": True})
    else:
        return render(request, "event-create.html", {"site": site,
                                                     "user": request.user,
                                                     "create": True})


def event_delete_view(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    event = [event for event in events if event.site == site]
    user = request.user

    if event and user:
        event = event[0]
        if event.speaker == user:
            event.delete()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your event was deleted.')
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Your must not delete others events.')
    return render(request, "event-delete.html", {"site": site, "user": user})


def event_change_view(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    event = [event for event in events if event.site == site]
    user = request.user

    if event:
        event = event[0]
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = EventForm(request.POST)
            # check whether it's valid:
            print("NO", form.errors)
            if form.is_valid():
                print("Yes")
                data = form.cleaned_data
                newevent = form.save(commit=False)
                newevent.submit_date = datetime.datetime.now()
                newevent.speaker = user
                newevent.site = site
                newevent.accepted = False
                otherevents = Event.objects.filter(title=newevent.title, site=site)
                if not otherevents or otherevents[0].title == event.title:
                    newevent.save()
                    event.delete()
                    event = newevent
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         'Changes successfully saved.')
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Title already exists.')
                    return HttpResponseRedirect('')
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                return HttpResponseRedirect("../event/"+event.title)
            messages.add_message(request,
                                 messages.ERROR,
                                 'Form was badly filled.')
            return HttpResponseRedirect('')
        # if a GET (or any other method) we'll create a blank form
        else:
            print("HI")
            form = EventForm(instance=event)
            print("BYE", form)
        return render(request, "event-create.html", {"event": event,
                                                     "form": form,
                                                     "site": site,
                                                     "user": user,
                                                     "create": False})
    else:
        raise Http404("Room does not exist.")

def register_view(request):
    # if this is a POST request we need to process the form data
    print("Hello")
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegistrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print("Hello")
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('complete')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegistrationForm()
        print(form.fields)
    return render(request,
                  'django_registration/registration_form.html',
                  {'form': form})



def profile_view(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if user.is_authenticated:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = ProfileForm(data=request.POST)
            # check whether it's valid:

            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                newuser = form.save(commit=False)
                otherusers = User.objects.filter(username=newuser.name)
                if not otherusers or newuser.username == user.username:
                    user.username = newuser.username
                    user.first_name = newuser.first_name
                    user.last_name = newuser.last_name
                    user.email = newuser.email
                    user.save()
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         'Changes successfully saved.')
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Username exists.')
            return HttpResponseRedirect('')

        # if a GET (or any other method) we'll create a blank form
        else:
            events = Event.objects.filter(speaker=user)
            form = ProfileForm(instance=request.user)
            sites = [event.site for event in events]
            sites_events = list(zip(sites, events))
            return render(request,
                          'profile.html',
                          {'form': form,
                           'sites_events': sites_events,
                           'user': request.user})
    else:
        return render(request,
                      'profile.html',
                      {'user': user})
