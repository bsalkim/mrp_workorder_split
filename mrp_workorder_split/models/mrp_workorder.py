from odoo import models
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        raise UserError("✅ TEST — override çalışıyor!")
