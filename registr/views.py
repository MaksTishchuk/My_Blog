from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views.generic.edit import FormView
from .forms import UserCreateForm
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User


class RegisterFormView(FormView):
    form_class = UserCreateForm
    success_url = "/user/login"
    template_name = "registr/register.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegisterFormView, self).form_invalid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "registr/login.html"
    success_url = "/"

    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)



class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")
