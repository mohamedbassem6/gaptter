from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import F, Q, Count
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timezone
from .forms import LogForm, NewListForm
from .models import *
from users.models import Profile
from filmOfTheWeek.models import FilmOfTheWeek
import requests
import math
import json
import threading

from .GaptRank import rank

api_key = settings.TMDB_API_KEY


def home(request):
    if request.user.is_authenticated:
        user = request.user

        followings_id = user.profile.following.values_list('user', flat=True)

        # seen_gapts = SeenGapt.objects.filter(user=user).values_list('gapt', flat=True)

        gapts = Gapt.objects.filter(Q(user__id__in=followings_id) | Q(user=user)).order_by('-date')
        reGapts = ReGaptLog.objects.filter(user__id__in=followings_id).order_by('-date')

        timeline_data = []

        for gapt in gapts:
            data = {
                'type': 1,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                'gapt': gapt,
                'liked': gapt.isLikedBy(user),
                'reGapted': gapt.isReGaptdBy(user),
            }
            timeline_data.append(data)

        for reGapt in reGapts:
            data = {
                'type': 0,  # 1 resembles a Gapt, and 0 resembles a reGapt (as the book 'Zero to One')
                'gapt': reGapt.gapt,
                "reGaptLog": reGapt,
                'reGapter': reGapt.user,
                'liked': reGapt.gapt.isLikedBy(user),
                'reGapted': reGapt.gapt.isReGaptdBy(user),
            }
            timeline_data.append(data)

        timeline_data = sorted(timeline_data, key=lambda instance: rank(instance, user), reverse=True)

        current_date = timezone.now()
        try:
            film_of_the_week = FilmOfTheWeek.objects.get(start_date__lte=current_date, end_date__gte=current_date)
        except FilmOfTheWeek.DoesNotExist:
            film_of_the_week = None
        
        context = {
            'gapts_activity': timeline_data,
            'film_of_the_week': film_of_the_week,
        }
        return render(request, "core/home-logged.html", context)
    else:
        return render(request, "core/home.html")
    

@login_required
@csrf_protect
def markGaptAsSeen(request):
    if request.method == 'POST':
        user = request.user

        gapt_id = request.POST['gapt_id']
        gapt = Gapt.objects.get(id=gapt_id)

        SeenGapt.objects.get_or_create(user=user, gapt=gapt)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})



def NotFound404(request):
    return render(request, "core/404.html")


def runtimeFormat(runtime):
    totalMinutes = int(runtime)

    hours = math.floor(totalMinutes / 60)
    minutes = totalMinutes - (hours * 60)

    if hours == 0 and minutes == 0:
        response = ""
    elif hours == 0:
        response = str(minutes) + "m"
    elif minutes == 0:
        response = str(hours) + "h"
    else:
        response = str(hours) + "h " + str(minutes) + "m"

    return response


def create_film_instance(film_id):
    Film.objects.create(tmdb_id=film_id)


