from django.conf.urls import include, url
import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^appointments/$', views.AppointmentsView.as_view(), name='appointments'),
    url(r'^appointments/update$', views.update_appointment, name='update-appointment'),
    url(r'^checkin/$', views.CheckinView.as_view(), name='checkin'),
    url(r'^checkin/verify/$', views.checkin_verify, name='checkin-verify'),
    url(r'^checkin/complete/$',views.checkin_complete, name='checkin-complete'),
    url(r'^checkin/(?P<patient_id>[0-9]+)/details/$', views.patient_details, name='patient-details'),
    url(r'', include('social_django.urls', namespace='social')),
]
