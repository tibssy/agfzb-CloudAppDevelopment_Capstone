import logging
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.conf import settings


logger = logging.getLogger(__name__)


def about(request):
    """
    This function handles a GET request for the about page of a Django application.
    It renders the about page template and returns the response.

    Parameters:
    request (HttpRequest): The request object containing the client's request information

    Returns:
    HttpResponse: The response object containing the rendered about page template.
    """
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html')


def contact(request):
    """
    This function handles a GET request to display the contact page of the Django App.

    Args:
        request: The request to be handled by the function.

    Returns:
        A rendered template of the contact page.
    """
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html')


def login_request(request):
    """
    This function handles a login request. It checks if the request is a POST request, and if so,
    it authenticates the user with the given username and password. If the authentication is successful,
    the user is logged in and redirected to the djangoapp:index page. If authentication fails,
    the user is redirected to the djangoapp:index page. If the request is not a POST request,
    the user is rendered the djangoapp:index page.
    """
    context = {}
    if request.method == 'POST':
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


def logout_request(request):
    """
    Logs out the user from the current request.

    Parameters:
    request (HttpRequest): The request object containing information about the current request.

    Returns:
    HttpResponseRedirect: A response redirecting the user to the main index page.
    """
    if request.method == 'GET':
        logout(request)
        return redirect('djangoapp:index')


def registration_request(request):
    """
    This function processes a registration request from a user.
    It checks if the user already exists and if not, creates a new user.

    Parameters:
        request (HttpRequest): The request object containing the user's registration information.

    Returns:
        render: The registration page if the user already exists.
        redirect: The index page if the user does not already exist.
    """
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        password = request.POST.get('psw')
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug(f'{username} is new user')
        if not user_exist:
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)

            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)


def get_dealerships(request):
    """
    This function retrieves a list of dealerships from a Cloud Foundry endpoint and renders them in an HTML template.

    Parameters:
        request (HttpRequest): The request object containing information about the current request.

    Returns:
        render (HttpResponse): An HttpResponse object containing the rendered HTML template with
        the list of dealerships.
    """
    if request.method == 'GET':
        url = f'{settings.CLOUD_URL}/get-dealership'
        dealerships = get_dealers_from_cf(url)
        context = {'dealerships': dealerships}
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, dealer_id):
    """
    This function is used to render the dealer details page for the given dealer ID.
    It retrieves the dealer reviews from Cloud Foundry and the dealer details from the Cloud Foundry API,
    and then renders the page with the dealer details and reviews.

    Args:
        request (HttpRequest): The request object containing the information about the request.
        dealer_id (int): The ID of the dealer.

    Returns:
        HttpResponse: The response object containing the rendered page.
    """
    if request.method == 'GET':
        url = f'{settings.CLOUD_URL}/get-review'
        dealer_url = f'{settings.CLOUD_URL}/get-dealership'
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        context = {'dealer_id': dealer_id, 'dealer': dealer, 'reviews': reviews}
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id):
    """
    add_review(request, dealer_id)

    This function allows a user to post a review of a car dealership.

    Parameters:
    request: The incoming HTTP request.
    dealer_id: The ID of the car dealership.

    Returns:
    Redirects to the details page of the car dealership.
    """
    if request.user.is_authenticated:
        url = f'{settings.CLOUD_URL}/post-review'
        dealer_url = f'{settings.CLOUD_URL}/get-dealership'
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        first_name = request.user.first_name
        last_name = request.user.last_name

        if request.method == 'GET':
            print(f'GET called')
            cars = CarModel.objects.all()
            context = {'dealer_id': dealer_id, 'dealer': dealer, 'cars': cars}
            return render(request, 'djangoapp/add_review.html', context)

        elif request.method == 'POST':
            car_id = request.POST.get('car')
            car = CarModel.objects.get(pk=car_id)

            review = {
                'car_make': car.make.name,
                'car_model': car.name,
                'car_year': car.year.strftime('%Y'),
                'dealership': dealer_id,
                'name': f'{first_name} {last_name}' if first_name and last_name else request.user.username,
                'purchase': True if request.POST.get('purchase') else False,
                'purchase_date': request.POST.get('purchase_date'),
                'review': request.POST.get('review')
            }

            json_payload = {"review": review}
            response = post_request(url, json_payload, dealerId=dealer_id)
            print(response)
            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
