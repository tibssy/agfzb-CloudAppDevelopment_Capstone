import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from django.conf import settings


def get_request(url, **kwargs):
    """
    get_request(url, **kwargs)

    Makes a get request to the given URL with the given keyword arguments.

    Parameters:
    url (str): The URL to make a request to.
    **kwargs (dict): Optional keyword arguments.

    Returns:
    json_data (dict): The response data in JSON format.

    Raises:
    Prints 'Network exception occurred' if a network exception occurs.
    """
    api_key = kwargs.get('api_key')
    headers = {'Content-Type': 'application/json'}
    authenticator = HTTPBasicAuth('apikey', api_key) if api_key else None
    try:
        response = requests.get(url, auth=authenticator, headers=headers, params=kwargs)
    except:
        print('Network exception occurred')
    else:
        json_data = json.loads(response.text)
        return json_data


def post_request(url, json_payload, **kwargs):
    """
    post_request(url, json_payload, **kwargs)

    Send a POST request to the specified URL, with the given json payload and any additional keyword arguments.

    Parameters:
        url (str): The URL to send the request to.
        json_payload (dict): The json payload to send in the request.
        **kwargs (dict): Any additional keyword arguments to send in the request.

    Returns:
        json_data (dict): The response data in JSON format.

    Raises:
        Network exception (Exception): If a network exception occurs.
    """
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print('Network exception occurred')
    else:
        json_data = json.loads(response.text)
        return json_data


def get_dealers_from_cf(url, **kwargs):
    """
    get_dealers_from_cf(url, **kwargs)

    Retrieve Car Dealer information from the given url and any additional keyword arguments.

    Parameters
    ----------
    url : str
        The url used to retrieve the Car Dealer information.
    **kwargs : dict
        Any additional keyword arguments used to filter the Car Dealer information.

    Returns
    -------
    list
        A list of CarDealer objects.
    """
    results = []
    state = kwargs.get('state')
    print(f'kwargs: {kwargs}')
    dealers = get_request(url, state=state)
    for dealer in dealers:
        dealer_obj = CarDealer(address=dealer.get('address'),
                               city=dealer.get('city'),
                               full_name=dealer.get('full_name'),
                               id=dealer.get('id'),
                               lat=dealer.get('lat'),
                               long=dealer.get('long'),
                               short_name=dealer.get('short_name'),
                               st=dealer.get('st'),
                               state=dealer.get('state'),
                               zip=dealer.get('zip'))

        results.append(dealer_obj)

    return results


def get_dealer_reviews_from_cf(url, **kwargs):
    """
    This function takes in a URL and keyword arguments, and returns a list of DealerReview objects.
    It makes an API call to the given URL, passing in the 'dealerId' keyword argument if it is provided.
    It then loops through the reviews returned, creating a DealerReview object for each one and setting
    the sentiment attribute to the result of the analyze_review_sentiments() function.
    Finally, it returns the list of DealerReview objects.
    """
    results = []
    dealer_id = kwargs.get('dealerId')
    reviews = get_request(url, dealerId=dealer_id)
    for review in reviews:
        review_obj = DealerReview(dealership=review.get('dealership'),
                                  name=review.get('name'),
                                  purchase=review.get('purchase'),
                                  review=review.get('review'),
                                  purchase_date=review.get('purchase_date'),
                                  car_make=review.get('car_make'),
                                  car_model=review.get('car_model'),
                                  car_year=review.get('car_year'),
                                  sentiment=None,
                                  id=review.get('id'))

        review_obj.sentiment = analyze_review_sentiments(review_obj.review)
        results.append(review_obj)

    return results


def analyze_review_sentiments(dealer_review):
    """
    analyze_review_sentiments(dealer_review)

    This function takes in a dealer review and returns a sentiment label based on the review.
    It uses the Watson Natural Language Understanding API to analyze the sentiment of the review and
    returns a label of 'positive', 'negative', or 'neutral'.
    """
    if not dealer_review:
        return 'neutral'

    json_data = get_request(url=f'{settings.NLU_URL}/v1/analyze',
                            api_key=settings.NLU_KEY,
                            version='2022-08-10',
                            text=dealer_review,
                            features='sentiment',
                            return_analyzed_text=True,
                            language='en')

    if json_data and json_data.get('sentiment'):
        return json_data['sentiment']['document']['label']
    else:
        return 'neutral'


def get_dealer_by_id_from_cf(url, dealer_id):
    """
    This function retrieves a dealer from a given URL with a specified dealer ID.

    Parameters:
        url (str): The URL to make the request from.
        dealer_id (int): The ID of the dealer to retrieve.

    Returns:
        dict: The dealer information as a dictionary.
    """
    return get_request(url, dealerId=dealer_id)[0]
