import config
from urllib.parse import quote

class YooMoneyManager:
    def __init__(self):
        self.wallet_number = config.YOOMONEY_WALLET

    def create_payment_form(self, amount, user_id, tariff):
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

yoomoney = YooMoneyManager()