import requests
import json
# import related models here
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    # print(f'get_request: {kwargs}')
    # print(f'GET from {url}')

    api_key = kwargs.get('api_key')
    headers = {'Content-Type': 'application/json'}
    authenticator = HTTPBasicAuth('apikey', api_key) if api_key else None

    try:
        response = requests.get(url, auth=authenticator, headers=headers, params=kwargs)
    except:
        print("Network exception occurred")
    else:
        status_code = response.status_code
        # print(f'With status {status_code}')
        json_data = json.loads(response.text)
        return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(f'kwargs: {kwargs}')
    print(f'json_payload: {json_payload}')
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occurred")
    else:
        print(response)



# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get('state')
    # Call get_request with a URL parameter
    dealers = get_request(url, state=state)
    # For each dealer object
    for dealer in dealers:
        # Create a CarDealer object with values in `dealer` object
        dealer_obj = CarDealer(address=dealer["address"],
                               city=dealer["city"],
                               full_name=dealer["full_name"],
                               id=dealer["id"],
                               lat=dealer["lat"],
                               long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"],
                               state=dealer['state'],
                               zip=dealer["zip"])

        results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    dealer_id = kwargs.get('dealerId')
# - Call get_request() with specified arguments
    reviews = get_request(url, dealerId=dealer_id)
    for review in reviews:
        # - Parse JSON results into a DealerView object list
        review_obj = DealerReview(dealership=review.get("dealership"),
                                  name=review.get("name"),
                                  purchase=review.get("purchase"),
                                  review=review.get("review"),
                                  purchase_date=review.get("purchase_date"),
                                  car_make=review.get("car_make"),
                                  car_model=review.get("car_model"),
                                  car_year=review.get("car_year"),
                                  sentiment=None,
                                  id=review.get("id"))

        review_obj.sentiment = analyze_review_sentiments(review_obj.review)
        results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    if not dealerreview:
        return "neutral"

    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/b2f336d6-2fd5-4890-a58a-9e994467faf8"
    # url = None
    api_key = "a-iijB6HCqi2D5_e0q7cjEJSRuml2z3NlGa_cvJa3Bvi"
    # api_key = None
    # - Call get_request() with specified arguments
    json_data = get_request(url=f'{url}/v1/analyze', api_key=api_key, version="2018-03-16", text=dealerreview, features="sentiment", return_analyzed_text=True, language='en')
    if json_data and json_data.get("sentiment"):
        # - Get the returned sentiment label such as Positive or Negative
        return json_data["sentiment"]["document"]["label"]
    else:
        print("neutral")
        return "neutral"

