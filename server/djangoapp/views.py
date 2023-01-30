from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return render(request, 'djangoapp:index', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    if request.method == "GET":
        logout(request)
        return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug(f'{username} is new user')
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == 'GET':
        url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-dealership'
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-review"
        dealer_url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-dealership'
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        context = {"dealer_id": dealer_id, "dealer": dealer, "reviews": reviews}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/post-review"
        dealer_url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-dealership'
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        first_name = request.user.first_name
        last_name = request.user.last_name

        if request.method == 'GET':
            cars = CarModel.objects.all()
            context = {"dealer_id": dealer_id, "dealer": dealer, "cars": cars}
            return render(request, 'djangoapp/add_review.html', context)

        elif request.method == 'POST':
            car_id = request.POST.get('car')
            car = CarModel.objects.get(pk=car_id)

            review = {
                'car_make': car.make.name,
                'car_model': car.name,
                'car_year': car.year.strftime("%Y"),
                'dealership': dealer_id,
                'name': f'{first_name} {last_name}' if first_name and last_name else request.user.username,
                'purchase': True if request.POST.get('purchase') else False,
                'purchase_date': request.POST.get('purchase_date'),
                'review': request.POST.get('review')
            }

            json_payload = {"review": review}
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
