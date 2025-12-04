from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.views.generic import View

# Create your views here.
class RegisterView(View):
    def get(self,request):
        form = UserCreationForm()
        return render(request, 'users/register.html', {'form':form})

    def post(self,request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username}')
            login(request, user)
            return redirect('home')
        return render(request, 'users/register.html', {'form':form})

class LoginView(View):
    def get(self,request):
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form':form})

    def post(self,request):
        form = AuthenticationForm(request=request, data=request.POST)
        print(f"POST data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Form errors: {form.errors}")
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            print(f"Authenticated user: {user}")
            if user is not None:
                login(request, user)
                messages.info(request,f'You are now logged in as {username}')
                return redirect('home')
        messages.error(request,'Invalid username or password')
        return render(request, 'users/login.html', {'form':form})

@login_required
def home_view(request):
    return render(request, 'teachers/home.html')
