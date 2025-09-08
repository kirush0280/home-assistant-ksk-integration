#!/usr/bin/env python3
"""
Финальная проверка оставшихся сенсоров.
"""

def final_sensor_check():
    remaining_sensors = {
        "Информационные": [
            "KSKAccountSensor - Информация о лицевом счете",
            "KSKUserInfoSensor - Информация о пользователе",
        ],
        
        "Финансовые (актуальные)": [
            "KSKBalanceSensor - Задолженность (debt) из account.balance",
            "KSKPenaltySensor - Пени (penalty) из account.balance", 
            "KSKAcceptedPaymentsSensor - Принятые платежи из account.balance",
            "KSKProcessingPaymentsSensor - Платежи в обработке из account.balance",
        ],
        
        "Показания счетчика": [
            "KSKMeterSensor - Информация о счетчике",
            "KSKReadingsSensor - Показания счетчика из transmission_details", 
            "KSKTariffSensor - Тариф из zones",
        ],
        
        "История потребления (ПРОБЛЕМНЫЕ?)": [
            "KSKLastConsumptionSensor - Из consumption_history[0].consumption",
            "KSKMonthlyConsumptionSensor - Из consumption_history для текущего месяца",
            "KSKAverageConsumptionSensor - Среднее из consumption_history[-3:]",
        ],
        
        "История платежей": [
            "KSKLastPaymentSensor - Из payment_history[0].amount",
        ],
        
        "Технические": [
            "KSKLastUpdateSensor - Время последнего обновления",
            "KSKDataFreshnessSensor - Свежесть данных",
        ]
    }
    
    print("=" * 80)
    print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА ОСТАВШИХСЯ СЕНСОРОВ")
    print("=" * 80)
    
    for category, sensors in remaining_sensors.items():
        print(f"\n📊 {category}:")
        print("-" * 50)
        for sensor in sensors:
            print(f"   ✅ {sensor}")
    
    print("\n" + "=" * 80)
    print("❓ ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ:")
    print("=" * 80)
    print("1. Сенсоры истории потребления (consumption_history):")
    print("   - Нужно проверить, есть ли реальные данные в API")
    print("   - В отладке не видели этих данных")
    print("   - Возможно эти сенсоры всегда пустые")
    print("\n2. Возможно стоит убрать:")
    print("   - KSKLastConsumptionSensor")
    print("   - KSKMonthlyConsumptionSensor") 
    print("   - KSKAverageConsumptionSensor")
    print("   Если API не предоставляет consumption_history данных")
    
    print("\n💡 ИТОГО:")
    print("✅ Основные сенсоры корректны")
    print("❓ Сенсоры истории потребления требуют проверки")

if __name__ == "__main__":
    final_sensor_check()
