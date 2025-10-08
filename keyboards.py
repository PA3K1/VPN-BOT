from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import config

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["🛒 Купить VPN", "📋 Мои покупки"],
        ["🆘 Поддержка"]
    ], resize_keyboard=True)

def tariffs_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 месяц - 299₽", callback_data="tariff_1_month")],
        [InlineKeyboardButton("3 месяца - 799₽", callback_data="tariff_3_months")],
        [InlineKeyboardButton("1 год - 1999₽", callback_data="tariff_1_year")]
    ])

def payment_keyboard(tariff):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Оплатить через Lolzsteam", callback_data=f"pay_{tariff}")],
        [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="back_to_tariffs")]
    ])

def support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Написать в поддержку", url=f"https://t.me/{config.SUPPORT_ACCOUNT.replace('@', '')}")]
    ])