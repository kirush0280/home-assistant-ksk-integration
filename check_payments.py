#!/usr/bin/env python3
"""
Проверяем что возвращает API payment_details - возможно там есть принятые платежи
"""

import asyncio
import aiohttp
import json
import pprint

API_BASE_URL = "https://lk-api.ksk-kaluga.ru:8443/api/v1"
API_AUTH_URL = f"{API_BASE_URL}/auth/login"
API_ACCOUNTS_URL = f"{API_BASE_URL}/accounts"
API_PAYMENT_DETAILS_URL = f"{API_BASE_URL}/payment-details"

LOGIN = "204027528"
PASSWORD = "qwsxza"

async def test_payment_details():
    async with aiohttp.ClientSession() as session:
        # Авторизация
        print("🔐 Авторизация...")
        auth_data = {
            "login": LOGIN,
            "password": PASSWORD
        }
        
        async with session.post(API_AUTH_URL, json=auth_data) as response:
            if response.status != 200:
                print(f"❌ Ошибка авторизации: {response.status}")
                return
            
            auth_result = await response.json()
            token = auth_result.get("data", {}).get("token")
            if not token:
                print("❌ Не удалось получить токен")
                return
            
            print(f"✅ Токен получен: {token[:20]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Получаем лицевые счета
        print("\n📋 Получаем лицевые счета...")
        async with session.get(API_ACCOUNTS_URL, headers=headers) as response:
            if response.status != 200:
                print(f"❌ Ошибка получения счетов: {response.status}")
                return
                
            accounts_result = await response.json()
            accounts = accounts_result.get("data", [])
            print(f"✅ Найдено счетов: {len(accounts)}")
            
            for account in accounts:
                print(f"  📊 Счет: {account.get('number')} - {account.get('address')}")
        
        # Проверяем payment_details для каждого счета
        for account in accounts:
            account_id = account.get("number")
            if not account_id:
                continue
                
            print(f"\n💰 Проверяем payment_details для счета {account_id}...")
            
            params = {"accountId": account_id}
            async with session.get(API_PAYMENT_DETAILS_URL, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"❌ Ошибка получения payment_details: {response.status}")
                    continue
                
                payment_result = await response.json()
                payment_data = payment_result.get("data", {})
                
                print(f"\n📊 ПОЛНЫЕ ДАННЫЕ payment_details для счета {account_id}:")
                print("="*60)
                pprint.pprint(payment_data, width=120, depth=5)
                print("="*60)
                
                # Анализируем структуру
                print(f"\n🔍 Анализ структуры payment_details:")
                if isinstance(payment_data, dict):
                    for key, value in payment_data.items():
                        print(f"  🏷️  {key}: {type(value).__name__}")
                        if isinstance(value, (list, dict)) and value:
                            if isinstance(value, list) and len(value) > 0:
                                print(f"    📝 Первый элемент: {type(value[0]).__name__}")
                                if isinstance(value[0], dict):
                                    print(f"    🔑 Ключи: {list(value[0].keys())}")
                            elif isinstance(value, dict):
                                print(f"    🔑 Ключи: {list(value.keys())}")
                
                # Ищем информацию о принятых платежах
                print(f"\n🎯 ПОИСК ПРИНЯТЫХ ПЛАТЕЖЕЙ:")
                
                def find_payments(data, path=""):
                    """Рекурсивный поиск данных о платежах"""
                    if isinstance(data, dict):
                        for key, value in data.items():
                            current_path = f"{path}.{key}" if path else key
                            
                            # Ключевые слова для платежей
                            payment_keywords = ['payment', 'платеж', 'принят', 'accepted', 
                                              'paid', 'оплач', 'сумма', 'amount', 'sum']
                            
                            if any(keyword in key.lower() for keyword in payment_keywords):
                                print(f"  💵 {current_path}: {value}")
                            
                            if isinstance(value, (dict, list)):
                                find_payments(value, current_path)
                                
                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            current_path = f"{path}[{i}]"
                            find_payments(item, current_path)
                
                find_payments(payment_data)

if __name__ == "__main__":
    asyncio.run(test_payment_details())
