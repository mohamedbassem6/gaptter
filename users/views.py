from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import (
    RegisterAuthForm,
    RegisterProfileForm,
    UserUpdateForm,
    ProfileUpdateForm,
)
from .models import FollowLog
from django.contrib.auth.models import User
from formtools.wizard.views import SessionWizardView
from django.http import JsonResponse
from itertools import chain
from datetime import datetime


class RegisterWizard(SessionWizardView):
    form_list = [RegisterAuthForm, RegisterProfileForm]


def register(request):
    if request.user.is_authenticated:
        return redirect("profile")
    else:
        if request.method == "POST":
            form = RegisterAuthForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get("username")
                messages.success(request, f"Hello, {username}")
                return redirect("login")

        else:
            form = RegisterAuthForm()

        return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    user = request.user
    context = dict()

    if user.profile.favourites.exists():
        context["favourites"] = user.profile.favourites.all()
    else:
        context["favourites"] = None

    if user.log_set.exists():
        context["logs"] = user.log_set.all().order_by("-date", "-time")[:5]
        context["logs_count"] = user.log_set.count()
        context["films_count"] = user.log_set.values("film").distinct().count()

        context["chronicle"] = dict()

        for log in context["logs"]:
            if context["chronicle"].get(log.date):
                context["chronicle"][log.date].append(log)
            else:
                context["chronicle"][log.date] = [log]
    else:
        context["logs"] = None
        context["chronicle"] = None
        context["logs_count"] = 0
        context["films_count"] = 0

    if user.list_set.exists():
        context["lists"] = user.list_set.all()
    else:
        context["lists"] = None

    if user.gapt_set.exists() or user.regaptlog_set.exists():
        gapts = user.gapt_set.all()
        reGapts = user.regaptlog_set.all()

        context["gapts_count"] = gapts.count() + reGapts.count()

        timeline_data = []

        for gapt in gapts:
            data = {
                "type": 1,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                "gapt": gapt,
                "liked": gapt.isLikedBy(user),
                "reGapted": gapt.isReGaptdBy(user),
            }
            timeline_data.append(data)

        for reGapt in reGapts:
            data = {
                "type": 0,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                "gapt": reGapt.gapt,
                "reGaptLog": reGapt,
                "reGapter": reGapt.user,
                "liked": reGapt.gapt.isLikedBy(user),
                "reGapted": reGapt.gapt.isReGaptdBy(user),
            }
            timeline_data.append(data)

        context["gapts_activity"] = sorted(
            timeline_data,

            key=lambda instance: instance["gapt"].date
            if instance["type"] == 1
            else instance["reGaptLog"].date,

            reverse=True,
        )
    else:
        context["gapts_activity"] = None
        context["gapts_count"] = 0

    return render(request, "users/profile.html", context)


@login_required
def profileSettings(request):
    if request.method == "POST":
        userUpdateForm = UserUpdateForm(request.POST, instance=request.user)
        profileUpdateForm = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if userUpdateForm.is_valid() and profileUpdateForm.is_valid():
            userUpdateForm.save()
            profileUpdateForm.save()
            messages.success(request, "Changes saved successfully.")
            return redirect("/profile")

    else:
        userUpdateForm = UserUpdateForm(instance=request.user)
        profileUpdateForm = ProfileUpdateForm(instance=request.user.profile)

    user_id = request.user.id

    context = {
        "userUpdateForm": userUpdateForm,
        "profileUpdateForm": profileUpdateForm,
        "user": User.objects.get(
            id=user_id
        ),  # To fix the problem with username changing automatically regardless of its validity
    }

    return render(request, "users/profile_settings.html", context)


