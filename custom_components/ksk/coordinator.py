"""КСК Account Coordinator - Исправленная версия с прямыми API вызовами."""
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
    API_METER_HISTORY_URL,
    API_PAYMENT_DETAILS_URL,
    API_PAYMENT_HISTORY_URL,
    DOMAIN,
    UPDATE_INTERVAL,
)
from .exceptions import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

class KSKDataUpdateCoordinator(DataUpdateCoordinator):
    """Координатор обновления данных КСК - Исправленная версия без браузера."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Инициализация координатора."""
        self.entry = entry
        self.username = entry.data[CONF_USERNAME]
        self.password = entry.data[CONF_PASSWORD]
        self.auth_token = None
        self.session_cookies = {}
        self.account_id = self.username
        
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
                await self._authenticate_direct()
            
            # Получаем данные пользователя
            user_info = await self._get_user_info()
            accounts = await self._get_accounts()
            
            if not accounts:
                raise UpdateFailed("Не найдены лицевые счета")
            
            # Получаем детальную информацию по всем лицевым счетам
            accounts_details = {}
            for account in accounts:
                account_id = account.get("number")
                if not account_id:
                    continue
                    
                try:
                    # Получаем детальную информацию по каждому счету
                    account_details = await self._get_account_details(account_id)
                    transmission_details = await self._get_transmission_details(account_id)
                    
                    # Получаем историю показаний счетчика и детали платежа
                    meter_history = await self._get_meter_history(account_id)
                    payment_details = await self._get_payment_details(account_id)
                    
                    # Получаем историю платежей
                    payment_history = await self._get_payment_history(account_id)
                    
                    accounts_details[account_id] = {
                        "account_details": account_details,
                        "transmission_details": transmission_details,
                        "meter_history": meter_history,
                        "payment_details": payment_details,
                        "payment_history": payment_history,
                    }
                    
                except Exception as err:
                    _LOGGER.warning(f"Ошибка получения данных для счета {account_id}: {err}")
                    # Сохраняем пустые данные, чтобы не ломать интеграцию
                    accounts_details[account_id] = {
                        "account_details": {},
                        "transmission_details": {},
                        "meter_history": [],
                        "payment_details": {},
                        "payment_history": [],
                    }
            
            return {
                "user_info": user_info,
                "accounts": accounts,
                "accounts_details": accounts_details,
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

    async def _authenticate_direct(self) -> None:
        """Прямая авторизация через API без браузера."""
        try:
            _LOGGER.info("Запуск прямой авторизации КСК...")
            
            session = async_get_clientsession(self.hass)
            
            # URL для авторизации
            auth_url = f"{API_BASE_URL}{API_AUTH_URL}"
            
            # Заголовки
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Origin': 'https://svet.kaluga.ru',
                'Referer': 'https://svet.kaluga.ru/',
                'Content-Type': 'application/json',
            }
            
            # Пробуем различные форматы данных авторизации
            auth_attempts = [
                # Базовый формат
                {"account": self.username, "password": self.password},
                
                # С district (найдено в анализе API)
                {"account": self.username, "password": self.password, "district": 5},
                {"account": self.username, "password": self.password, "id": 5},
                
                # Формат с умножением на district (найдено в JS коде)
                {"account": str(5 * int(1e8) + int(self.username)), "password": self.password},
                {"account": str(5 * int(1e8) + int(self.username)), "password": self.password, "district": 5},
                
                # Другие районы
                {"account": str(6 * int(1e8) + int(self.username)), "password": self.password, "district": 6},
                {"account": str(7 * int(1e8) + int(self.username)), "password": self.password, "district": 7},
                {"account": str(8 * int(1e8) + int(self.username)), "password": self.password, "district": 8},
            ]
            
            for i, auth_data in enumerate(auth_attempts, 1):
                _LOGGER.debug(f"Попытка авторизации {i}/{len(auth_attempts)}")
                
                try:
                    async with session.post(auth_url, json=auth_data, headers=headers, timeout=30) as response:
                        
                        if response.status == 200:
                            response_data = await response.json()
                            
                            if response_data.get('token'):
                                self.auth_token = response_data['token']
                                _LOGGER.info("Авторизация КСК успешна")
                                
                                # Сохраняем cookies если есть
                                if response.cookies:
                                    for cookie in response.cookies:
                                        self.session_cookies[cookie.key] = cookie.value
                                
                                return
                            elif 'success' in str(response_data).lower():
                                _LOGGER.debug(f"Возможно успешная авторизация: {response_data}")
                                # Пробуем извлечь токен из ответа
                                if 'data' in response_data and isinstance(response_data['data'], dict):
                                    if 'token' in response_data['data']:
                                        self.auth_token = response_data['data']['token']
                                        return
                        
                        elif response.status in [400, 404]:
                            error_data = await response.json()
                            error_msg = error_data.get('message', 'Unknown error')
                            
                            # Если это последняя попытка, выбрасываем исключение
                            if i == len(auth_attempts):
                                if 'not registered' in error_msg:
                                    raise InvalidAuth("Лицевой счет не зарегистрирован в системе")
                                elif 'inconsistent' in error_msg:
                                    raise InvalidAuth("Неверная пара логин/пароль")
                                else:
                                    raise InvalidAuth(f"Ошибка авторизации: {error_msg}")
                        
                        else:
                            _LOGGER.warning(f"Неожиданный статус ответа: {response.status}")
                            
                except Exception as e:
                    _LOGGER.warning(f"Ошибка в попытке авторизации {i}: {e}")
                    if i == len(auth_attempts):
                        raise InvalidAuth(f"Ошибка авторизации: {e}")
                    continue
            
            raise InvalidAuth("Все попытки авторизации исчерпаны")
            
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
            _LOGGER.error("Ошибка HTTP запроса %s: %s", url, err)
            raise UpdateFailed(f"Ошибка запроса к API: {err}")

    # API методы
    async def _get_user_info(self) -> dict:
        """Получение информации о пользователе."""
        url = f"{API_BASE_URL}{API_USER_INFO_URL}"
        return await self._make_request(url)

    async def _get_accounts(self) -> list[dict]:
        """Получение списка лицевых счетов."""
        url = f"{API_BASE_URL}{API_ACCOUNTS_URL}"
        result = await self._make_request(url)
        return result if isinstance(result, list) else [result]

    async def _get_account_details(self, account_id: str) -> dict:
        """Получение детальной информации по лицевому счету."""
        url = f"{API_BASE_URL}{API_ACCOUNT_DETAILS_URL.format(account_id=account_id)}"
        return await self._make_request(url)

    async def _get_transmission_details(self, account_id: str) -> dict:
        """Получение деталей передачи показаний."""
        url = f"{API_BASE_URL}{API_TRANSMISSION_DETAILS_URL.format(account_id=account_id)}"
        return await self._make_request(url)


    async def _get_meter_history(self, account_id: str) -> list[dict]:
        """Получение истории показаний счетчиков."""
        try:
            url = f"{API_BASE_URL}{API_METER_HISTORY_URL.format(account_id=account_id)}"
            return await self._make_request(url)
        except:
            return []

    async def _get_payment_details(self, account_id: str) -> dict:
        """Получение деталей для платежа."""
        try:
            url = f"{API_BASE_URL}{API_PAYMENT_DETAILS_URL.format(account_id=account_id)}"
            return await self._make_request(url)
        except:
            return {}

    async def _get_payment_history(self, account_id: str) -> list[dict]:
        """Получение истории платежей по лицевому счету."""
        try:
            url = f"{API_BASE_URL}{API_PAYMENT_HISTORY_URL.format(account_id=account_id)}"
            result = await self._make_request(url)
            return result if isinstance(result, list) else []
        except Exception as err:
            _LOGGER.warning(f"Не удалось получить историю платежей для счета {account_id}: {err}")
            return []

    # Дополнительные методы для интеграции
    async def submit_meter_readings(self, readings: dict) -> bool:
        """Отправка показаний счетчиков."""
        try:
            url = f"{API_BASE_URL}/api/profile/send-meter-lk"
            data = {
                "account": self.account_id,
                "readings": readings,
                "period": datetime.now().strftime("%Y-%m")
            }
            
            result = await self._make_request(url, "POST", data)
            return result.get('success', False)
            
        except Exception as err:
            _LOGGER.error("Ошибка отправки показаний: %s", err)
            return False

    async def get_payment_link(self, amount: float) -> str:
        """Получение ссылки на оплату."""
        try:
            url = f"{API_BASE_URL}/api/pay/make-paymnet"  # Да, в API опечатка "paymnet"
            data = {
                "accountNumber": self.account_id,
                "amount": str(amount),
                "deepLink": f"https://svet.kaluga.ru/{self.account_id}",
                "osType": ""
            }
            
            result = await self._make_request(url, "POST", data)
            return result.get('formUrl', '')
            
        except Exception as err:
            _LOGGER.error("Ошибка получения ссылки на оплату: %s", err)
            return ""

    async def get_current_time(self) -> datetime:
        """Получение текущего времени с сервера."""
        try:
            url = f"{API_BASE_URL}/api/service/time"
            result = await self._make_request(url)
            if 'currentTime' in result:
                time_str = result['currentTime'].split('.')[0]  # Убираем миллисекунды
                return datetime.fromisoformat(time_str)
            return dt_util.utcnow()
        except:
            return dt_util.utcnow()