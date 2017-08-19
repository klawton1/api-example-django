from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect


class HomeView(generic.TemplateView):
  template_name = 'index.html'

def logout_user(request):
  logout(request)
  return redirect('home')
