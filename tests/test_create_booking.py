import allure
import pytest
import requests
from conftest import api_client, generate_random_booking_data
from pydantic import ValidationError
from core.models.booking import BookingResponse

@allure.feature('Test Booking')
@allure.story('Positive:Creating booking with random data')
def test_create_booking_with_random_data(api_client,generate_random_booking_data):
    with allure.step("Подготовка данных для  создания брони"):
        booking_data = generate_random_booking_data

    with allure.step("Отправка запроса на создание бронирования и валидация"):
        #response = requests.post("https://restful-booker.herokuapp.com/booking", json=booking_data)
        response = api_client.create_booking(booking_data,status_code=200)
        response_json = response.json()

        try:
            BookingResponse(**response_json)
        except ValidationError as e:
            raise ValidationError(f"Response validation failed: {e}")

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    with allure.step("Проверка параметров брони в ответе"):
        assert 'bookingid' in response_json, "В ответе отсутствует bookingid"
        assert isinstance(response_json['bookingid'], int), "bookingid должен быть числом"
        assert response_json['booking']['firstname'] == booking_data['firstname'], "firstname не совпадает с ожидаемым"
        assert response_json['booking']['lastname'] == booking_data['lastname'], "lastname не совпадает с ожидаемым"
        assert response_json['booking']['totalprice'] == booking_data['totalprice'], "totalprice не совпадает с ожидаемым"
        assert response_json['booking']['depositpaid'] == booking_data['depositpaid'], "depositpaid не совпадает с ожидаемым"
        assert response_json['booking']['bookingdates']['checkin'] == booking_data['bookingdates']['checkin'], "checkin не совпадает с ожидаемым"
        assert response_json['booking']['bookingdates']['checkout'] == booking_data['bookingdates']['checkout'], "checkout не совпадает с ожидаемым"
        assert response_json['booking']['additionalneeds'] == booking_data['additionalneeds'], "additionalneeds не совпадает с ожидаемым"

@allure.feature('Test creating Booking')
@allure.story('Positive: Creating booking with custom data')
def test_creating_booking_with_custom_data(api_client):
    booking_data = {
        "firstname": "Ivan",
        "lastname": "Ivanovich",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        },
        "additionalneeds": "Dinner"
    }

    response = api_client.create_booking(booking_data, status_code=200)
    response_json = response.json()

    try:
        BookingResponse(**response_json)
    except ValidationError as e:
        raise ValidationError(f"Response validation failed: {e}")

    assert response_json['booking']['firstname'] == booking_data['firstname'], "firstname не совпадает с ожидаемым"
    assert response_json['booking']['lastname'] == booking_data['lastname'], "lastname не совпадает с ожидаемым"
    assert response_json['booking']['totalprice'] == booking_data['totalprice'], "totalprice не совпадает с ожидаемым"
    assert response_json['booking']['depositpaid'] == booking_data['depositpaid'], "depositpaid не совпадает с ожидаемым"
    assert response_json['booking']['bookingdates']['checkin'] == booking_data['bookingdates']['checkin'], "checkin не совпадает с ожидаемым"
    assert response_json['booking']['bookingdates']['checkout'] == booking_data['bookingdates']['checkout'], "checkout не совпадает с ожидаемым"
    assert response_json['booking']['additionalneeds'] == booking_data['additionalneeds'], "additionalneeds не совпадает с ожидаемым"

@allure.feature('Test creating Booking')
@allure.story('Negative: Creating booking with empty data')
def test_creating_booking_with_empty_data(api_client):
    booking_data = {
    }

    response = api_client.create_booking(booking_data,status_code=500)

    with allure.step("Проверка статуса ответа"):
        assert response.status_code == 500, f"Ожидался статус 500, получен {response.status_code}"




