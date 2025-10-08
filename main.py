from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import config
from keyboards import main_keyboard, tariffs_keyboard, payment_keyboard, support_keyboard
from database import Database
from payment import payment_checker

bot = Client(
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    name="VPN_BOT"
)

db = Database()

async def send_vpn_success(user_id, tariff, vpn_link):
    try:
        instruction_text = f"""
✅ **Оплата подтверждена!**

🎉 **Ваш VPN доступ активирован:**
• Тариф: {tariff.replace('_', ' ').title()}
• Ссылка на конфиг: `{vpn_link}`

📖 **Инструкция по установке:**

**Для Windows:**
1. Скачайте OpenVPN: https://openvpn.net/client/
2. Установите программу
3. Скачайте конфиг файл по ссылке выше
4. Запустите OpenVPN → Импорт файла → Подключиться

**Для Android:**
1. Установите OpenVPN из Play Market
2. Скачайте конфиг файл
3. В приложении: Import → Import from SD card
4. Выберите файл и нажмите Connect

⚡ **Преимущества нашего VPN:**
• Высокая скорость
• Безлимитный трафик
• Защита данных
• Поддержка 24/7

📞 **Поддержка:** {config.SUPPORT_ACCOUNT}
        """
        
        await bot.send_message(user_id, instruction_text)
        
    except Exception as e:
        print(f"Ошибка отправки VPN: {e}")

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
🔒 **Добро пожаловать в VPN сервис, {user.first_name}!**

⚡ **Преимущества нашего VPN:**
✓ Высокая скорость подключения
✓ Безлимитный трафик  
✓ Полная анонимность
✓ Защита от слежки
✓ Поддержка 24/7

🎯 **Выберите действие:**
    """
    await message.reply(welcome_text, reply_markup=main_keyboard())

@bot.on_message(filters.text)
async def handle_text(client: Client, message: Message):
    text = message.text
    
    if text == "🛒 Купить VPN":
        await message.reply("**Выберите тарифный план:**", reply_markup=tariffs_keyboard())
    
    elif text == "📋 Мои покупки":
        user_id = message.from_user.id
        purchases = db.get_user_purchases(user_id)
        
        if purchases:
            response = "📋 **Ваши активные подписки:**\n\n"
            for purchase in purchases:
                status = "✅ Активна" if purchase[8] == 'active' else "❌ Истекла"
                response += f"• Тариф: {purchase[2]}\n"
                response += f"• Стоимость: {purchase[3]}₽\n"
                response += f"• Ссылка: `{purchase[5]}`\n"
                response += f"• Действует до: {purchase[7]}\n"
                response += f"• Статус: {status}\n\n"
        else:
            response = "📭 У вас пока нет активных подписок"
        
        await message.reply(response)
    
    elif text == "🆘 Поддержка":
        await message.reply(
            f"📞 **Служба поддержки**\n\n"
            f"По любым вопросам обращайтесь:\n"
            f"{config.SUPPORT_ACCOUNT}\n\n"
            f"Мы онлайн 24/7!",
            reply_markup=support_keyboard()
        )

@bot.on_callback_query()
async def handle_callbacks(client: Client, callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    try:
        if data.startswith("tariff_"):
            tariff = data.replace("tariff_", "")
            price = config.PRICES[tariff]
            
            duration = {'1_month': '30 дней', '3_months': '90 дней', '1_year': '365 дней'}[tariff]

            await callback.message.edit_text(
                f"**Тариф:** {tariff.replace('_', ' ').title()}\n"
                f"**Цена:** {price}₽\n"
                f"**Срок:** {duration}\n\n"
                "**Для оплаты нажмите кнопку ниже:**\n"
                "Мы принимаем платежи через Lolzsteam",
                reply_markup=payment_keyboard(tariff)
            )

        elif data.startswith("lolz_instruction_"):
            tariff = data.replace("lolz_instruction_", "")
            price = config.PRICES[tariff]
            
            duration = {'1_month': '30 дней', '3_months': '90 дней', '1_year': '365 дней'}[tariff]

            initial_balance = payment_checker.get_balance()
            db.add_pending_payment(user_id, tariff, price, initial_balance)

            instruction_text = f"""
🎮 **Оплата через Lolzsteam**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽
**Срок:** {duration}

📋 **Инструкция:**

1. **Перейдите по ссылке:**
   https://{config.LOLZSTEAM_DOMAIN}/market/balance/transfer/

2. **Заполните форму:**
   • **Получатель:** `{config.LOLZSTEAM_USERNAME}` (или ID: {config.LOLZSTEAM_USER_ID})
   • **Сумма:** `{price}` ₽
   • **Комментарий:** `VPN{user_id}` (ОБЯЗАТЕЛЬНО!)

3. **Нажмите "Перевести" и подтвердите**

4. **После оплаты:**
   • Напишите в поддержку: {config.SUPPORT_ACCOUNT}
   • Или используйте команду: /check_payments

⚡ **VPN будет выдан вручную в течение 5-10 минут**
            """

            await callback.message.edit_text(
                instruction_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="back_to_tariffs")],
                    [InlineKeyboardButton("📞 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")]
                ])
            )

        elif data == "back_to_tariffs":
            await callback.message.edit_text("**Выберите тарифный план:**", reply_markup=tariffs_keyboard())

    except Exception as e:
        print(f"❌ Ошибка в обработчике колбэков: {e}")

@bot.on_message(filters.command("issue") & filters.user([9690362]))
async def manual_issue_vpn(client: Client, message: Message):
    """Ручная выдача VPN (только для админа)"""
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("❌ Использование: /issue <user_id> <tariff>\nТарифы: 1_month, 3_months, 1_year")
            return
        
        user_id = int(parts[1])
        tariff = parts[2]
        
        if tariff not in config.PRICES:
            await message.reply(f"❌ Неверный тариф. Доступные: {', '.join(config.PRICES.keys())}")
            return
        
        price = config.PRICES[tariff]
        vpn_link = config.VPN_LINKS.get(tariff)
        
        days = {
            "1_month": 30,
            "3_months": 90, 
            "1_year": 365
        }[tariff]
        
        db.complete_purchase(user_id, tariff, price, "manual", vpn_link, days)
        
        await client.send_message(
            user_id,
            f"✅ **Оплата подтверждена!**\n\n"
            f"**Ваш VPN доступ активирован:**\n"
            f"• Тариф: {tariff.replace('_', ' ').title()}\n"
            f"• Ссылка: `{vpn_link}`\n"
            f"• Действует: {days} дней\n\n"
            f"📖 Инструкция по установке в меню бота"
        )
        
        await message.reply(f"✅ VPN выдан пользователю {user_id}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")

@bot.on_message(filters.command("check_payments"))
async def check_recent_payments(client: Client, message: Message):
    """Проверить недавние платежи"""
    user_id = message.from_user.id
    
    pending = db.get_pending_payments()
    
    if pending:
        response = "⏳ **Ожидающие платежи:**\n\n"
        for payment in pending[-5:]:
            response += f"• ID: {payment[1]} | Тариф: {payment[2]} | Сумма: {payment[3]}₽\n"
        response += f"\nЧтобы выдать VPN: /issue {user_id} 1_month"
    else:
        response = "📭 Нет ожидающих платежей"
    
    await message.reply(response)

if __name__ == "__main__":
    print("🚀 VPN бот запускается...")
    bot.run()