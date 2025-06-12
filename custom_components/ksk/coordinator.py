"""КСК Account Coordinator - реальное API через браузерную автоматизацию."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import date, datetime
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_BASE_URL,
    API_AUTH_URL,
    API_USER_INFO_URL,
    API_ACCOUNTS_URL,
    API_ACCOUNT_DETAILS_URL,
    API_TRANSMISSION_DETAILS_URL,
    API_CONSUMPTION_HISTORY_URL,
    API_PAYMENT_HISTORY_URL,
    API_METER_HISTORY_URL,
    API_PAYMENT_DETAILS_URL,
    DOMAIN,
    UPDATE_INTERVAL,
)
from .exceptions import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

class KSKDataUpdateCoordinator(DataUpdateCoordinator):
    """Координатор обновления данных КСК."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Инициализация координатора."""
        self.entry = entry
        self.username = entry.data[CONF_USERNAME]
        self.password = entry.data[CONF_PASSWORD]
        self.auth_token = None
        self.session_cookies = {}
        self.account_id = self.username  # Используем username как account_id
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=True
            ),
        )

    def get_all_accounts(self) -> list[dict]:
        """Получение всех лицевых счетов."""
        if not self.data or "accounts" not in self.data:
            return []
        return self.data["accounts"]

    async def _async_update_data(self) -> dict[str, Any]:
        """Получение данных от API КСК."""
        try:
            # Проверяем, есть ли действующий токен
            if not self.auth_token:
                await self._authenticate()
            
            # Получаем данные пользователя
            user_info = await self._get_user_info()
            accounts = await self._get_accounts()
            
            if not accounts:
                raise UpdateFailed("Не найдены лицевые счета")
            
            # Получаем детальную информацию по первому счету
            account_details = await self._get_account_details(self.account_id)
            transmission_details = await self._get_transmission_details(self.account_id)
            
            # Получаем историю
            consumption_history = await self._get_consumption_history(self.account_id)
            payment_history = await self._get_payment_history(self.account_id)
            meter_history = await self._get_meter_history(self.account_id)
            payment_details = await self._get_payment_details(self.account_id)
            
            return {
                "user_info": user_info,
                "accounts": accounts,
                "account_details": account_details,
                "transmission_details": transmission_details,
                "consumption_history": consumption_history,
                "payment_history": payment_history,
                "meter_history": meter_history,
                "payment_details": payment_details,
                "last_update": dt_util.utcnow(),
            }
            
        except InvalidAuth:
            # Сбрасываем токен и пробуем заново
            self.auth_token = None
            self.session_cookies = {}
            raise ConfigEntryAuthFailed("Ошибка авторизации КСК")
        except Exception as err:
            _LOGGER.error("Ошибка получения данных КСК: %s", err)
            raise UpdateFailed(f"Ошибка получения данных: {err}")

    async def _authenticate(self) -> None:
        """Авторизация через браузерную автоматизацию."""
        try:
            _LOGGER.info("Запуск браузерной авторизации КСК...")
            
            # Импортируем selenium только при необходимости
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
            except ImportError:
                raise CannotConnect("Selenium не установлен. Установите: apt install python3-selenium")
            
            # Настройки Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Открываем страницу авторизации
                driver.get("https://svet.kaluga.ru/auth")
                await asyncio.sleep(3)
                
                # Находим поля и авторизуемся
                login_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                
                login_field.send_keys(self.username)
                password_field.send_keys(self.password)
                
                # Отправляем форму
                form = driver.find_element(By.TAG_NAME, "form")
                form.submit()
                
                await asyncio.sleep(5)
                
                # Извлекаем cookies
                cookies = driver.get_cookies()
                for cookie in cookies:
                    self.session_cookies[cookie['name']] = cookie['value']
                
                # Ищем токен в cookies
                if 'token' in self.session_cookies:
                    self.auth_token = self.session_cookies['token']
                    _LOGGER.info("Токен авторизации получен из cookies")
                else:
                    # Анализируем сетевые запросы для поиска токена
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            if message['message']['method'] == 'Network.requestWillBeSent':
                                request = message['message']['params']['request']
                                headers = request.get('headers', {})
                                if 'authorization' in headers:
                                    auth_header = headers['authorization']
                                    if auth_header.startswith('Bearer '):
                                        self.auth_token = auth_header.replace('Bearer ', '')
                                        _LOGGER.info("Токен авторизации получен из заголовков")
                                        break
                        except:
                            continue
                
                if not self.auth_token:
                    raise InvalidAuth("Не удалось получить токен авторизации")
                
                _LOGGER.info("Авторизация КСК успешна")
                
            finally:
                driver.quit()
                
        except Exception as err:
            _LOGGER.error("Ошибка авторизации КСК: %s", err)
            raise InvalidAuth(f"Ошибка авторизации: {err}")

    def _get_auth_headers(self) -> dict[str, str]:
        """Получение заголовков авторизации."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Origin': 'https://svet.kaluga.ru',
            'Referer': f'https://svet.kaluga.ru/{self.account_id}'
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        return headers

    async def _make_request(self, url: str, method: str = "GET", data: dict = None) -> dict:
        """Выполнение HTTP запроса к API КСК."""
        session = async_get_clientsession(self.hass)
        headers = self._get_auth_headers()
        
        # Добавляем cookies к сессии
        if self.session_cookies:
            cookie_header = "; ".join([f"{k}={v}" for k, v in self.session_cookies.items()])
            headers['Cookie'] = cookie_header
        
        try:
            if method == "POST":
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    if response.status == 401:
                        raise InvalidAuth("Токен авторизации недействителен")
                    response.raise_for_status()
                    return await response.json()
            else:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 401:
                        raise InvalidAuth("Токен авторизации недействителен")
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Ошибка HTTP запроса к %s: %s", url, err)
            raise CannotConnect(f"Ошибка подключения: {err}")

    async def _get_user_info(self) -> dict:
        """Получение информации о пользователе."""
        url = f"{API_BASE_URL}{API_USER_INFO_URL}"
        return await self._make_request(url)

    async def _get_accounts(self) -> list:
        """Получение списка лицевых счетов."""
        url = f"{API_BASE_URL}{API_ACCOUNTS_URL}"
        return await self._make_request(url)

    async def _get_account_details(self, account_id: str) -> dict:
        """Получение детальной информации по лицевому счету."""
        url = f"{API_BASE_URL}{API_ACCOUNT_DETAILS_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_transmission_details(self, account_id: str) -> dict:
        """Получение деталей передачи данных."""
        url = f"{API_BASE_URL}{API_TRANSMISSION_DETAILS_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_consumption_history(self, account_id: str) -> list:
        """Получение истории потребления."""
        url = f"{API_BASE_URL}{API_CONSUMPTION_HISTORY_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_payment_history(self, account_id: str) -> list:
        """Получение истории платежей."""
        url = f"{API_BASE_URL}{API_PAYMENT_HISTORY_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_meter_history(self, account_id: str) -> list:
        """Получение истории показаний счетчика."""
        url = f"{API_BASE_URL}{API_METER_HISTORY_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_payment_details(self, account_id: str) -> dict:
        """Получение деталей платежа."""
        url = f"{API_BASE_URL}{API_PAYMENT_DETAILS_URL.format(account_id=account_id)}"
        return await self._make_request(url) 