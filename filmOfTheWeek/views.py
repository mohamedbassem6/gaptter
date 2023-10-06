from django.shortcuts import render
from filmOfTheWeek.models import Film

# Create your views here.
def home(request):
    film = Film.objects.get(title='The Nice Guys')
    return render(request, 'filmOfTheWeek/fotw_home.html', {'film': film})