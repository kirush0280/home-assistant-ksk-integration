"""КСК Sensor definitions - расширенная версия для всех данных API."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import KSKDataUpdateCoordinator


class KSKBaseSensorEntity(CoordinatorEntity[KSKDataUpdateCoordinator], SensorEntity):
    """Базовый класс для сенсоров КСК."""

    def __init__(
        self,
        coordinator: KSKDataUpdateCoordinator,
        account_data: dict,
        sensor_key: str,
        name: str,
        icon: str | None = None,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Инициализация сенсора."""
        super().__init__(coordinator)
        
        self.account_data = account_data
        self.account_number = account_data.get("number", "unknown")
        
        # Уникальный ID
        self._attr_unique_id = f"ksk_{self.account_number}_{sensor_key}"
        
        # Название
        self._attr_name = f"{name} ({self.account_number})"
        
        # Атрибуты устройства
        if icon:
            self._attr_icon = icon
        if unit:
            self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class
        if entity_category:
            self._attr_entity_category = entity_category
        
        # Информация об устройстве
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.account_number)},
            "name": f"КСК {self.account_number}",
            "manufacturer": "Калужская Сбытовая Компания",
            "model": account_data.get("meterName", "Электросчетчик"),
            "sw_version": account_data.get("meterNumber"),
        }

    @property
    def available(self) -> bool:
        """Доступность сенсора."""
        return self.coordinator.data is not None
    
    def get_account_details(self, key: str = None):
        """Получение детальных данных для конкретного лицевого счета."""
        if not self.coordinator.data or "accounts_details" not in self.coordinator.data:
            return {} if key else None
            
        account_details = self.coordinator.data["accounts_details"].get(self.account_number, {})
        
        if key:
            return account_details.get(key, {})
        return account_details


# =============================================================================
# ОСНОВНЫЕ СЕНСОРЫ ЛИЦЕВОГО СЧЕТА
# =============================================================================

class KSKAccountSensor(KSKBaseSensorEntity):
    """Сенсор лицевого счета."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "account",
            "Лицевой счет",
            icon="mdi:identifier",
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    @property
    def native_value(self) -> str:
        """Значение сенсора."""
        return self.account_number

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        return {
            "address": self.account_data.get("address"),
            "meter_name": self.account_data.get("meterName"),
            "meter_number": self.account_data.get("meterNumber"),
            "zones_count": self.account_data.get("zonesCount", 1),
            "has_invoice": self.account_data.get("hasInvoice", False),
            "can_sbp": self.account_data.get("canSBP", False),
            "is_before_tech": self.account_data.get("isBeforeTech", False),
        }


class KSKUserInfoSensor(KSKBaseSensorEntity):
    """Сенсор информации о пользователе."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "user_info",
            "Информация о пользователе",
            icon="mdi:account",
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    @property
    def native_value(self) -> str:
        """Значение сенсора."""
        user_info = self.coordinator.data.get("user_info", {})
        return user_info.get("name", "Неизвестно")

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        user_info = self.coordinator.data.get("user_info", {})
        return {
            "email": user_info.get("email"),
            "phone": user_info.get("phone"),
            "full_name": user_info.get("fullName"),
        }


# =============================================================================
# ФИНАНСОВЫЕ СЕНСОРЫ
# =============================================================================

class KSKBalanceSensor(KSKBaseSensorEntity):
    """Сенсор задолженности."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "balance",
            "Задолженность",
            icon="mdi:currency-rub",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float:
        """Значение сенсора."""
        balance = self.account_data.get("balance", {})
        return balance.get("debt", 0.0)

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        balance = self.account_data.get("balance", {})
        return {
            "duty": balance.get("duty", 0.0),
            "sud": balance.get("sud", 0.0),
            "payment_disconnection": balance.get("paymentDisconnection", 0.0),
            "penalty": balance.get("penalty", 0.0),
            "accepted": balance.get("accepted", 0),
            "processing": balance.get("processing", 0),
        }


class KSKPenaltySensor(KSKBaseSensorEntity):
    """Сенсор пени."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "penalty",
            "Пени",
            icon="mdi:alert-circle",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float:
        """Значение сенсора."""
        balance = self.account_data.get("balance", {})
        return balance.get("penalty", 0.0)


class KSKAcceptedPaymentsSensor(KSKBaseSensorEntity):
    """Сенсор принятых платежей."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "accepted_payments",
            "Принятые платежи",
            icon="mdi:check-circle",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float:
        """Значение сенсора."""
        balance = self.account_data.get("balance", {})
        return balance.get("accepted", 0.0)


class KSKProcessingPaymentsSensor(KSKBaseSensorEntity):
    """Сенсор платежей в обработке."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "processing_payments",
            "Платежи в обработке",
            icon="mdi:clock-outline",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float:
        """Значение сенсора."""
        balance = self.account_data.get("balance", {})
        return balance.get("processing", 0.0)


# =============================================================================
# СЕНСОРЫ СЧЕТЧИКА И ПОКАЗАНИЙ
# =============================================================================

