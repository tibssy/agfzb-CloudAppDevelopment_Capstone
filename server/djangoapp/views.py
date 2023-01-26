from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        dealer_names = [dealer.short_name for dealer in dealerships]
        # Return a list of dealer short name
        context['dealerships'] = dealerships
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
# def get_dealer_details(request):
    context = {}
    if request.method == 'GET':
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        review_names = ', '.join([f'[ Name: {review.name}, Review: {review.review}, Sentiment: {review.sentiment} ]' for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(review_names)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
# def add_review(request):
    if request.user.is_authenticated:
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/tibssy1982_dev/api/post-review"
        first_name = request.user.first_name
        last_name = request.user.last_name

        review = {}
        review["name"] = f'{first_name} {last_name}' if first_name and last_name else request.user.username
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = int(dealer_id)
        review["review"] = "This is a great car dealer"
        review["purchase"] = "false"

        print(review)

        json_payload = {"review": review}
        review_response = post_request(url, json_payload, dealerId=dealer_id)


        return HttpResponse(review_response)