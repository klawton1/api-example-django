from django.db import models
from django.contrib.auth.models import User
import datetime

class ArrivedPatient(models.Model):
  first_name = models.CharField(max_length=200)
  last_name = models.CharField(max_length=200)
  ssn = models.CharField(max_length=50)
  created_at = models.DateField(auto_now_add=True)
  patient_id = models.IntegerField()
  doctor_id = models.IntegerField()
  chart_id = models.CharField(max_length=200)
  appointment_id = models.CharField(max_length=200)
  time_waiting = models.DurationField(default=datetime.timedelta(seconds=0))
  seen_by_doctor = models.BooleanField(default=False)