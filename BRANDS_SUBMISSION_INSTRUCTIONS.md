# 📋 Инструкция по добавлению логотипа КСК в Home Assistant Brands

## 🎯 Цель
Чтобы логотип КСК корректно отображался в Home Assistant и HACS, необходимо добавить его в официальный репозиторий [home-assistant/brands](https://github.com/home-assistant/brands).

## 📁 Подготовленные файлы
В папке `brands_submission/custom_integrations/ksk/` находятся:
- `icon.png` - иконка 256×256 пикселей  
- `icon@2x.png` - hDPI иконка 512×512 пикселей
- `logo.png` - логотип 256×256 пикселей  
- `logo@2x.png` - hDPI логотип 512×512 пикселей

## 🚀 Пошаговая инструкция

### 1. Форк репозитория
1. Перейдите на https://github.com/home-assistant/brands
2. Нажмите кнопку **Fork** в правом верхнем углу
3. Создайте форк в своем аккаунте

### 2. Клонирование форка
```bash
git clone https://github.com/ВАШ_GITHUB_USERNAME/brands.git
cd brands
```

### 3. Создание ветки для изменений
```bash
git checkout -b add-ksk-integration
```

### 4. Добавление файлов
```bash
# Создаем папку для интеграции КСК
mkdir -p custom_integrations/ksk

# Копируем подготовленные файлы
cp /path/to/your/brands_submission/custom_integrations/ksk/* custom_integrations/ksk/
```

### 5. Коммит изменений
```bash
git add custom_integrations/ksk/
git commit -m "Add КСК (Kaluga Supply Company) integration branding

- Add icon.png (256x256) and icon@2x.png (512x512)  
- Add logo.png (256x256) and logo@2x.png (512x512)
- Support for ksk domain integration"
```

### 6. Пуш в ваш форк  
```bash
git push origin add-ksk-integration
```

### 7. Создание Pull Request
1. Перейдите на GitHub в ваш форк brands
2. Нажмите **Pull Request**
3. Убедитесь, что base repository: `home-assistant/brands` base: `master`
4. Заполните описание PR:

**Title:** `Add КСК (Kaluga Supply Company) integration branding`

**Description:**
```
## Summary
Add branding assets for the КСК (Kaluga Supply Company) custom integration.

## Integration Details
- **Domain:** `ksk`
- **Type:** Custom Integration  
- **Repository:** https://github.com/kirush0280/home-assistant-ksk-integration
- **Company:** КСК (Калужская Сбытовая Компания)

## Files Added
- `custom_integrations/ksk/icon.png` (256×256)
- `custom_integrations/ksk/icon@2x.png` (512×512)  
- `custom_integrations/ksk/logo.png` (256×256)
- `custom_integrations/ksk/logo@2x.png` (512×512)

## Verification
- [x] Images meet the size requirements
- [x] Images are optimized PNG format
- [x] Images have transparent background
- [x] Domain matches integration manifest.json
- [x] No trademark violations

The logo is sourced from the official КSK website: https://svet.kaluga.ru
```

### 8. После одобрения PR
После того как PR будет принят:
1. Логотипы станут доступны по URL: `https://brands.home-assistant.io/ksk/icon.png`
2. Интеграция автоматически получит фирменные иконки в Home Assistant
3. HACS будет отображать правильный логотип

## ⏱️ Время ожидания
- **Обработка PR:** 1-7 дней (зависит от загруженности мейнтейнеров)
- **Кеширование:** до 24 часов после принятия PR  
- **Обновление в Home Assistant:** в следующем релизе

## 📞 Поддержка
Если возникнут вопросы при создании PR, обращайтесь к:
- [Документации Home Assistant Brands](https://github.com/home-assistant/brands#readme)
- [Гайдлайнам по контрибьютингу](https://github.com/home-assistant/brands/blob/master/.github/CONTRIBUTING.md)

---
*Все логотипы являются собственностью КСК (Калужская Сбытовая Компания) и использованы для идентификации.*
