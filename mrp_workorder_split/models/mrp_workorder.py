import logging
from odoo import models

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        self.ensure_one()
        _logger.warning(f"✅ [MODÜL] record_production override edildi — {self.name}")

        production = self.production_id
        if not production:
            return super().record_production()

        produced = self.qty_produced
        planned = self.qty_production  # üretilecek toplam miktar (iş emri özelinde)

        _logger.warning(f"📊 Üretilen: {produced}, Planlanan: {planned}, İş Emri: {self.name}")

        res = super().record_production()

        if produced < planned:
            _logger.warning("🔁 Parçalı üretim tespit edildi. Üretim emri bölünüyor...")

            remaining_qty = planned - produced

            new_mo = production.copy({
                'product_qty': remaining_qty,
                'origin': f"{production.name} - Kalan",
                'workorder_ids': False,
                'state': 'confirmed',
            })

            new_mo.action_confirm()
            new_mo.action_assign()
            new_mo._generate_workorders()

            _logger.warning(f"🆕 Yeni Üretim Emri: {new_mo.name} — Miktar: {remaining_qty}")
            _logger.warning(f"🛠 Yeni üretim emrinde iş emirleri oluşturuldu: {new_mo.workorder_ids.mapped('name')}")

        return res
