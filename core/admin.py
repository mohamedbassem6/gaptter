from typing import Any
from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Film)
admin.site.register(Person)
admin.site.register(CareerActivity)
admin.site.register(Log)
admin.site.register(Gapt)
admin.site.register(SeenGapt)
admin.site.register(LikeLog)
admin.site.register(ReGaptLog)
admin.site.register(List)
admin.site.register(FilmListLog)