def user(request, username):
    if request.user.is_authenticated and request.user.username == username:
        return redirect("/profile/")

    querySet = User.objects.filter(username=username)
    context = dict()

    if querySet.exists():
        target_user = querySet.first()
        context["target_user"] = target_user

        if target_user.profile.favourites.exists():
            context["favourites"] = target_user.profile.favourites.all()
        else:
            context["favourites"] = None

        if target_user.log_set.exists():
            context["logs"] = target_user.log_set.all().order_by("-date")[:5]
            context["logs_count"] = target_user.log_set.count()
            context["films_count"] = target_user.log_set.values_list("film", flat=True).distinct().count()

            print(target_user.log_set.values_list("film", flat=True).distinct().count())

            context["chronicle"] = dict()

            for log in context["logs"]:
                if context["chronicle"].get(log.date):
                    context["chronicle"][log.date].append(log)
                else:
                    context["chronicle"][log.date] = [log]
        else:
            context["logs"] = None
            context["logs_count"] = 0
            context["films_count"] = 0
            context["chronicle"] = None

        if target_user.list_set.exists():
            context["lists"] = target_user.list_set.all()
        else:
            context["lists"] = None

        if target_user.gapt_set.exists() or target_user.regaptlog_set.exists():
            gapts = target_user.gapt_set.all()
            reGapts = target_user.regaptlog_set.all()
            context["gapts_count"] = gapts.count() + reGapts.count()

            timeline_data = []

            for gapt in gapts:
                data = {
                    "type": 1,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                    "gapt": gapt,
                    "liked": gapt.isLikedBy(request.user) if request.user.is_authenticated else False,
                    "reGapted": gapt.isReGaptdBy(request.user) if request.user.is_authenticated else False,
                }
                timeline_data.append(data)

            for reGapt in reGapts:
                data = {
                    "type": 0,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                    "gapt": reGapt.gapt,
                    "reGaptLog": reGapt,
                    "reGapter": reGapt.user,
                    "liked": reGapt.gapt.isLikedBy(request.user) if request.user.is_authenticated else False,
                    "reGapted": reGapt.gapt.isReGaptdBy(request.user) if request.user.is_authenticated else False,
                }
                timeline_data.append(data)

            context["gapts_activity"] = sorted(
                timeline_data,

                key=lambda instance: instance["gapt"].date
                if instance["type"] == 1
                else instance["reGaptLog"].date,

                reverse=True,
            )
        else:
            context["gapts"] = None
            context["gapts_count"] = 0

        if request.user.is_authenticated and request.user.profile.doesFollow(target_user):
            context["doesFollow"] = True
        else:
            context["doesFollow"] = False
    else:
        return redirect("/404/")

    return render(request, "users/user.html", context)


def watchlist(request, username):
    if request.user.is_authenticated and username == request.user.username:
        return redirect("profile_watchlist")

    user_query_set = User.objects.filter(username=username)

    if user_query_set.exists():
        context = dict()

        list = user.profile.watchlist
        context["list"] = list

        user = user_query_set.first()

        if user.is_authenticated:
            context["self_watchlist"] = False

            list_count = list.count()
            context["list_count"] = list_count

            watched_count = 0

            for film in list.films.all():
                if user.profile.hasWatched(film):
                    watched_count += 1

            context["watched_count"] = watched_count

            if list_count != 0:
                context["watched_percentage"] = round(
                    (watched_count / list_count) * 100
                )

        return render(request, "core/watchlist.html", context)
    else:
        return redirect("/404/")


@login_required
def profile_watchlist(request):
    list = request.user.profile.watchlist

    return render(
        request, "core/watchlist.html", {"list": list, "self_watchlist": True}
    )


@csrf_exempt
def followUser(request, username):
    if request.method == "POST":
        loggedUser = request.user
        followedUser = User.objects.get(username=username)

        if loggedUser.profile.following.filter(user=followedUser).exists():
            FollowLog.objects.get(
                followee=followedUser.profile, follower=loggedUser.profile
            ).delete()
            return JsonResponse({"status": "unfollowed"})
        else:
            FollowLog.objects.create(
                follower=loggedUser.profile, followee=followedUser.profile
            )
            return JsonResponse({"status": "followed"})
    else:
        redirect("/404/")
