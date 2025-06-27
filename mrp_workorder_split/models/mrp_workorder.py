import logging
from odoo import models

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        for workorder in self:
            _logger.warning(f"✅ [MODÜL] record_production override edildi — {workorder.name}")

            production = workorder.production_id
            total_produced = sum(production.workorder_ids.mapped('qty_producing'))
            expected_qty = production.product_qty

            _logger.warning(f"📊 Üretilen: {total_produced}, Planlanan: {expected_qty}, İş Emri: {workorder.name}")

            # İlk veya son iş emri değilse ve üretim tam değilse üretim emrini böl
            if total_produced < expected_qty:
                workorders = production.workorder_ids
                if workorder != workorders[0] and workorder != workorders[-1]:
                    remaining_qty = expected_qty - total_produced
                    if remaining_qty > 0:
                        new_mo = production.copy({
                            'product_qty': remaining_qty,
                            'origin': f"{production.name} - Bölme",
                        })
                        _logger.warning(f"✂️ Yeni üretim emri oluşturuldu: {new_mo.name} — Miktar: {remaining_qty}")

                        # İş emirlerini oluştur
                        new_mo._create_workorder()
        # Varsayılan davranışla devam et
        return super(MrpWorkorder, self).record_production()
