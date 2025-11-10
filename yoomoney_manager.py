import config
from urllib.parse import quote

class YooMoneyManager:
    def __init__(self):
        self.wallet_number = config.YOOMONEY_WALLET

    def create_payment_form(self, amount, user_id, tariff):
        """Создает форму для перевода в ЮMoney"""
        # Кодируем параметры для URL
        targets = quote(f"VPN {tariff}")
        comment = quote(f"VPN{user_id}")

        payment_url = (
            f"https://yoomoney.ru/quickpay/confirm.xml?"
            f"receiver={self.wallet_number}&"
            f"quickpay-form=button&"
            f"targets={targets}&"
            f"sum={amount}&"
            f"label=VPN{user_id}&"
            f"comment={comment}&"
            f"successURL=https://t.me/{config.BOT_USERNAME}"
        )

        return payment_url

    def create_simple_payment_link(self, amount, user_id):
        """Простая ссылка для перевода"""
        return f"https://yoomoney.ru/to/{self.wallet_number}/{amount}"

yoomoney = YooMoneyManager()