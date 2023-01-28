from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)
dealerships = None


# Create your views here.


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
        print(f'Log out the user {request.user.username}')
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
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, 'djangoapp/index.html', context)
def get_dealerships(request):
    context = {}
    if request.method == 'GET':
        url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-dealership'
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)

        # Stored Dealer Names With Ids in MIDDLEWARE
        request.session["dealerships"] = {dealer.id: dealer.full_name for dealer in dealerships}
        request.session.save()

        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == 'GET':
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)

        if request.session.get('dealerships'):
            context['dealer'] = request.session["dealerships"][str(dealer_id)]
        else:
            dealer_url = 'https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-dealership'
            context['dealer'] = get_dealer_by_id(dealer_url, dealer_id)

        context['reviews'] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
# def add_review(request):
    if request.user.is_authenticated:
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/post-review"
        first_name = request.user.first_name
        last_name = request.user.last_name

        review = dict()
        review["name"] = f'{first_name} {last_name}' if first_name and last_name else request.user.username
        review["time"] = datetime.utcnow().isoformat()
        review["car_make"] = 'Subaru'
        review["car_model"] = 'Foster'
        review["car_year"] = 2020
        review["dealership"] = int(dealer_id)
        review["review"] = "worst ever dealership"
        review["purchase"] = "false"

        json_payload = {"review": review}
        # review_response = post_request(url, json_payload, dealerId=dealer_id)

        # return HttpResponse(review_response)
        return HttpResponse('hello')