from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        _logger.warning(f"✅ record_production override çalıştı — {self.name}")

        res = super().record_production()

        for workorder in self:
            produced_qty = workorder.qty_produced
            planned_qty = workorder.production_id.product_qty

            if produced_qty < planned_qty:
                remaining_qty = planned_qty - produced_qty

                _logger.warning(f"🔁 Kalan üretim için yeni iş emri hazırlanıyor — Kalan: {remaining_qty}")

                # Yeni iş emri için yeni workorder kaydı yaratmak için production_id'den routing işlenmesini tekrar çağıracağız
                workorder.production_id._generate_workorders()

                _logger.warning(f"✅ Yeni iş emirleri oluşturuldu. Üretim emri: {workorder.production_id.name}")

        return res
