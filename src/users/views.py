from django.forms import forms
from django.http import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileUpdateForm, UserRegisterForm, UserCreationForm, UserUpdateForm

# Create your views here.

def register(request):

    if request.method == 'POST':

        form = UserRegisterForm(request.POST)

        if form.is_valid():
            forms.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Successfuly created account: {username}')
            return redirect('loging')

    else:
        form = UserRegisterForm()

    return render(request, '#', {'forms': form})

    
@login_required
def profile(requst):

    if request.method == 'POST':
        update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if update_form.is_valid() and profile_form.is_valid():
            update_form.save()
            profile_form.save()
            messages.success(request, f'Account has been updated')
            return redirect('profile')

    else:
        update_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, '#', {'update_form': update_form, 'profile_form': profile_form})


@login_required
def SearchView(request):
    if request.method == 'POST':
        cn = request.POST.get('search')
        results = User.objects.filter(username__contains=cn)
        context = {'results': results}
        
        return render(request, '#', context)