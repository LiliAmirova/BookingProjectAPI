from core.clients.api_client import APIClient
import pytest
from datetime import datetime, timedelta
from faker import Faker


@pytest.fixture(scope="session")  # существует в рамках сессии
def api_client():  # это ф-ция, кот создает объект APIClient
    client = APIClient()  # создали объект класса APIClient (доступны все функции которые есть у нашего клиента
    client.auth()
    return client  # чтобы вернуть объект


@pytest.fixture
def booking_dates():  # ф-ция, которая генерит даты в определенном диапазоне от текущего дня
    today = datetime.today()
    checkin_date = today + timedelta(days=10)  # дата заезда
    checkout_date = checkin_date + timedelta(days=5)  # дата выезда

    return {
        "checkin": checkin_date.strftime('%Y-%m-%d'),
        "checkout": checkout_date.strftime('%Y-%m-%d')
    }


@pytest.fixture()  # с помощью faker генерим случайные данные
def generate_random_booking_data(booking_dates):
    faker = Faker() # создали объект класса Faker
    firstname = faker.first_name()
    lastname = faker.last_namr()
    totalprice = faker.random_number(digits=3)
    depositpaid = faker.boolean()
    additionalneeds = faker.sentence()

    data = { # словарь формируем
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "additionalneeds": additionalneeds
    }

    return data