def movie(request, movie_id):
    movie = dict()
    movie["id"] = movie_id

    # Get a QuerySet to validate the film existence in database
    querySet = Film.objects.filter(tmdb_id=movie_id)

    # A flag indicating whether a thread has already been created and currently running in the background, to save the film instance in the database
    has_ongoing_thread = False

    for thread in threading.enumerate():
        if thread.getName() == str(movie_id):
            has_ongoing_thread = True
            break

    # If film not in database, or already has an instance that is getting created in the background
    if not querySet.exists() or has_ongoing_thread:
        detailsResponse = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(movie_id)
            + "?api_key="
            + api_key
        ).json()

        if detailsResponse["adult"] == True:
            return redirect("/404/")

        creditsResponse = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(movie_id)
            + "/credits?api_key="
            + api_key
        ).json()

        for person in creditsResponse['cast']:
            person['tmdb_id'] = person.pop('id')

        directors = []
        for person in creditsResponse['crew']:
            if person["job"] == "Director":
                person['tmdb_id'] = person.pop('id')
                directors.append(person)

        if not has_ongoing_thread:
            thread = threading.Thread(
                target=create_film_instance,
                args=[movie_id],
                name=str(movie_id),
                daemon=False,
            )
            thread.start()  # Create a thread that will make an instance of the film in the database

        # Dsiplay the film using TMDB API directly, while the film instance is getting created in the background

        backdrops = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(movie_id)
            + "/images?include_image_language=null&api_key="
            + api_key
        ).json()["backdrops"]

        if backdrops:
            backdrop_file_path = max(
                backdrops, key=lambda x: x["vote_average"] * x["vote_count"]
            )["file_path"]
        else:
            backdrop_file_path = ""

        movie["title"] = detailsResponse["title"]
        movie["overview"] = detailsResponse["overview"]
        movie["backdrop"] = backdrop_file_path
        movie["poster"] = detailsResponse["poster_path"]
        movie["runtime"] = runtimeFormat(detailsResponse["runtime"])
        movie["genres"] = [genre["name"] for genre in detailsResponse["genres"]]
        movie["year"] = datetime.strptime(
            detailsResponse["release_date"], "%Y-%m-%d"
        ).year
        movie["cast"] = creditsResponse["cast"]
        movie["directors"] = directors

    else:
        film_in_database = querySet.first()

        # if (date.today() - film_in_database.last_updated).days > 3:
        #     film_in_database.update()

        # Handle backdrops
        if film_in_database.custom_backdrop_path != "":
            backdrop_file_path = film_in_database.custom_backdrop_path
        elif film_in_database.backdrop_path != "":
            backdrop_file_path = film_in_database.backdrop_path
        else:
            backdrop_file_path = ""

        # Handle posters
        if film_in_database.custom_poster_path != "":
            poster_file_path = film_in_database.custom_poster_path
        elif film_in_database.poster_path != "":
            poster_file_path = film_in_database.poster_path
        else:
            poster_file_path = ""

        movie["title"] = film_in_database.title
        movie["overview"] = film_in_database.overview
        movie["backdrop"] = backdrop_file_path
        movie["poster"] = poster_file_path
        movie["runtime"] = runtimeFormat(film_in_database.runtime)
        movie["genres"] = film_in_database.genres.all()
        movie["year"] = film_in_database.release_date.year

        movie["cast"] = film_in_database.careeractivity_set.filter(
                                department="Acting"
                            ).values(
                                tmdb_id=F("person__tmdb_id"),
                                name=F("person__name"),
                                character=F("role"),
                            )
        
        movie["directors"] = film_in_database.careeractivity_set.filter(
                                    role="Director", department="Directing"
                                ).values(tmdb_id=F("person__tmdb_id"), name=F("person__name"))
        

    # Handle favourite movies
    user = request.user
    if user.is_authenticated:
        if user.profile.favourites.filter(tmdb_id=movie_id).exists():
            is_favourite = True
        else:
            is_favourite = False
    else:
        is_favourite = False

    # Handle friends who also watched this movie
    watched_by = []
    if user.is_authenticated:
        for person in user.profile.following.all():
            if person.user.log_set.filter(film__tmdb_id=movie_id).exists():
                watched_by.append(person.user)

    log_form = LogForm()

    # Handle related gapts
    gapts = []

    if querySet.exists():
        gapts = querySet.first().gapt_set.all().annotate(likes_count=Count('likes')).order_by('-likes_count')[:50]

        if user.is_authenticated:
            for gapt in gapts:
                liked = gapt.isLikedBy(user)
                reGaptd = gapt.isReGaptdBy(user)
                gapt = gapt.__dict__
                gapt['liked'] = liked
                gapt['reGaptd'] = reGaptd
                

    # A list of tuples
    user_lists = []
    if user.is_authenticated:
        for list in user.list_set.all():
            t = (list, list.has_film_id(movie_id))
            user_lists.append(t)

    context = {
        "movie": movie,
        "watched_by": watched_by,
        "is_favourite": is_favourite,
        "gapts": gapts,
        "log_form": log_form,
        "user_lists": user_lists,
    }

    return render(request, "core/movie.html", context)


def dateFormat(date):
    if not date:
        return

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    parameters = date.split("-")
    response = (
        months[int(parameters[1]) - 1]
        + " "
        + str(int(parameters[2]))
        + ", "
        + parameters[0]
    )

    return response


