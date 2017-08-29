from django import forms
import datetime
# forms go here
class NewPatient(forms.Form):
  # TODO: Define form fields here
  first_name = forms.CharField()
  last_name = forms.CharField()
  ssn1 = forms.CharField(required=False, label="Social Security Number (optional)", widget=forms.TextInput(attrs={'maxlength':'3', 'pattern':'[0-9]{3}'}))
  ssn2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'maxlength':'2', 'pattern':'[0-9]{2}'}))
  ssn3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'maxlength':'4', 'pattern':'[0-9]{4}'}))

class PatientInfo(forms.Form):
  reason = forms.CharField(widget=forms.Textarea)
  first_name = forms.CharField(required=False)
  last_name = forms.CharField(required=False)
  email = forms.CharField(required=False)
  cell_phone = forms.CharField(required=False)
  address = forms.CharField(required=False)
  zip_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'maxlength':'5', 'pattern':'[0-9]{5}'}))
  date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, datetime.datetime.now().year)))
