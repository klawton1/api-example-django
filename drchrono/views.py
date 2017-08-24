from django.views import generic

from django.http import HttpResponseRedirect

from django.urls import reverse

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect, render

from .forms import NewPatient, PatientInfo
from .models import ArrivedPatient

import datetime, pdb

class HomeView(generic.TemplateView):
  template_name = 'index.html'

class CheckinView(LoginRequiredMixin, generic.edit.FormView):
  template_name = 'checkin.html'
  form_class = NewPatient
  success_url = '/checkin/verify'

def logout_user(request):
  logout(request)
  return redirect('home')

@login_required
def checkin_verify(request):
  if request.method == "POST":
    f = request.POST
    ssn = "{}-{}-{}".format(f.get('ssn1'),f.get('ssn2'),f.get('ssn3'))
    first_name = f.get('first_name')
    last_name = f.get('last_name')
    patients = request.user.profile.get_patients(first_name=first_name, last_name=last_name)
    patient = {}
    for pat in patients:
      if pat['social_security_number'] == ssn:
        patient = pat
        break
    if patients and not patient: patient = patients[0]
    if patient:
      return redirect('patient-details', patient_id=patient['id'])
    else:
      messages.warning(request, "Couldn't find you in our records. Try entering your information again")
      return redirect('checkin')

@login_required
def patient_details(request, patient_id):
  patient = request.user.profile.get_patient(patient_id)
  patient_info = {
    'first_name': patient['first_name'],
    'last_name': patient['last_name'],
    'cell_phone': patient['cell_phone'],
    'email': patient['email'],
    'address': patient['address'],
    'zip_code': patient['zip_code'],
    'date_of_birth': patient['date_of_birth'],
  }
  form = PatientInfo(initial=patient_info)
  data = {
    'patient': patient, 
    'form':form, 
  }
  appointments = request.user.profile.get_appointments(patient_id=patient_id)
  if appointments:
    data['appointment'] = appointments[0]
    date = appointments[0]['scheduled_time']
    data['appointment']['scheduled_time'] = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    data['doctor'] = request.user.profile.get_doctor(appointments[0]['doctor'])
  return render(request, 'patient_details.html', data)

@login_required
def checkin_complete(request):
  if request.method == "POST":
    f = request.POST
    date = "{}{}{}".format(f.get('date_of_birth_month'), f.get('date_of_birth_day'), f.get('date_of_birth_year'))
    date = datetime.datetime.strptime(date, '%m%d%Y').date()
    info = {
      'first_name': f.get('first_name'),
      'last_name': f.get('last_name'),
      'email': f.get('email'),
      'address': f.get('address'),
      'zip_code': f.get('zip_code'),
      'cell_phone': f.get('cell_phone'),
      'date_of_birth': date,
    }
    res = request.user.profile.update_patient(f.get('patient_id'), info)
    try:
      res.raise_for_status()
    except:
      print("COULDN'T UPDATE!", res.text)
      messages.warning(request, "Could not update profile. ")
      return redirect('patient-details', patient_id=f.get('patient_id'))

    #Not Working
    arrived_patient_info = {
      'first_name': f.get('first_name'),
      'last_name': f.get('last_name'),
      'patient_id': f.get('patient_id'),
      'doctor_id': f.get('doctor_id')
    }
    if f.get('reason'):
      appointment_info = {
        'reason': f.get('reason'),
        'is_walk_in': True,
        'status': 'Arrived',
        'office': 162014,
        'exam_room': 0,
        'duration': 30,
        'doctor': f.get('doctor_id'),
        'patient': f.get('patient_id'),
        'scheduled_time': datetime.datetime.now()
      }
      appointment = request.user.profile.create_appointment(appointment_info)
      arrived_patient_info['appointment_id'] = appointment['id']
      #need to get appointment id
      ArrivedPatient.objects.create(**arrived_patient_info)
      # pdb.set_trace()
      messages.success(request, 'Thanks {}! Your doctor will be with you shortly'.format(f.get('first_name')))
      return redirect('checkin')
    else:
      arrived_patient_info['appointment_id'] = f.get('appointment_id')
      try:
        ArrivedPatient.objects.create(**arrived_patient_info)
        messages.success(request, 'Thanks {}! Your doctor will be with you shortly'.format(f.get('first_name')))
      except:
        messages.success(request, 'Thanks {}! Your already checked in'.format(f.get('first_name')))
        request.user.porfile.update_appointment(r.get('appointment_id'), {'status': 'Arrived'})
      return redirect('checkin')


