from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import Database

# Инициализация бота
bot = Client(
    "vpn_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

db = Database()

# Клавиатуры
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Купить VPN", callback_data="show_tariffs")],
        [InlineKeyboardButton("📋 Мои покупки", callback_data="my_purchases")],
        [InlineKeyboardButton("🆘 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")]
    ])

def tariffs_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 месяц - 199₽", callback_data="tariff_1_month")],
        [InlineKeyboardButton("3 месяца - 499₽", callback_data="tariff_3_months")],
        [InlineKeyboardButton("1 год - 1699₽", callback_data="tariff_1_year")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ])

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

@bot.on_callback_query()
async def handle_callbacks(client, callback):
    data = callback.data
    user_id = callback.from_user.id

    try:
        if data == "show_tariffs":
            await callback.message.edit_text(
                "**Выберите тарифный план:**",
                reply_markup=tariffs_keyboard()
            )

        elif data == "back_to_main":
            await callback.message.edit_text(
                "🔒 **Главное меню VPN сервиса**\n\nВыберите действие:",
                reply_markup=main_keyboard()
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

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 ЮMoney", callback_data=f"pay_yoomoney_{tariff}")],
                [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="back_to_tariffs")]
            ])

            await callback.message.edit_text(
                f"**Тариф:** {tariff.replace('_', ' ').title()}\n"
                f"**Цена:** {price}₽\n"
                f"**Срок:** {duration}\n\n"
                "💸 **Выберите способ оплаты:**",
                reply_markup=keyboard
            )

        elif data == "back_to_tariffs":
            await callback.message.edit_text(
                "**Выберите тарифный план:**",
                reply_markup=tariffs_keyboard()
            )

        elif data.startswith("pay_yoomoney_"):
            tariff = data.replace("pay_yoomoney_", "")
            price = config.PRICES[tariff]
            
            from yoomoney_manager import yoomoney
            payment_url = yoomoney.create_payment_form(price, user_id, tariff)
            
            db.add_pending_payment(user_id, tariff, price)

            payment_text = f"""
💳 **Оплата через ЮMoney**

**Тариф:** {tariff.replace('_', ' ').title()}
**Сумма:** {price}₽

👇 **Нажмите для перехода к оплате:**

⚡ **После оплаты напишите в поддержку**
📞 **Поддержка:** {config.SUPPORT_ACCOUNT}
            """

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Оплатить через ЮMoney", url=payment_url)],
                [InlineKeyboardButton("📞 Поддержка", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"tariff_{tariff}")]
            ])

            await callback.message.edit_text(
                payment_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

        else:
            await callback.answer("⚠️ Функция в разработке")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

@bot.on_message(filters.command("stats"))
async def show_stats(client: Client, message: Message):
    """Показать статистику бота"""
    if message.from_user.id != 9690362:  # Только для админа
        return

    try:
        pending = db.get_pending_payments()
        stats_text = f"""
📊 **Статистика бота:**

⏳ Ожидающие платежи: {len(pending)}
👥 Всего пользователей: {db.get_all_users()}
        """
        await message.reply(stats_text)
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 VPN Bot started!")
    bot.run()