# Home Assistant Интеграция КСК (Калужская Сбытовая Компания)

Интеграция для Home Assistant для работы с личным кабинетом Калужской Сбытовой Компании (электроснабжение).

## 🔧 **Возможности:**
- Получение данных с электросчетчиков
- Просмотр показаний и задолженности
- Отправка показаний счетчиков
- Получение счетов на оплату
- Поддержка многотарифного учета (день/ночь)

## 📦 **Доступные датчики:**
Интеграция создает все возможные сенсоры для вашего лицевого счета. Ненужные сенсоры можно отключить вручную в настройках Home Assistant (Settings → Entities).

## 🚀 **Возможности для автоматизации**

### Уведомления о задолженности
```yaml
automation:
  - alias: "КСК: Уведомление о задолженности"
    trigger:
      platform: numeric_state
      entity_id: sensor.ksk_XXXXXXXXX_balance
      above: 1000
    action:
      service: notify.telegram
      data:
        message: "Задолженность по КСК: {{ states('sensor.ksk_XXXXXXXXX_balance') }} руб"
```

### Мониторинг потребления
```yaml
automation:
  - alias: "КСК: Высокое потребление"
    trigger:
      platform: numeric_state
      entity_id: sensor.ksk_XXXXXXXXX_monthly_consumption
      above: 500
    action:
      service: notify.mobile_app
      data:
        message: "Высокое потребление в этом месяце: {{ states('sensor.ksk_XXXXXXXXX_monthly_consumption') }} кВт⋅ч"
```

### Напоминание о передаче показаний
```yaml
automation:
  - alias: "КСК: Напоминание о показаниях"
    trigger:
      platform: time
      at: "09:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 25 }}"
    action:
      service: notify.all_devices
      data:
        message: "Не забудьте передать показания счетчика КСК!"
```

## 📊 **Dashboard карточки**

### Финансовая сводка
```yaml
type: entities
title: "КСК: Финансы"
entities:
  - sensor.ksk_XXXXXXXXX_balance
  - sensor.ksk_XXXXXXXXX_penalty
  - sensor.ksk_XXXXXXXXX_accepted_payments
  - sensor.ksk_XXXXXXXXX_processing_payments
```

### Показания и тарифы
```yaml
type: entities
title: "КСК: Показания"
entities:
  - sensor.ksk_XXXXXXXXX_readings_основной
  - sensor.ksk_XXXXXXXXX_tariff_основной
  - sensor.ksk_XXXXXXXXX_consumption
```

### История потребления
```yaml
type: history-graph
title: "КСК: Потребление"
entities:
  - sensor.ksk_XXXXXXXXX_monthly_consumption
  - sensor.ksk_XXXXXXXXX_average_consumption
hours_to_show: 720
```

## 📥 **Установка**
Интеграция устанавливается через HACS (Home Assistant Community Store).

## ⚙️ **Настройка**
Настройка через интерфейс Home Assistant: Settings → Integrations → Add Integration → КСК Калуга

*Замените XXXXXXXXX на ваш номер лицевого счета в примерах выше.* 