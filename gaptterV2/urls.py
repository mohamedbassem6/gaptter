"""
URL configuration for gaptterV2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as authViews
from users import views as usersViews
from django.conf import settings
from django.conf.urls.static import static

from notifications.consumers import NotificationConsumer

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', usersViews.register, name='register'),
    path('login/', authViews.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', authViews.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', authViews.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('profile/', usersViews.profile, name='profile'),
    path('profile/watchlist/', usersViews.profile_watchlist, name='profile_watchlist'),
    path('profile/settings/', usersViews.profileSettings, name='profileSettings'),

    path('', include('core.urls')),
    path('notifications/', include('notifications.urls')),
    path('films-of-the-week/', include('filmOfTheWeek.urls')),
    # path('chat/', include('chat.urls')),

    path('<username>/', usersViews.user, name='user'),
    path('<username>/watchlist/', usersViews.watchlist, name='user_watchlist'),
    path('<username>/follow/', usersViews.followUser, name='followUser'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]