def person(request, person_id):
    # Get the details of the person using TMDB API
    detailsResponse = requests.get(
        "https://api.themoviedb.org/3/person/" + person_id + "?api_key=" + api_key
    ).json()

    # Get the credits of the person using TMDB API
    creditsResponse = requests.get(
        "https://api.themoviedb.org/3/person/"
        + person_id
        + "/movie_credits?api_key="
        + api_key
    ).json()

    departmentsResponse = requests.get(
        "https://api.themoviedb.org/3/configuration/jobs" + "?api_key=" + api_key
    ).json()

    career = dict()

    career[detailsResponse["known_for_department"]] = dict()

    if detailsResponse["known_for_department"] == "Directing":
        career["Writing"] = dict()
        career["Acting"] = dict()
    elif detailsResponse["known_for_department"] == "Acting":
        career["Directing"] = dict()
        career["Writing"] = dict()
    else:
        career["Directing"] = dict()
        career["Writing"] = dict()
        career["Acting"] = dict()

    # Add all the possible departments to 'career'
    for department in departmentsResponse:
        if (
            department["department"] == "Actors"
            or department["department"] == "Directing"
            or department["department"] == "Writing"
            or department["department"] == detailsResponse["known_for_department"]
        ):
            continue
        else:
            career[department["department"]] = dict()

    creditsResponse["cast"] = sorted(
        creditsResponse["cast"],
        key=lambda x: datetime.strptime(x["release_date"], "%Y-%m-%d")
        if x["release_date"]
        else datetime.min,
        reverse=True,
    )

    creditsResponse["crew"] = sorted(
        creditsResponse["crew"],
        key=lambda x: datetime.strptime(x["release_date"], "%Y-%m-%d")
        if x["release_date"]
        else datetime.min,
        reverse=True,
    )

    for entry in creditsResponse["cast"]:
        credit = {
            "title": entry["title"],
            "id": entry["id"],
            "role": entry["character"],
        }

        if career["Acting"].get(entry["release_date"][:4]):
            career["Acting"][entry["release_date"][:4]].append(credit)
        else:
            career["Acting"][entry["release_date"][:4]] = [credit]

    for entry in creditsResponse["crew"]:
        credit = {
            "title": entry["title"],
            "id": entry["id"],
            "role": entry["job"],
        }

        if career[entry["department"]].get(entry["release_date"][:4]):
            career[entry["department"]][entry["release_date"][:4]].append(credit)
        else:
            career[entry["department"]][entry["release_date"][:4]] = [credit]

    person = {
        "name": detailsResponse["name"],
        "biography": detailsResponse["biography"],
        "hometown": detailsResponse["place_of_birth"],
        "birthday": dateFormat(detailsResponse["birthday"]),
        "profile": detailsResponse["profile_path"],
        "known_for": detailsResponse["known_for_department"],
        "career": career,
    }

    # Cuz kosom Israel
    if person["hometown"]:
        person["hometown"] = person["hometown"].replace("Israel", "Palestine")

    context = {"person": person}
    return render(request, "core/person.html", context)


def userList(request, list_id):
    list = List.objects.get(id=list_id)

    if list.title == "Watchlist":
        return redirect(f"/{ list.user.username }/watchlist")
    else:
        context = dict()
        context['self_watchlist'] = False
        context['list'] = list

        list_count = list.count()
        context['list_count'] = list_count

        user = request.user

        if user.is_authenticated:
            watched_count = 0
            for film in list.films.all():
                if user.profile.hasWatched(film):
                    watched_count += 1

            context['watched_count'] = watched_count

            if (list_count != 0):
                context['watched_percentage'] = round((watched_count / list_count) * 100)

        return render(request, "core/list.html", context)

@login_required
def newList(request):
    film_data = Film.objects.values()
    film_data_json = json.dumps(list(film_data), default=str)

    if request.POST:
        list_form = NewListForm(request.POST)

        if list_form.is_valid():
            created_list = list_form.save(commit=False)

            created_list.user = request.user
            created_list.save()

            film_ids = eval(request.POST['films'])
            for id in film_ids:
                film = Film.objects.get(tmdb_id=int(id))

                FilmListLog.objects.create(list=created_list, film=film)


            return redirect(f'/list/{ created_list.id }')
        
    else:
        list_form = NewListForm()

    context = {
        'form': list_form,
        'film_data': film_data,
        'film_data_json': film_data_json
    }

    return render(request, 'core/list_form.html', context)

@login_required
@csrf_protect
def favourite(request, movie_id):
    if request.method == "POST":
        user = request.user

        if user.profile.favourites.filter(tmdb_id=movie_id).exists():
            user.profile.favourites.remove(Film.objects.get(tmdb_id=movie_id))
            return JsonResponse({"status": "removed"})
        else:
            user.profile.favourites.add(Film.objects.get(tmdb_id=movie_id))
            return JsonResponse({"status": "added"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})


@login_required
def log(request, movie_id):
    if request.method == "POST":
        user = request.user
        film = Film.objects.get(tmdb_id=movie_id)

        log_form = LogForm(request.POST)

        if log_form.is_valid():
            log = log_form.save(commit=False)
            log.user = user
            log.film = film
            log.save()

            if user.profile.inWatchlist(film):
                user.profile.watchlist.films.remove(film)
                messages.success(request, f"{ film.title } has been logged successfully, and your watchlist is now updated.")
            else:
                messages.success(request, f"{ film.title } has been logged successfully.")
        else:
            for error in log_form.errors:
                messages.error(request, log_form.errors[error])

    return redirect(f"/movie/{ movie_id }")

