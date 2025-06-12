"""Config flow для интеграции КСК."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlowWithConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .exceptions import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KSK."""

    VERSION = 1
    reauth_entry: ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Проверяем данные авторизации
                await self._validate_input(user_input)
                
                # Создаем уникальный ID на основе username
                unique_id = user_input[CONF_USERNAME]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                # Создаем запись конфигурации
                return self.async_create_entry(
                    title=f"КСК {user_input[CONF_USERNAME]}",
                    data=user_input,
                )
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Неожиданная ошибка")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _validate_input(self, data: dict[str, Any]) -> None:
        """Проверка данных авторизации."""
        username = data[CONF_USERNAME]
        password = data[CONF_PASSWORD]
        
        if not username or not password:
            raise InvalidAuth("Не указаны логин или пароль")
        
        # Проверяем, что username состоит из цифр (номер лицевого счета)
        if not username.isdigit():
            raise InvalidAuth("Логин должен быть номером лицевого счета (только цифры)")
        
        # Для полной проверки можно было бы запустить браузерную авторизацию,
        # но это займет много времени. Ограничимся базовой проверкой.
        _LOGGER.info("Данные авторизации КСК прошли базовую проверку")
        
        # В реальной проверке здесь был бы запуск браузерной автоматизации,
        # но мы делаем это позже в координаторе для экономии времени

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle reauthorization request from KSK."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication with KSK."""
        errors: dict[str, str] = {}

        if user_input:
            assert self.reauth_entry is not None
            password = user_input[CONF_PASSWORD]
            data = {
                CONF_USERNAME: self.reauth_entry.data[CONF_USERNAME],
                CONF_PASSWORD: password,
            }

            try:
                await self._validate_input(data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    self.reauth_entry,
                    data={
                        **self.reauth_entry.data,
                        CONF_PASSWORD: password,
                    },
                )
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        reauth_schema = vol.Schema({vol.Required(CONF_PASSWORD): str})
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=reauth_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowWithConfigEntry:
        """Create the options flow."""
        return KskOptionsFlowHandler(config_entry)


class KskOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle an options flow for KSK."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        ) 