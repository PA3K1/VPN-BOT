from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import requests
import sqlite3
import asyncio

# Простая база данных в памяти
users_db = {}
pending_payments = []

# Бот БЕЗ прокси - используем другой подход
bot = Client(
    "vpn_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    # Убираем proxy полностью
)


@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    users_db[user_id] = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name
    }

    keyboard = [
        [InlineKeyboardButton("1 месяц - 299₽", callback_data="tariff_1_month")],
        [InlineKeyboardButton("3 месяца - 799₽", callback_data="tariff_3_months")],
        [InlineKeyboardButton("1 год - 1999₽", callback_data="tariff_1_year")]
    ]

    await message.reply(
        "🔒 **VPN Сервис SnowBall**\n\n"
        "Выберите тариф:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@bot.on_callback_query()
async def handle_callbacks(client, callback):
    data = callback.data
    user_id = callback.from_user.id

    if data.startswith("tariff_"):
        tariff = data.replace("tariff_", "")
        prices = {"1_month": 299, "3_months": 799, "1_year": 1999}
        durations = {"1_month": "30 дней", "3_months": "90 дней", "1_year": "365 дней"}

        price = prices[tariff]
        duration = durations[tariff]

        keyboard = [
            [InlineKeyboardButton("🎮 Инструкция по оплате", callback_data=f"pay_{tariff}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]

        await callback.message.edit_text(
            f"**Тариф:** {tariff.replace('_', ' ').title()}\n"
            f"**Цена:** {price}₽\n"
            f"**Срок:** {duration}\n\n"
            "Нажмите кнопку ниже для инструкции по оплате:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("pay_"):
        tariff = data.replace("pay_", "")
        prices = {"1_month": 299, "3_months": 799, "1_year": 1999}
        price = prices[tariff]

        # Добавляем в ожидающие платежи
        pending_payments.append({
            'user_id': user_id,
            'tariff': tariff,
            'amount': price
        })

        instruction = f"""
🎮 **Оплата через Lolzsteam**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽

📋 **Инструкция:**

1. **Перейдите по ссылке:**
   https://lolz.live/market/balance/transfer/

2. **Заполните форму:**
   • **Получатель:** `pazk` (ID: 9690362)
   • **Сумма:** `{price}` ₽
   • **Комментарий:** `VPN{user_id}`

3. **После оплаты напишите в поддержку:**
   @pa3kkkkk

⚡ **VPN будет выдан вручную**
        """

        keyboard = [
            [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="back")],
            [InlineKeyboardButton("📞 Поддержка", url="https://t.me/pa3kkkkk")]
        ]

        await callback.message.edit_text(
            instruction,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("1 месяц - 299₽", callback_data="tariff_1_month")],
            [InlineKeyboardButton("3 месяца - 799₽", callback_data="tariff_3_months")],
            [InlineKeyboardButton("1 год - 1999₽", callback_data="tariff_1_year")]
        ]
        await callback.message.edit_text(
            "🔒 **VPN Сервис SnowBall**\n\nВыберите тариф:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@bot.on_message(filters.command("check"))
async def check_payments(client, message):
    """Проверить ожидающие платежи"""
    if pending_payments:
        response = "⏳ **Ожидающие платежи:**\n\n"
        for payment in pending_payments[-5:]:
            response += f"• ID: {payment['user_id']} | Тариф: {payment['tariff']} | Сумма: {payment['amount']}₽\n"
    else:
        response = "📭 Нет ожидающих платежей"

    await message.reply(response)


@bot.on_message(filters.command("issue"))
async def issue_vpn(client, message):
    """Выдать VPN (только тебе)"""
    if message.from_user.id != 9690362:  # Твой ID
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("Использование: /issue <user_id> <tariff>")
            return

        user_id = int(parts[1])
        tariff = parts[2]

        vpn_links = {
            "1_month": "https://sub.snowfall.top/bxMHd7z0JHfB2dwK",
            "3_months": "https://sub.snowfall.top/bxMHd7z0JHfB2dwK",
            "1_year": "https://sub.snowfall.top/bxMHd7z0JHfB2dwK"
        }

        vpn_link = vpn_links.get(tariff)

        await client.send_message(
            user_id,
            f"✅ **Оплата подтверждена!**\n\n"
            f"**Ваш VPN доступ:**\n"
            f"• Тариф: {tariff.replace('_', ' ').title()}\n"
            f"• Ссылка: `{vpn_link}`\n\n"
            f"📞 Поддержка: @pa3kkkkk"
        )

        await message.reply(f"✅ VPN выдан пользователю {user_id}")

    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("🚀 Бот запускается...")
    bot.run()