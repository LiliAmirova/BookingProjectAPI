import requests
import os # модуль для работы с файлами
from dotenv import load_dotenv
from core.setting.environments import Environment # среда
from core.clients.endpoints import Endpoints
from core.setting.config import Users, Timeouts
from requests.auth import HTTPBasicAuth
import allure
import pytest

load_dotenv() # чтобы прогружались все актуальные переменные, которые в файле dotenv

class APIClient:   # обертка для фреймворка requests
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f"Unsupported environment value: {environment_str}") # Неподдерживаемое значение среды

        self.base_url = self.get_base_url(environment)
        # self.session установить httpx-соединение и не закрывать сессию и выполнить несколько запросов
        # это помогает сократить расходы на подключение
        # можно без сессии:
        #self.headers = {
        #    'Content-Type': 'application/json'
        #}
        self.session = requests.Session()
        self.session.headers = {
            'Accept': 'application/json',  # Ожидаем JSON в ответе
            'Content-Type': 'application/json', # Отправляем JSON
            'Cookie': 'token'  # сама добавила для функции auth
        }

    def get_base_url(self, environment:Environment) -> str:
        if environment == Environment.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Environment.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment: {environment}") # среда не поддерживается

    # def get(self, endpoint, params=None, status_code=200):
    #     url = self.base_url + endpoint
    #     response = requests.get(url, headers=self.headers, params=params)
    #     if status_code:
    #         assert response.status_code == status_code
    #     return response.json()
    #
    # def post(self, endpoint, data=None, status_code=200):
    #     url = self.base_url + endpoint
    #     response = requests.post(url, headers=self.headers, json=data)
    #     # ранее было response = httpx.post(BASE_URL + LOGIN_USER, json=users_data)
    #     if status_code:
    #         assert response.status_code == status_code
    #     return response.json()

    # функция: проверка доступности и работоспособности API
    def ping(self):
        with allure.step('Ping api client'):
            url = f"{self.base_url}/{Endpoints.PING_ENDPOINT.value}"
            response = self.session.get(url)
            response.raise_for_status()  # проверка http ошибки
        with allure.step('Assert status code'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"  # если получили другой код статус, то ожидали, но получили такой-то код
        return response.status_code

    # получение токена
    def auth(self):
        with allure.step('Getting authenticate'):  # получаем аутентификацию
            url = f"{self.base_url}/{Endpoints.AUTH_ENDPOINT.value}"  # формируем переменную url
            payload = {"username": Users.USERNAME.value, "password": Users.PASSWORD.value}  # передаем тело в запросе POST
            response = self.session.post(url, json=payload, timeout=Timeouts.TIMEOUT.value)
            response.raise_for_status()  # доп проверка: проверяем, что ошибки http нет
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        token = response.json().get("token")  # полученный токен из ответа положили в переменную token
        with allure.step('GUpdating header with authorization'):  # обновляем header с записью авторизацией
            # self.session.headers.update({"Authorization": f"Bearer {token}"})  # из строки 23 (добавляем заголовок Authorization)
            self.session.headers.update({"Cookie": f"token {token}"})


    # GetBooking
    def get_booking_by_id(self, booking_id):
        with allure.step(f'Отправляем запрос по адресу/Getting object with  bookings by id: {self.base_url + Endpoints.BOOKING_ENDPOINT.value + booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.get(url, timeout=Timeouts.TIMEOUT)
            response.raise_for_status()  # получение статус кода, а именно нет ли какой-то определенной  http ошибки
        with allure.step(f'Проверяем код ответа/Checking status code: '):
            assert response.status_code == 200, f"Ожидали статус код 200, но получили/Expected status 200 but got {response.status_code}"
        return  response.json()

    # Delete - используется авторизация
    def delete_booking(self, booking_id):
        with allure.step('Deleting booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            # HTTPBasicAuth происходит кодирование полученных логина и пароля в Basic 64 доб-ся в Authorization
            response = self.session.delete(url, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Checking status code:'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"
        return response.status_code == 201

    def create_booking(self,booking_data):
        with allure.step('Creating booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            print("URL:", url)
            print("Request Data:", booking_data)
            response = self.session.post(url, json=booking_data,timeout=10)
            self.session.headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            #response = requests.post(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Checking status code'):
           assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response

    def get_booking_ids(self, params=None):  # params=None передаем значение по умолчанию
        with allure.step('Getting object with booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert  response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return  response.json()

    def update_booking(self, booking_id):
        with allure.step('Updating Booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.put(url, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Checking status code:'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def partial_update_booking(self, booking_id):
        with allure.step('Updating Booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.patch(url, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Checking status code:'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

