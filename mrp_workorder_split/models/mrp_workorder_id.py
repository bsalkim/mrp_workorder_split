import logging
from odoo import models
import re

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _split_production(self, qty):
        # Odoo'nun standart bölme fonksiyonu
        backorder = super()._split_production(qty)

        # Referans numarasını düzenle
        match = re.match(r'(.*?)(-\d+)?$', self.name)
        base_name = match.group(1) if match else self.name

        existing_mos = self.env['mrp.production'].search([('name', 'like', f"{base_name}-%")])
        existing_suffixes = []
        for mo in existing_mos:
            m = re.match(rf'{re.escape(base_name)}-(\d+)$', mo.name)
            if m:
                existing_suffixes.append(int(m.group(1)))

        suffix = 1
        while f"{base_name}-{str(suffix).zfill(3)}" in existing_mos.mapped('name'):
            suffix += 1

        new_name = f"{base_name}-{str(suffix).zfill(3)}"
        backorder.write({'name': new_name})

        _logger.warning(f"🔧 Backorder üretim emri numarası güncellendi: {new_name}")

        return backorder
