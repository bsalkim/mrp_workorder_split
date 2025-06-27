from odoo import models
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        _logger.warning("✅ [MODÜL] record_production override edildi!")
        res = super().record_production()

        for workorder in self:
            produced = workorder.qty_produced
            expected = workorder.qty_production  # düzeltildi ✅

            _logger.warning(f"📊 [MODÜL] {workorder.name} — Üretilen: {produced}, Planlanan: {expected}")

            if 0 < produced < expected:
                remaining_qty = expected - produced
                production = workorder.production_id

                _logger.warning(f"⏸ [MODÜL] Parçalı üretim tespit edildi. Yeni üretim emri açılıyor. Kalan: {remaining_qty}")

                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'product_qty': remaining_qty,
                    'product_uom_id': production.product_uom_id.id,
                    'bom_id': production.bom_id.id,
                    'origin': f"{production.name} - Split",
                    'company_id': production.company_id.id,
                })

                new_mo._generate_workorders()
                _logger.warning(f"✅ [MODÜL] Yeni üretim emri oluşturuldu: {new_mo.name} ({remaining_qty})")

        return res
