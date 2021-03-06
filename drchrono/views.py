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

import datetime, pytz, pdb

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
    #Check for successful patient update
    try:
      res.raise_for_status()
    except:
      messages.warning(request, "Could not update profile. ")
      return redirect('patient-details', patient_id=f.get('patient_id'))
    arrived_patient_info = {
      'first_name': f.get('first_name'),
      'last_name': f.get('last_name'),
      'patient_id': f.get('patient_id'),
      'doctor_id': f.get('doctor_id')
    }
    # If this is a walk in appointment
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
      arrived_patient_info['walk_in'] = True
      ArrivedPatient.objects.create(**arrived_patient_info)
      messages.success(request, 'Thanks {}! Your doctor will be with you shortly'.format(f.get('first_name')))
      return redirect('checkin')
    else:
      arrived_patient_info['appointment_id'] = f.get('appointment_id')
      try:
        ArrivedPatient.objects.create(**arrived_patient_info)
        messages.success(request, 'Thanks {}! Your doctor will be with you shortly'.format(f.get('first_name')))
      except:
        messages.success(request, 'Thanks {}! Your already checked in'.format(f.get('first_name')))
      request.user.profile.update_appointment(f.get('appointment_id'), {'status': 'Arrived'})
      return redirect('checkin')

class AppointmentsView(LoginRequiredMixin,generic.TemplateView):
  template_name = "appointments.html"
  def get_context_data(self, **kwargs):
      context = super(AppointmentsView, self).get_context_data(**kwargs)
      patients = ArrivedPatient.objects.filter(seen_by_doctor=False, no_show=False)
      appointments = self.request.user.profile.get_appointments()
      #change str of scheduled_time to datetime for template filter
      for appointment in appointments: 
        appointment['scheduled_time'] = datetime.datetime.strptime(appointment['scheduled_time'], "%Y-%m-%dT%H:%M:%S")
      context['arrived'] = patients
      context['appointments'] = appointments
      patients_seen = ArrivedPatient.objects.filter(seen_by_doctor=True)
      total_time = datetime.timedelta()
      # Add time deltas for all patients who have had appointments
      for patient in patients_seen: total_time += patient.time_waiting 
      avg_wait = int(total_time.total_seconds() / len(patients_seen) / 60)
      context['avg_wait'] = avg_wait
      context['status'] = set(['Cancelled','Complete','No Show','Rescheduled'])
      return context

def update_appointment(request):
  if request.method == "POST":
    f = request.POST
    status = f.get('status')
    app_id = f.get('appointment_id')
    appointment = ArrivedPatient.objects.filter(appointment_id=app_id, seen_by_doctor=False, no_show=False).first()
    response = request.user.profile.update_appointment(app_id, {'status': status})
    try:
      response.raise_for_status()
      messages.success(request, "Successfully updated appointment")
    except:
      messages.warning(request, "Error while updating appointment")
    if appointment:
      date = datetime.datetime.now(pytz.utc)
      appointment.time_waiting = date - appointment.created_at
      if status in ['Complete','In Room']:
        appointment.seen_by_doctor = True
      else:
        appointment.no_show = True
      appointment.save()
    return redirect('appointments')
      


