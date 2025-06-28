import logging
from odoo import models
import re

_logger = logging.getLogger(__name__)

class MrpProductionBackorder(models.TransientModel):
    _inherit = 'mrp.production.backorder'

    def action_backorder(self):
        res = super().action_backorder()

        for record in self:
            for production in record.production_ids:
                # Sadece backorder kaydedilen kayıtlar
                for backorder in production.backorder_ids:
                    # Ana numarayı ayıkla
                    match = re.match(r'(.*?)(-\d+)?$', production.name)
                    base_name = match.group(1) if match else production.name

                    existing_names = self.env['mrp.production'].search([('name', 'like', f"{base_name}-%")]).mapped('name')
                    suffix = 1
                    while f"{base_name}-{str(suffix).zfill(3)}" in existing_names:
                        suffix += 1

                    new_name = f"{base_name}-{str(suffix).zfill(3)}"
                    backorder.name = new_name

                    _logger.warning(f"🔧 Backorder üretim emri adı güncellendi: {new_name}")

        return res
