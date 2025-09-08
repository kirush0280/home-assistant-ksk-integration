[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

![КСК Калуга logo](images/logo.png)

# Home Assistant интеграция КСК (Калужская Сбытовая Компания)

Интеграция для Home Assistant для работы с личным кабинетом Калужской Сбытовой Компании (электроснабжение).

[🔗 **Официальный сайт КСК**](https://svet.kaluga.ru) 

---

## ✨ **Основные возможности**

- 🔌 **Мониторинг электросчетчиков** - получение актуальных данных
- 📊 **Просмотр показаний и задолженности** - контроль потребления и платежей
- 🏠 **Поддержка нескольких лицевых счетов** - квартира, дача, гараж в одной интеграции
- 📝 **Отправка показаний счетчиков** - автоматическая передача данных
- 🧾 **Получение счетов на оплату** - загрузка документов
- ⚡ **Поддержка многотарифного учета** - день/ночь/пик
- 🚀 **Автоматизация и уведомления** - настройка сценариев

---

## 📋 **История изменений**

📝 **Все обновления и изменения** документируются в **[CHANGELOG.md](CHANGELOG.md)**

Последняя версия поддерживает:
- 🏠 **Несколько лицевых счетов** в одной учетной записи
- 📱 **Отдельные устройства** для каждого лицевого счета
- ⚡ **Оптимизированную производительность** без лишних запросов
- 🔄 **Обратную совместимость** с существующими настройками

---

## 📦 **Установка**

### Через HACS (Рекомендуется)

**Способ 1.** [![Открыть репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kirush0280&repository=home-assistant-ksk-integration&category=integration) → Установить

**Способ 2.** Вручную через HACS:
1. Откройте HACS в Home Assistant  
2. Перейдите в **Integrations**
3. Нажмите **⋮** → **Custom repositories**
4. Добавьте URL: `https://github.com/kirush0280/home-assistant-ksk-integration`
5. Выберите категорию: **Integration**
6. Нажмите **Add** → **Install**
7. Перезагрузите Home Assistant

### Ручная установка

1. Скопируйте папку `custom_components/ksk` в директорию `custom_components` вашего Home Assistant
2. Перезагрузите Home Assistant
3. Добавьте интеграцию через UI

---

## ⚙️ **Настройка**

**Настройки** → **Устройства и службы** → **Интеграции** → [![Добавить интеграцию](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ksk) → Поиск **КСК Калуга**

или нажмите:

[![Добавить интеграцию КСК](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ksk)

### Данные для входа:
- **Номер лицевого счета** (например: 12345678)
- **Пароль** от личного кабинета [КСК](https://svet.kaluga.ru/auth)

---

## 📊 **Доступные датчики**

Интеграция автоматически создает все доступные сенсоры для каждого лицевого счета:

> 🏠 **Множественные лицевые счета:** Если у вас несколько объектов (квартира, дача, гараж), каждый будет представлен отдельным устройством со своими датчиками.

### 💰 **Финансовые данные**
- `sensor.ksk_12345678_balance` - Баланс лицевого счета
- `sensor.ksk_12345678_penalty` - Начисленные пени
- `sensor.ksk_12345678_last_payment` - Последний платеж

### ⚡ **Показания счетчика**
- `sensor.ksk_12345678_readings_day` - Показания (день)
- `sensor.ksk_12345678_readings_night` - Показания (ночь)
- `sensor.ksk_12345678_tariff_day` - Тариф (день)
- `sensor.ksk_12345678_tariff_night` - Тариф (ночь)

### 📈 **Потребление**
- `sensor.ksk_12345678_monthly_consumption` - Месячное потребление
- `sensor.ksk_12345678_average_consumption` - Среднее потребление

*Замените 12345678 на ваш номер лицевого счета*

### 🏠 **Пример для нескольких лицевых счетов**

Если у вас есть квартира (12345678) и дача (87654321), интеграция создаст:
- **Устройство 1:** КСК 12345678 с сенсорами `sensor.ksk_12345678_*`
- **Устройство 2:** КСК 87654321 с сенсорами `sensor.ksk_87654321_*`

---

## 🚀 **Автоматизация**

### Уведомление о задолженности

```yaml
automation:
  - alias: "КСК: Уведомление о задолженности"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ksk_12345678_balance
        below: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Задолженность по электричеству"
          message: "Баланс: {{ states('sensor.ksk_12345678_balance') }} ₽"
```

### Еженедельная проверка показаний

```yaml
automation:
  - alias: "КСК: Еженедельная проверка"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: ksk.refresh
        target:
          device_id: !device_id "КСК Account 12345678"
```

### График потребления

```yaml
type: history-graph
title: "КСК: Потребление"
entities:
  - sensor.ksk_12345678_monthly_consumption
  - sensor.ksk_12345678_average_consumption
hours_to_show: 720
```

### Автоматизация для нескольких объектов

```yaml
automation:
  - alias: "КСК: Уведомление о любой задолженности"
    trigger:
      - platform: numeric_state
        entity_id: 
          - sensor.ksk_12345678_balance  # Квартира
          - sensor.ksk_87654321_balance  # Дача
        below: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Задолженность по электричеству"
          message: >
            {% set account = trigger.entity_id.split('_')[1] %}
            {% set object_name = 'Квартира' if account == '12345678' else 'Дача' %}
            {{ object_name }}: {{ trigger.to_state.state }} ₽
```

---

## 🛠️ **Доступные сервисы**

### `ksk.refresh` - Обновить данные
Принудительное обновление всех данных интеграции.

### `ksk.get_bill` - Получить счет
Загружает счет за указанную дату.
**Параметры:**
- `device_id` - ID устройства КСК
- `date` - Дата в формате YYYY-MM-DD

### `ksk.send_readings` - Передать показания
Отправляет показания счетчика в КСК.

---

## 🐛 **Диагностика и отладка**

### Включение логов

Добавьте в `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.ksk: debug
```

### Типичные проблемы

**Ошибка авторизации:**
- Проверьте правильность номера лицевого счета и пароля
- Убедитесь, что вы можете войти на [сайт КСК](https://svet.kaluga.ru/auth)

**Нет данных от датчиков:**
- Проверьте подключение к интернету
- Перезапустите интеграцию через настройки

---

## 🤝 **Поддержка проекта**

Если интеграция помогла вам, поставьте ⭐ проекту на GitHub!

### Сообщить об ошибке
[📝 Создать Issue](https://github.com/kirush0280/home-assistant-ksk-integration/issues)

### Предложить улучшение  
[💡 Feature Request](https://github.com/kirush0280/home-assistant-ksk-integration/issues/new)

---

## 📄 **Лицензия**

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) для подробностей.

---

## 🔗 **Полезные ссылки**

- [🏠 Home Assistant](https://www.home-assistant.io/)
- [📦 HACS](https://hacs.xyz/)
- [⚡ Официальный сайт КСК](https://svet.kaluga.ru)
- [📋 Личный кабинет КСК](https://svet.kaluga.ru/auth)

---

<p align="center">
  <sub>Создано с ❤️ для сообщества Home Assistant</sub>
</p>

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/kirush0280/home-assistant-ksk-integration.svg?style=for-the-badge
[commits]: https://github.com/kirush0280/home-assistant-ksk-integration/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/kirush0280/home-assistant-ksk-integration.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/kirush0280/home-assistant-ksk-integration.svg?style=for-the-badge
[releases]: https://github.com/kirush0280/home-assistant-ksk-integration/releases
