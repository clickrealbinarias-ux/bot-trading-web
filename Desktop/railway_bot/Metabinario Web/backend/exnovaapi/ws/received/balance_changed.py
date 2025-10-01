"""Module for Exnova websocket."""

def balance_changed(api, message):
    if message['name'] == 'balance-changed':
        balance = message['msg']['current_balance']
        # if self.api.get_active_account_type() == balance['type']:
        try:
            api.profile.balance = balance["amount"]
        except Exception:
            pass

        try:
            api.profile.balance_id = balance["id"]
        except Exception:
            pass

        try:
            api.profile.balance_type = balance["type"]
        except Exception:
            pass