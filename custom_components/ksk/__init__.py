"""Интеграция КСК для Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import KSKDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Настройка интеграции КСК."""
    _LOGGER.info("Настройка интеграции КСК для аккаунта: %s", entry.data.get("username"))
    
    # Создаем координатор данных
    coordinator = KSKDataUpdateCoordinator(hass, entry)
    
    # Выполняем первоначальное обновление данных
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Ошибка при первоначальной настройке КСК: %s", err)
        raise ConfigEntryNotReady(f"Не удалось подключиться к КСК: {err}") from err
    
    # Сохраняем координатор в hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Настраиваем платформы
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Интеграция КСК успешно настроена")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Выгрузка интеграции КСК."""
    _LOGGER.info("Выгрузка интеграции КСК")
    
    # Выгружаем платформы
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Удаляем данные из hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    return unload_ok 