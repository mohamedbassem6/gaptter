from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date, datetime
from django.core.validators import MaxValueValidator, MinValueValidator
import json
import requests
import math


class Person(models.Model):
    tmdb_id = models.PositiveBigIntegerField(blank=False, unique=True)
    name = models.CharField(max_length=70, blank=True)
    profile_picture_path = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    career = models.JSONField(blank=True)
    birthday = models.DateField(blank=True, null=True)
    location = models.TextField(blank=True)
    known_for_department = models.TextField(blank=True)

    last_updated = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = 'People'

    def save(self, *args, **kwargs):
        # Get the details of the person, using TMDB API
        detailsResponse = requests.get(
            "https://api.themoviedb.org/3/person/"
            + self.tmdb_id
            + "?api_key="
            + settings.TMDB_API_KEY
        ).json()

        # Get the credits of the person, using TMDB API
        creditsResponse = requests.get(
            "https://api.themoviedb.org/3/person/"
            + self.tmdb_id
            + "/movie_credits?api_key="
            + settings.TMDB_API_KEY
        ).json()

        departmentsResponse = requests.get(
            "https://api.themoviedb.org/3/configuration/jobs"
            + "?api_key="
            + settings.TMDB_API_KEY
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

        self.name = detailsResponse["name"]

        self.bio = detailsResponse["biography"]

        if detailsResponse["place_of_birth"] != None:
            self.location = detailsResponse["place_of_birth"]

        if detailsResponse["birthday"] != None:
            self.birthday = datetime.strptime(detailsResponse["birthday"], "%Y-%m-%d")

        if detailsResponse["profile_path"] != None:
            self.profile_picture_path = detailsResponse["profile_path"]

        if detailsResponse["known_for_department"] != None:
            self.known_for_department = detailsResponse["known_for_department"]

        self.career = json.dumps(career)

        self.last_updated = date.today()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Genre(models.Model):
    tmdb_id = models.PositiveBigIntegerField(blank=False)
    name = models.TextField(blank=False)

    def __str__(self):
        return self.name


class Film(models.Model):
    tmdb_id = models.PositiveIntegerField(blank=False, unique=True)
    title = models.TextField(blank=True)
    original_title = models.TextField(blank=True)
    runtime = models.PositiveIntegerField(blank=True)
    custom_backdrop_path = models.TextField(blank=True)
    backdrop_path = models.TextField(blank=True)
    custom_poster_path = models.TextField(blank=True)
    poster_path = models.TextField(blank=True)
    overview = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)
    people = models.ManyToManyField(Person, through="CareerActivity", symmetrical=True)
    genres = models.ManyToManyField(Genre, blank=True)

    last_updated = models.DateField(default=date.today)

    def save(self, *args, **kwargs):
        detailsResponse = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(self.tmdb_id)
            + "?api_key="
            + settings.TMDB_API_KEY
        ).json()

        creditsResponse = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(self.tmdb_id)
            + "/credits?api_key="
            + settings.TMDB_API_KEY
        ).json()

        self.title = detailsResponse["title"]
        self.original_title = detailsResponse["original_title"]
        self.overview = detailsResponse["overview"]
        self.poster_path = detailsResponse["poster_path"]
        self.runtime = detailsResponse["runtime"]
        self.release_date = datetime.strptime(
            detailsResponse["release_date"], "%Y-%m-%d"
        )

        backdrops = requests.get(
            "https://api.themoviedb.org/3/movie/"
            + str(self.tmdb_id)
            + "/images?include_image_language=null&api_key="
            + settings.TMDB_API_KEY
        ).json()["backdrops"]

        if backdrops:
            self.backdrop_path = max(
                backdrops, key=lambda x: x["vote_average"] * x["vote_count"]
            )["file_path"]
        else:
            self.backdrop_path = ""

        super().save(*args, **kwargs)

        for genre in detailsResponse["genres"]:
            genre_object, created = Genre.objects.get_or_create(
                tmdb_id=genre["id"], defaults={"name": genre["name"]}
            )
            self.genres.add(genre_object)

        for actor in creditsResponse["cast"]:
            actor_object, created = Person.objects.get_or_create(
                tmdb_id=str(actor["id"])
            )
            CareerActivity.objects.get_or_create(
                film=self,
                person=actor_object,
                department="Acting",
                role=actor["character"],
            )

        for person in creditsResponse["crew"]:
            person_object, created = Person.objects.get_or_create(
                tmdb_id=str(person["id"])
            )
            CareerActivity.objects.get_or_create(
                film=self,
                person=person_object,
                department=person["department"],
                role=person["job"],
            )

    def __str__(self):
        return str(self.tmdb_id) + ":\t" + self.title


