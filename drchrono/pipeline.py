import requests, datetime, pytz
from .models import Profile

def create_profile(backend, user, response, *args, **kwargs):
  if kwargs.get('is_new'):
    profile = Profile.objects.create(
      user = user,
      is_doctor = response.get('is_doctor'),
      doctor_id = response.get('doctor'),
    )
    api_response = requests.get('https://drchrono.com/api/users/current', headers={
      'Authorization': 'Bearer %s' % response.get('access_token'),
    })
    api_response.raise_for_status()
    data = api_response.json()
    if response.get('is_doctor'):
      api_response = requests.get('https://drchrono.com/api/doctors/{}'.format(data.get('doctor')), headers={
        'Authorization': 'Bearer %s' % response.get('access_token'),
      })
      data = api_response.json()
      user.first_name = data.get('first_name')
      user.last_name = data.get('last_name')
      user.email =data.get('email')
      user.save()
