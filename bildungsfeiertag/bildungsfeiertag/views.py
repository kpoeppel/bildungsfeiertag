import os
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db import IntegrityError
from .models import Site, Room, Event, Vote, MediaFile
from .models import User, Helper, ScheduledEvent, Interest, Registration
from .models import EVENT_DEFAULT_DURATION
from .forms import ProfileForm, EventForm, UserRegistrationForm
import datetime
from django.contrib import messages
from django_registration.backends.activation.views import RegistrationView

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
    if user.is_authenticated:
        helper = Helper.objects.filter(user=user, site=site)
    else:
        helper = None
    if site.roomsdistributed:
        rooms = Room.objects.filter(site=site)
        scheduled_events = [ScheduledEvent.objects.filter(room=room).order_by("time") for room in rooms]
        print(scheduled_events)
        return render(request, "site.html", {"site": site,
                                             "rooms_events": list(zip(rooms, scheduled_events)),
                                             "user": user,
                                             "helper": helper})
    else:
        events = Event.objects.filter(site=site, active=True).order_by("submit_date")
        return render(request, "site.html", {"site": site,
                                             "events": events,
                                             "user": user,
                                             "helper": helper})


def scheduled_event_view(request, site_name, event_title):
    site = get_object_or_404(Site, name=site_name)
    events = get_list_or_404(Event, title=event_title)
    scheduled_event = [ScheduledEvent.objects.filter(event=event) for event in events if event.site == site]
    user = request.user
    if scheduled_event and scheduled_event[0]:
        scheduled_event = scheduled_event[0][0]
        if request.method == 'POST':
            interest = Interest.objects.filter(user=user, scheduled_event=scheduled_event)
            if interest:
                interest[0].delete()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'You are not interested in '+scheduled_event.title+" anymore.")
            else:
                interest = Interest(user=user, event=event)
                interest.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'You are interested in '+event.title+".")
        if user.is_authenticated:
            interests = len(Interest.objects.filter(scheduled_event=scheduled_event))
            interest = Interest.objects.filter(user=user, scheduled_event=scheduled_event)
        else:
            interests = len(Interest.objects.filter(scheduled_event=scheduled_event))
            interest = None
        return render(request,
                      "scheduled-event.html",
                      {"scheduled_event": scheduled_event,
                       "site": site, "user": user,
                       "interests": interests, "interest": interest})
    else:
        raise Http404("Event does not exist.")


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
        scheduled_events = ScheduledEvent.objects.filter(room=room).order_by("time")
        return render(request, "room.html", {"room": room,
                                             "scheduled_events": scheduled_events,
                                             "site": site,
                                             "user": user})
    else:
        raise Http404("Room does not exist.")

def helper_info_view(request, site_name):
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
    return render(request, "helper-info.html", {"site": site,
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


class register_view(RegistrationView):
    # if this is a POST request we need to process the form data
    template_name = 'django_registration/registration_form.html'
    form_class = UserRegistrationForm

    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = self.form_class(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            self.create_inactive_user(form)
            return HttpResponseRedirect('complete')
        return render(request, self.template_name, {'form': form})

    # if a GET (or any other method) we'll create a blank form
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        # print(form.fields)
        return render(request, self.template_name, {'form': form})



def profile_view(request):
    user = request.user
    # if this is a POST request we need to process the form data
    if user.is_authenticated:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = ProfileForm(data=request.POST, instance=request.user)
            # check whether it's valid:
            print("Hallo")
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #print(form)
            #print(form.errors)
            if form.is_valid():
                newuser = form.save(commit=False)
                print(User.objects.filter(email=newuser.email), user.email)
                if user.email == newuser.email or not User.objects.filter(email=newuser.email):
                    newuser.save()
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         'Email exists.')
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Bad input.')
            return HttpResponseRedirect('')

        # if a GET (or any other method) we'll create a blank form
        else:
            events = Event.objects.filter(speaker=user)
            votes = Vote.objects.filter(user=user)
            events_voted = [vote.event for vote in votes]
            sites_voted = [event.site for event in events_voted]
            form = ProfileForm(instance=request.user)
            sites = [event.site for event in events]
            sites_events = list(zip(sites, events))
            sites_events_voted = list(zip(sites_voted, events_voted))
            return render(request,
                          'profile.html',
                          {'form': form,
                           'sites_events': sites_events,
                           'sites_events_voted': sites_events_voted,
                           'user': request.user})
    else:
        return render(request,
                      'profile.html',
                      {'user': user})
