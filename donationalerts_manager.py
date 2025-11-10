import config


class DonationAlertsManager:
    def __init__(self):
        self.donation_page = "https://www.donationalerts.com/r/pazk"

    def create_donation_link(self, amount, user_id, tariff):
        """Создает ссылку для доната с комментарием"""
        donation_url = f"{self.donation_page}?amount={amount}&message=VPN{user_id}"
        return donation_url


donationalerts = DonationAlertsManager()