@login_required
def add_to_list(request, movie_id):
    if request.method == "POST":
        film = Film.objects.get(tmdb_id=movie_id)

        response = [eval(x) for x in request.POST.getlist('lists_id')]

        added_films = []
        removed_films = []

        for list_id, film_added in response:
            list = List.objects.get(id=int(list_id))

            if list.has_film(film) and not film_added:
                FilmListLog.objects.get(list=list, film=film).delete()
                removed_films.append(film.title)
            elif not list.has_film(film) and film_added:
                FilmListLog.objects.create(list=list, film=film)
                added_films.append(film.title)

        messages.success(request, f'Your lists have been updated successfully')

    return redirect(f'/movie/{ movie_id }')


@login_required
def createGapt(request, movie_id):
    if request.method == "POST":
        user = request.user
        film = Film.objects.get(tmdb_id=movie_id)
        content = request.POST["content"]

        gapt = Gapt(user=user, film=film, content=content)
        gapt.save()

    return redirect(f"/movie/{ movie_id }")

@login_required
@csrf_protect
def likeGapt(request):
    if request.method == "POST":
        username = request.POST['username']
        gapt_id = request.POST['gapt_id']

        user = User.objects.get(username=username)
        gapt = Gapt.objects.get(id=gapt_id)

        query_set = LikeLog.objects.filter(user=user, gapt=gapt)

        if query_set.exists():
            query_set.first().delete()
            return JsonResponse({"status": "success", "message": -1})
        else:
            LikeLog.objects.create(user=user, gapt=gapt)
            return JsonResponse({"status": "success", "message": 1})

    else:
        return JsonResponse({"status": "error", "message": "An error has occurred. Please try again later!"})

@login_required
@csrf_protect
def reGapt(request):
    if request.method == "POST":
        username = request.POST['username']
        gapt_id = request.POST['gapt_id']

        user = User.objects.get(username=username)
        gapt = Gapt.objects.get(id=gapt_id)

        query_set = ReGaptLog.objects.filter(user=user, gapt=gapt)

        if query_set.exists():
            query_set.first().delete()
            return JsonResponse({"status": "success", "message": -1})
        else:
            ReGaptLog.objects.create(user=user, gapt=gapt)
            return JsonResponse({"status": "success", "message": 1})

    else:
        return JsonResponse({"status": "error", "message": "An error has occurred. Please try again later!"})


def search(request):
    query = request.GET["query"]

    moviesQuery = requests.get(
        "https://api.themoviedb.org/3/search/movie?query="
        + query
        + "&include_adult=false"
        + "&api_key="
        + api_key
    ).json()

    movies = {
        "results": moviesQuery["results"],
        "resultsCount": moviesQuery["total_results"],
        "pagesCount": moviesQuery["total_pages"],
    }

    peopleQuery = requests.get(
        "https://api.themoviedb.org/3/search/person?query="
        + query
        + "&api_key="
        + api_key
    ).json()

    people = {
        "results": peopleQuery["results"],
        "resultsCount": peopleQuery["total_results"],
        "pagesCount": peopleQuery["total_pages"],
    }

    usersQuery = User.objects.filter(
        profile__name__icontains=query, username__icontains=query
    )

    users = {
        "results": usersQuery.all(),
        "resultsCount": usersQuery.count() if usersQuery.exists() else 0,
    }

    gaptsQuery = Gapt.objects.filter(content__icontains=query)

    gapts = {
        "results": gaptsQuery.all(),
        "resultsCount": gaptsQuery.count() if gaptsQuery.exists() else 0,
    }

    context = {
        "query": query,
        "movies": movies,
        "people": people,
        "users": users,
        "gapts": gapts,
        "resultsCount": movies["resultsCount"]
        + people["resultsCount"]
        + users["resultsCount"],
    }

    return render(request, "core/search.html", context)

def search_films(request):
    if request.method == 'POST':
        query = request.POST['query']
        query_set = Film.objects.filter(Q(title__icontains=query) | Q(original_title__icontains=query))

        if query_set.exists():
            response = []
            for obj in query_set:
                film = {
                    'tmdb_id': obj.tmdb_id,
                    'title': obj.title,
                    'poster': obj.poster_path if not obj.custom_poster_path else obj.custom_poster_path,
                    'year': obj.release_date.year,
                    'directors': list(obj.careeractivity_set.filter(
                                    role="Director", department="Directing"
                                ).values_list("person__name", flat=True)),
                }

                response.append(film)

        else:
            response = 'No Films Found...'

        return JsonResponse({'data': response})
    
    return redirect('/404/')