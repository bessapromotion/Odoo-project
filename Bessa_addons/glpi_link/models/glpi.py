from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ticket_number = fields.Char(string="N°ticket GLPI", required=True, size=5, pattern=r'^\d{1,5}$')
    ticket_link = fields.Char(string="Lien vers le ticket GLPI", readonly=True, store=True)

    APP_TOKEN = "cSwHiDrTU2Gdh0kTnQSWykba5RW85tZHBt1QGaK6"

    def _get_session_token(self):
        url = "http://192.168.2.16/apirest.php/initSession"
        username = "admin"
        password = "@Dmin-2021$$"

        headers = {
            "Content-Type": "application/json",
            "App-Token": self.APP_TOKEN,
        }

        response = requests.get(url, headers=headers, auth=(username, password))

        if response.status_code == 200:
            session_token = response.json().get("session_token")
            return session_token

        raise ValidationError("Impossible de récupérer le session token. Veuillez vérifier vos informations d'identification.")

    @api.constrains('ticket_number')
    def _check_ticket_number(self):
        for order in self:
            if order.ticket_number:
                url = f"http://192.168.2.16/apirest.php/ticket/{order.ticket_number}"
                session_token = self._get_session_token()

                headers = {
                    "Content-Type": "application/json",
                    "Session-Token": session_token,
                    "App-Token": self.APP_TOKEN
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    order.ticket_link = f"http://192.168.2.16/front/ticket.form.php?id={order.ticket_number}"
                else:
                    raise ValidationError("Le numéro de ticket spécifié est invalide. Veuillez vérifier le numéro de ticket et réessayer.")