class CareerActivity(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    department = models.TextField()
    role = models.TextField()

    def __str__(self):
        if self.department == "Acting":
            return f"{ self.person.name } starred in '{ self.film.title }' as ({ self.role })"
        else:
            return f"{ self.person.name } worked in '{ self.film.title }' as ({ self.role })"


class List(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    films = models.ManyToManyField(Film, through='FilmListLog', blank=True)
    ordered = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(default=timezone.now)

    def count(self):
        return self.films.count()
    
    def has_film_id(self, film_id):
        return self.films.filter(tmdb_id=film_id).exists()
    
    def has_film(self, film):
        return self.films.contains(film)

    def __str__(self):
        return f"@{ self.user.username }: '{ self.title }' ({ self.id })"
    

class FilmListLog(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    order = models.IntegerField(blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.order = self.list.count() + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.order} {self.film.title} in {self.list.title}'
    
    class Meta:
        ordering = ('order',)


class Gapt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    film = models.ForeignKey(Film, on_delete=models.CASCADE, blank=False)
    content = models.CharField(max_length=512, blank=False)
    date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, through='LikeLog', related_name='likes')
    reGapts = models.ManyToManyField(User, through='reGaptLog', related_name='reGapts')

    def __str__(self):
        return "@" + self.user.username + ": " + self.film.title
    
    def model_name(self):
        return self._meta.object_name

    def whenPosted(self):
        now = timezone.now()

        datePosted = self.date

        diff = now - datePosted

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 7:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 7 and diff.days < 365:
            return datePosted.strftime("%B %-d at %-I:%M %p")

        if diff.days >= 365:
            return datePosted.strftime("%B %-d, %Y at %-I:%M %p")

    def getLikesCount(self):
        return self.likes.count()

    def getReGaptsCount(self):
        return self.reGapts.count()
    
    def isLikedBy(self, user):
        return self.likes.filter(username=user.username).exists()
    
    def isReGaptdBy(self, user):
        return self.reGapts.filter(username=user.username).exists()
    
    def isSeenBy(self, user):
        return SeenGapt.objects.filter(user=user, gapt=self).exists()
    

class LikeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    gapt = models.ForeignKey(Gapt, on_delete=models.CASCADE, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return f'@{ self.user.username } liked gapt #{ self.gapt.id } on { self.date }'
    

class ReGaptLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    gapt = models.ForeignKey(Gapt, on_delete=models.CASCADE, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return f'@{ self.user.username } reGapt\'d gapt #{ self.gapt.id } on { self.date }'
    
    def model_name(self):
        return self._meta.object_name
    

class SeenGapt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    gapt = models.ForeignKey(Gapt, on_delete=models.CASCADE, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return f'@{ self.user.username } saw gapt #{ self.gapt.id } on { self.date }'


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    film = models.ForeignKey(Film, on_delete=models.CASCADE, blank=True)
    date = models.DateField(
        default=date.today,
        validators=[
            MaxValueValidator(
                date.today(),
                message="You have entered a date that is beyond the current timeline. Please check your flux capacitor and try again.",
            )
        ],
    )
    time = models.TimeField(default=timezone.now)
    rating = models.DecimalField(
        decimal_places=1,
        max_digits=2,
        validators=[
            MaxValueValidator(5, message="Rating can't be a value more than 5."),
            MinValueValidator(0, message="Rating can't be a negative value."),
        ],
    )

    def __str__(self):
        return f"@{ self.user.username }: '{ self.film.title }', { self.rating }"
