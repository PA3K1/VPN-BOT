from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import Database
from yoomoney_manager import yoomoney
from donationalerts_manager import donationalerts
import asyncio
import sys
import signal

# Инициализация
bot = Client(
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    name="VPN_BOT"
)

db = Database()


# Обработчик остановки для стабильной работы
def signal_handler(signum, frame):
    print("🔴 Получен сигнал остановки...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Клавиатуры
def main_keyboard():
    return [[
        InlineKeyboardButton("🛒 Купить VPN", callback_data="show_tariffs"),
        InlineKeyboardButton("📋 Мои покупки", callback_data="my_purchases")
    ], [
        InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")
    ]]


def tariffs_keyboard():
    return [[
        InlineKeyboardButton("1 месяц - 199₽", callback_data="tariff_1_month")
    ], [
        InlineKeyboardButton("3 месяца - 499₽", callback_data="tariff_3_months")
    ], [
        InlineKeyboardButton("1 год - 1699₽", callback_data="tariff_1_year")
    ], [
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    ]]


def payment_keyboard(tariff):
    return [[
        InlineKeyboardButton("🎁 DonationAlerts", callback_data=f"pay_donate_{tariff}"),
        InlineKeyboardButton("💳 ЮMoney", callback_data=f"pay_yoomoney_{tariff}")
    ], [
        InlineKeyboardButton("🔙 Назад к тарифам", callback_data="back_to_tariffs")
    ]]


async def send_vpn_instructions(user_id, tariff, vpn_link):
    """Отправляет инструкцию по установке VPN"""
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
        print(f"Ошибка отправки инструкции: {e}")


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
    await message.reply(welcome_text, reply_markup=InlineKeyboardMarkup(main_keyboard()))


@bot.on_callback_query()
async def handle_callbacks(client: Client, callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    try:
        if data == "show_tariffs":
            await callback.message.edit_text(
                "**Выберите тарифный план:**",
                reply_markup=InlineKeyboardMarkup(tariffs_keyboard())
            )

        elif data == "back_to_main":
            await callback.message.edit_text(
                "🔒 **Главное меню VPN сервиса**\n\nВыберите действие:",
                reply_markup=InlineKeyboardMarkup(main_keyboard())
            )

        elif data == "back_to_tariffs":
            await callback.message.edit_text(
                "**Выберите тарифный план:**",
                reply_markup=InlineKeyboardMarkup(tariffs_keyboard())
            )

        elif data == "my_purchases":
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

            await callback.message.edit_text(
                response,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                ]])
            )

        elif data.startswith("tariff_"):
            tariff = data.replace("tariff_", "")
            price = config.PRICES[tariff]
            duration = {'1_month': '30 дней', '3_months': '90 дней', '1_year': '365 дней'}[tariff]

            await callback.message.edit_text(
                f"**Тариф:** {tariff.replace('_', ' ').title()}\n"
                f"**Цена:** {price}₽\n"
                f"**Срок:** {duration}\n\n"
                "💸 **Выберите способ оплаты:**",
                reply_markup=InlineKeyboardMarkup(payment_keyboard(tariff))
            )

        elif data.startswith("pay_donate_"):
            tariff = data.replace("pay_donate_", "")
            price = config.PRICES[tariff]
            user_id = callback.from_user.id

            # Создаем ссылку для доната
            donation_url = donationalerts.create_donation_link(price, user_id, tariff)

            # Добавляем в ожидающие платежи
            db.add_pending_payment(user_id, tariff, price)

            payment_text = f"""
🎁 **Оплата через DonationAlerts**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽

💡 **Как оплатить:**
1. Нажмите кнопку «Перейти к оплате»
2. Выберите способ оплаты (карта, QIWI и др.)
3. После оплаты нажмите «Я оплатил»

⚡ **Преимущества:**
• Не нужна регистрация
• Моментальное зачисление  
• Любые карты и электронные кошельки

📞 **Поддержка:** {config.SUPPORT_ACCOUNT}
            """

            keyboard = [
                [InlineKeyboardButton("🎁 Перейти к оплате", url=donation_url)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data=f"check_donate_{tariff}_{user_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"tariff_{tariff}")]
            ]

            await callback.message.edit_text(
                payment_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )

        elif data.startswith("check_donate_"):
            parts = data.replace("check_donate_", "").split("_")
            tariff = parts[0]
            user_id = int(parts[1])
            price = config.PRICES[tariff]

            check_text = f"""
⏳ **Платеж проверяется**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽
**Ваш ID:** {user_id}

🔍 **Проверяю донат в системе...**
Обычно это занимает 1-2 минуты.

💡 **Проверьте:**
• Совпадает ли сумма ({price}₽)
• Указан ли комментарий: `VPN{user_id}`

📞 **Если платеж не прошел:**
{config.SUPPORT_ACCOUNT}
            """

            await callback.message.edit_text(
                check_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_donate_{tariff}_{user_id}")
                ], [
                    InlineKeyboardButton("📞 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")
                ]])
            )

        elif data.startswith("pay_yoomoney_"):
            tariff = data.replace("pay_yoomoney_", "")
            price = config.PRICES[tariff]
            user_id = callback.from_user.id

            # Создаем ссылку для оплаты
            payment_url = yoomoney.create_payment_form(price, user_id, tariff)

            # Добавляем в ожидающие платежи
            db.add_pending_payment(user_id, tariff, price)

            payment_text = f"""
💳 **Оплата через ЮMoney**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽

🏦 **Безопасная оплата:**
• Принимаем карты, QIWI, WebMoney
• Перевод через защищенный шлюз ЮMoney
• Мгновенное зачисление

👇 **Нажмите для перехода к оплате:**

⚡ **После оплаты нажмите «Я оплатил»**
📞 **Поддержка:** {config.SUPPORT_ACCOUNT}
            """

            keyboard = [
                [InlineKeyboardButton("💳 Оплатить через ЮMoney", url=payment_url)],
                [InlineKeyboardButton("✅ Я оплатил", callback_data=f"check_yoomoney_{tariff}_{user_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"tariff_{tariff}")]
            ]

            await callback.message.edit_text(
                payment_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )

        elif data.startswith("check_yoomoney_"):
            parts = data.replace("check_yoomoney_", "").split("_")
            tariff = parts[0]
            user_id = int(parts[1])
            price = config.PRICES[tariff]

            check_text = f"""
⏳ **Платеж проверяется**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽
**Ваш ID:** {user_id}

🔍 **Проверяю платеж в системе...**
Обычно это занимает 1-2 минуты.

💡 **Проверьте:**
• Совпадает ли сумма ({price}₽)
• Указан ли комментарий: `VPN{user_id}`

📞 **Если платеж не прошел:**
{config.SUPPORT_ACCOUNT}
            """

            await callback.message.edit_text(
                check_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_yoomoney_{tariff}_{user_id}")
                ], [
                    InlineKeyboardButton("📞 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")
                ]])
            )

    except Exception as e:
        print(f"❌ Ошибка в обработчике колбэков: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


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
            await message.reply("❌ Неверный тариф. Доступные: 1_month, 3_months, 1_year")
            return

        price = config.PRICES[tariff]
        vpn_link = config.VPN_LINKS.get(tariff)

        days = {"1_month": 30, "3_months": 90, "1_year": 365}[tariff]
        db.complete_purchase(user_id, tariff, price, "manual", vpn_link, days)

        await client.send_message(
            user_id,
            f"✅ **Оплата подтверждена!**\n\n"
            f"**Ваш VPN доступ активирован:**\n"
            f"• Тариф: {tariff.replace('_', ' ').title()}\n"
            f"• Ссылка: `{vpn_link}`\n"
            f"• Действует: {days} дней\n\n"
            f"📖 Инструкция по установке отправлена отдельным сообщением."
        )

        # Отправляем инструкцию
        await send_vpn_instructions(user_id, tariff, vpn_link)

        await message.reply(f"✅ VPN выдан пользователю {user_id}")

    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@bot.on_message(filters.command("check_payments"))
async def check_payments(client: Client, message: Message):
    """Проверить ожидающие платежи"""
    pending = db.get_pending_payments()

    help_text = """
🔍 **Как проверять платежи:**

**DonationAlerts:**
1. Зайди: https://www.donationalerts.com/dashboard
2. Открой «История донатов»
3. Ищи комментарии: `VPN123456`

**ЮMoney:**
1. Зайди: https://yoomoney.ru
2. Открой «История операций»  
3. Ищи комментарии: `VPN123456`

📋 **Ожидающие платежи:**
"""

    if pending:
        for payment in pending[-10:]:
            help_text += f"• ID: {payment[1]} | Тариф: {payment[2]} | Сумма: {payment[3]}₽\n"
        help_text += f"\n💡 Для выдачи VPN: /issue USER_ID TARIFF"
    else:
        help_text += "📭 Нет ожидающих платежей"

    await message.reply(help_text)


@bot.on_message(filters.command("stats"))
async def show_stats(client: Client, message: Message):
    """Показать статистику бота"""
    if message.from_user.id != 9690362:  # Только для админа
        return

    try:
        # Простая статистика
        pending = db.get_pending_payments()
        stats_text = f"""
📊 **Статистика бота:**

⏳ Ожидающие платежи: {len(pending)}
👥 Всего пользователей: {db.get_all_users()}

💸 Для проверки платежей: /check_payments
🎫 Для выдачи VPN: /issue USER_ID TARIFF
        """
        await message.reply(stats_text)
    except Exception as e:
        await message.reply(f"❌ Ошибка статистики: {e}")


if __name__ == "__main__":
    print("🚀 VPN бот запускается...")
    try:
        bot.run()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)