class KSKMeterSensor(KSKBaseSensorEntity):
    """Сенсор счетчика."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "meter",
            "Счетчик",
            icon="mdi:counter",
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    @property
    def native_value(self) -> str:
        """Значение сенсора."""
        return self.account_data.get("meterName", "Неизвестно")

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        return {
            "meter_number": self.account_data.get("meterNumber"),
            "zones_count": self.account_data.get("zonesCount", 1),
            "is_before_tech": self.account_data.get("isBeforeTech", False),
        }


class KSKReadingsSensor(KSKBaseSensorEntity):
    """Сенсор показаний счетчика."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict, zone_name: str = "основной") -> None:
        self.zone_name = zone_name
        super().__init__(
            coordinator,
            account_data,
            f"readings_{zone_name}",
            f"Показания ({zone_name})",
            icon="mdi:counter",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        # Получаем показания из transmission данных для конкретного счета
        transmission = self.get_account_details("transmission_details")
        last_indications = transmission.get("lastIndications", [])
        
        # Для основной зоны берем первое значение
        if self.zone_name == "основной" and last_indications:
            try:
                return float(last_indications[0])
            except (ValueError, IndexError):
                pass
                
        # Ищем в zones из transmission данных (они более актуальные)
        zones = transmission.get("zones", [])
        for zone in zones:
            if zone.get("name") == self.zone_name:
                indication = zone.get("indication")
                if indication:
                    try:
                        return float(indication)
                    except ValueError:
                        pass
        
        # Если не найдено в transmission, ищем в базовых данных счета
        zones = self.account_data.get("zones", [])
        for zone in zones:
            if zone.get("name") == self.zone_name:
                indication = zone.get("indication")
                if indication:
                    try:
                        return float(indication)
                    except ValueError:
                        pass
        
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        transmission = self.get_account_details("transmission_details")
        zone_info = None
        
        # Ищем информацию о зоне в transmission данных
        zones = transmission.get("zones", [])
        for zone in zones:
            if zone.get("name") == self.zone_name:
                zone_info = zone
                break
        
        # Если не найдено, ищем в базовых данных счета
        if not zone_info:
            zones = self.account_data.get("zones", [])
            for zone in zones:
                if zone.get("name") == self.zone_name:
                    zone_info = zone
                    break
        
        attrs = {
            "last_period": transmission.get("lastPeriod"),
            "current_period": transmission.get("period"),
            "zone_name": self.zone_name,
            "account_number": self.account_number,
        }
        
        if zone_info:
            attrs["tariff"] = zone_info.get("tariff")
            
        return attrs


class KSKTariffSensor(KSKBaseSensorEntity):
    """Сенсор тарифа."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict, zone_name: str = "основной") -> None:
        self.zone_name = zone_name
        super().__init__(
            coordinator,
            account_data,
            f"tariff_{zone_name}",
            f"Тариф ({zone_name})",
            icon="mdi:currency-rub",
            unit="RUB/kWh",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        zones = self.account_data.get("zones", [])
        for zone in zones:
            if zone.get("name") == self.zone_name:
                return zone.get("tariff")
        
        # Если не найдена зона, берем первый тариф
        tarifs = self.account_data.get("tarifs", [])
        if tarifs:
            return tarifs[0]
            
        return None


class KSKPaymentAmountSensor(KSKBaseSensorEntity):
    """Сенсор суммы к доплате."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "payment_amount",
            "Сумма к доплате",
            icon="mdi:cash-multiple",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        transmission = self.get_account_details("transmission_details")
        return transmission.get("amount")


# =============================================================================
# СЕНСОРЫ ИСТОРИИ
# =============================================================================

class KSKLastConsumptionSensor(KSKBaseSensorEntity):
    """Сенсор последнего потребления."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "last_consumption",
            "Последнее потребление",
            icon="mdi:history",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        consumption_history = self.get_account_details("consumption_history")
        if consumption_history:
            latest = consumption_history[0]
            return latest.get("consumption", 0.0)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        consumption_history = self.get_account_details("consumption_history")
        if consumption_history:
            latest = consumption_history[0]
            return {
                "period": latest.get("period"),
                "amount": latest.get("amount"),
                "date": latest.get("date"),
                "account_number": self.account_number,
            }
        return {"account_number": self.account_number}


class KSKLastPaymentSensor(KSKBaseSensorEntity):
    """Сенсор последнего платежа."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "last_payment",
            "Последний платеж",
            icon="mdi:credit-card",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        payment_history = self.get_account_details("payment_history")
        if payment_history:
            latest = payment_history[0]
            return latest.get("amount", 0.0)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        payment_history = self.get_account_details("payment_history")
        if payment_history:
            latest = payment_history[0]
            return {
                "date": latest.get("date"),
                "method": latest.get("method"),
                "status": latest.get("status"),
                "description": latest.get("description"),
                "account_number": self.account_number,
            }
        return {"account_number": self.account_number}


class KSKMonthlyConsumptionSensor(KSKBaseSensorEntity):
    """Сенсор месячного потребления."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "monthly_consumption",
            "Месячное потребление",
            icon="mdi:calendar-month",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        consumption_history = self.get_account_details("consumption_history")
        current_month = dt_util.now().month
        current_year = dt_util.now().year
        
        for consumption in consumption_history:
            period = consumption.get("period", "")
            if f"{current_month:02d}.{current_year}" in period:
                return consumption.get("consumption", 0.0)
        
        return None


class KSKAverageConsumptionSensor(KSKBaseSensorEntity):
    """Сенсор среднего потребления."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "average_consumption",
            "Среднее потребление",
            icon="mdi:chart-line",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        consumption_history = self.get_account_details("consumption_history")
        if len(consumption_history) >= 3:
            # Берем последние 3 месяца для расчета среднего
            total = sum(item.get("consumption", 0) for item in consumption_history[:3])
            return round(total / 3, 2)
        return None


# =============================================================================
# ТЕХНИЧЕСКИЕ СЕНСОРЫ
# =============================================================================

class KSKLastUpdateSensor(KSKBaseSensorEntity):
    """Сенсор последнего обновления."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "last_update",
            "Последнее обновление",
            icon="mdi:clock",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    @property
    def native_value(self):
        """Значение сенсора."""
        return self.coordinator.data.get("last_update")


class KSKDataFreshnessSensor(KSKBaseSensorEntity):
    """Сенсор свежести данных."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "data_freshness",
            "Свежесть данных",
            icon="mdi:timer",
            unit=UnitOfTime.MINUTES,
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    @property
    def native_value(self) -> int | None:
        """Значение сенсора."""
        last_update = self.coordinator.data.get("last_update")
        if last_update:
            delta = dt_util.now() - last_update
            return int(delta.total_seconds() / 60)
        return None


class KSKPaymentDetailsSensor(KSKBaseSensorEntity):
    """Сенсор деталей платежа."""

    def __init__(self, coordinator: KSKDataUpdateCoordinator, account_data: dict) -> None:
        super().__init__(
            coordinator,
            account_data,
            "payment_details",
            "Детали платежа",
            icon="mdi:receipt",
            unit="RUB",
            device_class=SensorDeviceClass.MONETARY,
        )

    @property
    def native_value(self) -> float | None:
        """Значение сенсора."""
        payment_details = self.get_account_details("payment_details")
        return payment_details.get("amount", 0.0)

    @property
    def extra_state_attributes(self) -> dict:
        """Дополнительные атрибуты."""
        payment_details = self.get_account_details("payment_details")
        return {
            "commission": payment_details.get("commission", 0.0),
            "total_amount": payment_details.get("totalAmount", 0.0),
            "min_amount": payment_details.get("minAmount", 0.0),
            "max_amount": payment_details.get("maxAmount", 0.0),
            "account_number": self.account_number,
        }


# =============================================================================
# НАСТРОЙКА СЕНСОРОВ
# =============================================================================

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка сенсоров КСК."""
    coordinator: KSKDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    
    # Получаем все лицевые счета
    if coordinator.data and "accounts" in coordinator.data:
        accounts = coordinator.data["accounts"]
        
        for account in accounts:
            account_number = account.get("number")
            if not account_number:
                continue
                
            # Основные сенсоры для каждого счета
            entities.extend([
                # Основная информация
                KSKAccountSensor(coordinator, account),
                KSKUserInfoSensor(coordinator, account),
                
                # Финансовые сенсоры
                KSKBalanceSensor(coordinator, account),
                KSKPenaltySensor(coordinator, account),
                KSKAcceptedPaymentsSensor(coordinator, account),
                KSKProcessingPaymentsSensor(coordinator, account),
                KSKPaymentDetailsSensor(coordinator, account),
                
                # Счетчик и показания
                KSKMeterSensor(coordinator, account),
                KSKPaymentAmountSensor(coordinator, account),
                
                # История
                KSKLastConsumptionSensor(coordinator, account),
                KSKLastPaymentSensor(coordinator, account),
                KSKMonthlyConsumptionSensor(coordinator, account),
                KSKAverageConsumptionSensor(coordinator, account),
                
                # Технические
                KSKLastUpdateSensor(coordinator, account),
                KSKDataFreshnessSensor(coordinator, account),
            ])
            
            # Сенсоры показаний и тарифов для каждой зоны
            zones = account.get("zones", [])
            if not zones:
                # Если зон нет, создаем основную зону
                entities.extend([
                    KSKReadingsSensor(coordinator, account, "основной"),
                    KSKTariffSensor(coordinator, account, "основной"),
                ])
            else:
                for zone in zones:
                    zone_name = zone.get("name", "основной")
                    entities.extend([
                        KSKReadingsSensor(coordinator, account, zone_name),
                        KSKTariffSensor(coordinator, account, zone_name),
                    ])

    async_add_entities(entities) 