"""Constants for the КСК integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "ksk"

ATTRIBUTION: Final = "Данные получены от Калужской Сбытовой Компании"
MANUFACTURER: Final = "Калужская Сбытовая Компания"
MODEL: Final = "КСК Калуга Электроснабжение"

# App constants
APP_VERSION: Final = {"КСК": "3.0.3"}
MOBILE_APP_NAME: Final = "КСК"

API_TIMEOUT: Final = 30
API_MAX_TRIES: Final = 3
API_RETRY_DELAY: Final = 10
UPDATE_HOUR_BEGIN: Final = 1
UPDATE_HOUR_END: Final = 5
UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=30)

REQUEST_REFRESH_DEFAULT_COOLDOWN = 5

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

CONF_ACCOUNT: Final = "account"
CONF_DATA: Final = "data"
CONF_LINK: Final = "link"
CONF_ACCOUNTS: Final = "accounts"
CONF_RESULT: Final = "result"
CONF_INFO: Final = "info"
CONF_PAYMENT: Final = "payment"
CONF_READINGS: Final = "readings"
CONF_AUTO_UPDATE: Final = "auto_update"

# РЕАЛЬНЫЕ API URLs - ОБНОВЛЕНО ПО РЕЗУЛЬТАТАМ ТЕСТИРОВАНИЯ
API_BASE_URL: Final = "https://svet.kaluga.ru/test7/service"
MAIN_SITE_URL: Final = "https://svet.kaluga.ru"
CONFIGURATION_URL: Final = "https://svet.kaluga.ru/auth"

# API Endpoints
API_AUTH_URL: Final = "/auth/sign-in"
API_USER_INFO_URL: Final = "/api/profile/user-info"
API_ACCOUNTS_URL: Final = "/api/profile/accounts/"
API_ACCOUNT_DETAILS_URL: Final = "/api/profile/account/{account_id}"
API_TRANSMISSION_DETAILS_URL: Final = "/api/profile/transmission-details/{account_id}"
API_METER_HISTORY_URL: Final = "/history/meters/{account_id}"
API_PAYMENT_DETAILS_URL: Final = "/api/pay/paymentDetails/{account_id}"
API_TIME_URL: Final = "/service/api/service/time"

FORMAT_DATE_SHORT_YEAR: Final = "%d.%m.%y"
FORMAT_DATE_FULL_YEAR: Final = "%d.%m.%Y"

ATTR_LABEL: Final = "Label"

REFRESH_TIMEOUT = timedelta(minutes=10)
ATTR_VALUE: Final = "value"
ATTR_STATUS: Final = "status"
ATTR_EMAIL: Final = "email"
ATTR_COUNTER: Final = "counter"
ATTR_MESSAGE: Final = "message"
ATTR_SENT: Final = "sent"
ATTR_COORDINATOR: Final = "coordinator"
ATTR_READINGS: Final = "readings"
ATTR_BALANCE: Final = "balance"
SERVICE_REFRESH: Final = "refresh"
SERVICE_SEND_READINGS = "send_readings"
SERVICE_GET_BILL: Final = "get_bill"
ACTION_TYPE_SEND_READINGS: Final = "send_readings"
ACTION_TYPE_BILL: Final = "get_bill"
ACTION_TYPE_REFRESH: Final = "refresh"
ATTR_LSPU_INFO: Final = "lspu_info"
ATTR_ELS_INFO: Final = "els_info"
ATTR_ELS = "els"
ATTR_IS_ELS = "is_els"
ATTR_LSPU_INFO_GROUP = "lspuInfoGroup"
ATTR_COUNTERS: Final = "counters"
ATTR_ALIAS: Final = "alias"
ATTR_LAST_UPDATE_TIME: Final = "last_update_time"
ATTR_JNT_ACCOUNT_NUM: Final = "jntAccountNum"
ATTR_UUID: Final = "uuid"
ATTR_SERIAL_NUM: Final = "serialNumber"
ATTR_MODEL: Final = "model"
ATTR_NAME: Final = "name"
ATTR_ACCOUNT_ID: Final = "accountId"

# Configuration and options
CONF_ACCOUNT_ID: Final = "account_id"
CONF_PHONE_NUMBER: Final = "phone_number"

# Defaults
DEFAULT_NAME: Final = "КСК"
DEFAULT_AUTO_UPDATE: Final = True

# API
API_LOGIN_URL: Final = f"{API_BASE_URL}/auth"
API_MAIN_URL: Final = f"{API_BASE_URL}/main"
API_SERVICE_URL: Final = f"{API_BASE_URL}/service"

# Coordinator
COORDINATOR: Final = "coordinator"

# Sensors
SENSOR_TYPES: Final = {
    "balance": {
        "name": "Баланс",
        "key": "balance",
        "icon": "mdi:currency-rub",
        "unit": "руб",
        "device_class": "monetary",
        "state_class": "total",
    },
    "last_payment": {
        "name": "Последний платеж",
        "key": "last_payment",
        "icon": "mdi:calendar-clock",
        "unit": None,
        "device_class": "timestamp",
        "state_class": None,
    },
    "debt": {
        "name": "Задолженность",
        "key": "debt",
        "icon": "mdi:alert-circle",
        "unit": "руб",
        "device_class": "monetary",
        "state_class": "total",
    },
    "current_readings": {
        "name": "Текущие показания",
        "key": "current_readings",
        "icon": "mdi:gauge",
        "unit": "кВт⋅ч",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "previous_readings": {
        "name": "Предыдущие показания",
        "key": "previous_readings",
        "icon": "mdi:gauge",
        "unit": "кВт⋅ч",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "consumption": {
        "name": "Потребление",
        "key": "consumption",
        "icon": "mdi:flash",
        "unit": "кВт⋅ч",
        "device_class": "energy",
        "state_class": "total",
    },
}

# Buttons
BUTTON_TYPES: Final = {
    "update_data": {
        "name": "Обновить данные",
        "key": "update_data",
        "icon": "mdi:refresh",
    },
    "submit_readings": {
        "name": "Подать показания",
        "key": "submit_readings",
        "icon": "mdi:upload",
    },
} 