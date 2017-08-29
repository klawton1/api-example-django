from django.db import models
from django.contrib.auth.models import User
from social_django.utils import load_strategy

import datetime, requests, pytz

class ArrivedPatient(models.Model):
  first_name = models.CharField(max_length=200)
  last_name = models.CharField(max_length=200)
  created_at = models.DateTimeField(auto_now_add=True)
  patient_id = models.IntegerField(null=False, blank=False)
  doctor_id = models.IntegerField(null=False, blank=False)
  appointment_id = models.CharField(max_length=200, unique=True)
  time_waiting = models.DurationField(default=datetime.timedelta(seconds=0))
  seen_by_doctor = models.BooleanField(default=False)
  no_show = models.BooleanField(default=False)
  walk_in = models.BooleanField(default=False)

class Profile(models.Model):
  user = models.OneToOneField(User)
  is_doctor = models.BooleanField(default=False)
  doctor_id = models.IntegerField(null=False, blank=False)

  def __str__(self):
    return self.user.username

  def social(self):
    return self.user.social_auth.first()

  def access_header(self):
    social = self.social()
    return {'Authorization': 'Bearer {}'.format(social.get_access_token(load_strategy()))}

  def get_patients(self, first_name=None, last_name=None):
    # Access Token for Current User
    headers = self.access_header()
    patients = []
    patients_url = 'https://drchrono.com/api/patients'
    params = {}
    if first_name:
      params['first_name'] = first_name
    if last_name:
      params['last_name'] = last_name
    while patients_url:
      response = requests.get(patients_url, headers=headers, params=params)
      data = response.json()
      patients.extend(data['results'])
      patients_url = data['next'] # A JSON null on the last page
    return patients

  def get_patient(self, patient_id):
    # Access Token for Current User
    headers = self.access_header()
    patient_url = 'https://drchrono.com/api/patients/{}'.format(patient_id)
    response = requests.get(patient_url, headers=headers)
    patient = response.json()
    return patient

  def update_patient(self, patient_id, data):
    headers = self.access_header()
    patient_url = 'https://drchrono.com/api/patients/{}'.format(patient_id)
    response = requests.patch(patient_url, headers=headers, data=data)
    return response

  def create_appointment(self, appointment_data):
    headers = self.access_header()
    appointment_url = 'https://drchrono.com/api/appointments'
    response = requests.post(appointment_url, headers=headers, data=appointment_data)
    response = response.json()
    return response

  def update_appointment(self, appointment_id, appointment_data):
    headers = self.access_header()
    appointment_url = 'https://drchrono.com/api/appointments/{}'.format(appointment_id)
    response = requests.patch(appointment_url, headers=headers, data=appointment_data)
    return response

  def get_appointments(self, patient_id=None, doctor_id=None):
    headers = self.access_header()
    appointments_url = 'https://drchrono.com/api/appointments'
    params = {'date': datetime.datetime.now(pytz.timezone('US/Pacific')).date()}
    if patient_id:
      params['patient'] = patient_id
    appointments = []
    if doctor_id:
      params['doctor'] = doctor_id
    appointments = []
    while appointments_url:
      response = requests.get(appointments_url, headers=headers, params=params)
      data = response.json()
      appointments.extend(data['results'])
      appointments_url = data['next']
    return appointments

  def get_doctor(self, doctor_id):
    headers = self.access_header()
    doctor_url = 'https://drchrono.com/api/doctors/{}'.format(doctor_id)
    response = requests.get(doctor_url, headers=headers)
    doctor = response.json()
    return doctor

