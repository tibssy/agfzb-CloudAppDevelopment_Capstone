from django.db import models


class CarMake(models.Model):
    """
    This class CarMake is a model that stores the name and description of a car make.
    It has two fields: name and description. The name field is a CharField with a max length of 50 that cannot be null.
    The description field is a CharField with a max length of 300.
    This class has a __str__ method that returns a string representation of the CarMake object.
    """
    name = models.CharField(null=False, max_length=50)
    description = models.CharField(max_length=300)

    def __str__(self):
        return f'Name: {self.name}, Description: {self.description}'


class CarModel(models.Model):
    """
    CarModel is a class for cars models that contains information about the car make, name, dealer ID, type, and year.

    Attributes:
    make (ForeignKey): CarMake object associated with this car model
    name (CharField): Name of the car model
    dealer_id (IntegerField): ID of the dealer associated with this car model
    type (CharField): Type of the car model (sedan, suv, wagon)
    year (DateField): Year of the car model

    Methods:
    __str__(): Returns a string representation of the car model
    """
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    TYPES = ((SEDAN, 'Sedan'), (SUV, 'Suv'), (WAGON, 'Wagon'))

    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=50)
    dealer_id = models.IntegerField()
    type = models.CharField(max_length=50, choices=TYPES)
    year = models.DateField()

    def __str__(self):
        return f'Name: {self.name}, Dealer ID: {self.dealer_id}, Type: {self.type}, Year: {self.year}'


class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, state, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.state = state
        self.zip = zip

    def __str__(self):
        return f'Dealer name: {self.full_name}'


class DealerReview:
    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment, id):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
        self.id = id

    def __str__(self):
        return f'Name: {self.name}, Review: {self.review}, Sentiment: {self.sentiment}'
