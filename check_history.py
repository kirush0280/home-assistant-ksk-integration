#!/usr/bin/env python3
"""
Быстрая проверка истории потребления в API.
"""

import asyncio
import json
import aiohttp

USERNAME = "204027528"
PASSWORD = "qwsxza"
API_BASE_URL = "https://svet.kaluga.ru/test7/service"

async def check_consumption_history():
    """Проверяем consumption_history."""
    
    async with aiohttp.ClientSession() as session:
        # Авторизация
        auth_url = f"{API_BASE_URL}/auth/sign-in"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Origin': 'https://svet.kaluga.ru',
            'Referer': 'https://svet.kaluga.ru/',
            'Content-Type': 'application/json',
        }
        
        auth_data = {"account": USERNAME, "password": PASSWORD}
        
        async with session.post(auth_url, json=auth_data, headers=headers) as response:
            auth_result = await response.json()
            token = auth_result.get('token')
            
            if not token:
                print("❌ Не удалось получить токен")
                return
            
            headers['Authorization'] = f'Bearer {token}'
            
            # Получаем список счетов
            accounts_url = f"{API_BASE_URL}/api/profile/accounts/"
            async with session.get(accounts_url, headers=headers) as resp:
                accounts = await resp.json()
                if isinstance(accounts, dict):
                    accounts = [accounts]
            
            print("🔍 ПРОВЕРКА HISTORY ENDPOINTS:")
            print("=" * 60)
            
            for account in accounts[:1]:  # Проверяем только первый счет
                account_id = account.get("number")
                print(f"\n🏠 Проверяем счет {account_id}:")
                
                # Проверяем consumption_history
                try:
                    consumption_url = f"{API_BASE_URL}/history/consumptions/{account_id}"
                    async with session.get(consumption_url, headers=headers) as resp:
                        if resp.status == 200:
                            consumption_history = await resp.json()
                            print(f"📊 consumption_history: {json.dumps(consumption_history, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"❌ consumption_history: HTTP {resp.status}")
                except Exception as e:
                    print(f"❌ consumption_history: {e}")
                
                # Проверяем payment_history  
                try:
                    payment_url = f"{API_BASE_URL}/history/payments/{account_id}"
                    async with session.get(payment_url, headers=headers) as resp:
                        if resp.status == 200:
                            payment_history = await resp.json()
                            print(f"💳 payment_history: {json.dumps(payment_history, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"❌ payment_history: HTTP {resp.status}")
                except Exception as e:
                    print(f"❌ payment_history: {e}")
                
                # Проверяем meter_history
                try:
                    meter_url = f"{API_BASE_URL}/history/meters/{account_id}"
                    async with session.get(meter_url, headers=headers) as resp:
                        if resp.status == 200:
                            meter_history = await resp.json()
                            print(f"⚡ meter_history: {json.dumps(meter_history, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"❌ meter_history: HTTP {resp.status}")
                except Exception as e:
                    print(f"❌ meter_history: {e}")
            
            print("\n" + "=" * 60)
            print("ВЫВОДЫ:")
            print("Если какие-то history endpoints возвращают пустые данные или ошибки,")
            print("соответствующие сенсоры можно убрать из интеграции.")

if __name__ == "__main__":
    asyncio.run(check_consumption_history())
