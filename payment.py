import requests
import config


class PaymentProcessor:
    def __init__(self):
        self.api_token = config.LOLZSTEAM_API_TOKEN
        self.base_url = f"https://api.{config.LOLZSTEAM_DOMAIN}"

    def get_balance(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{self.base_url}/api/user/me", headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                balance = user_data.get("balance", 0)
                return balance
            else:
                return 0

        except Exception as e:
            return 0


payment_checker = PaymentProcessor()