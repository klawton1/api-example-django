from django.conf.urls import include, url
import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'', include('social_django.urls', namespace='social')),
]
