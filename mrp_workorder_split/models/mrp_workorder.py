import logging
from odoo import models

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self, *args, **kwargs):
        _logger.warning(f"✅ [MODÜL] record_production override edildi — {self.name}")

        res = super().record_production(*args, **kwargs)

        for workorder in self:
            production = workorder.production_id
            expected_qty = workorder.qty_production
            produced_qty = workorder.qty_produced

            _logger.warning(f"📊 Üretilen: {produced_qty}, Planlanan: {expected_qty}, İş Emri: {workorder.name}")

            workorders = production.workorder_ids.sorted('id')
            if workorder != workorders[0] and workorder != workorders[-1] and 0 < produced_qty < expected_qty:
                _logger.warning("🔁 Parçalı üretim tespit edildi. Yeni üretim emri kopyalanıyor...")

                remaining_qty = expected_qty - produced_qty

                new_mo = production.copy({
                    'product_qty': remaining_qty,
                    'origin': f"{production.name} - Kalan",
                    'workorder_ids': False,
                })

                new_mo.action_confirm()

                for new_workorder, original_workorder in zip(new_mo.workorder_ids.sorted('id'), production.workorder_ids.sorted('id')):
                    if original_workorder.state == 'done':
                        new_workorder.qty_production = 0
                        new_workorder.qty_produced = 0
                        new_workorder.write({'state': 'done'})
                    elif original_workorder.qty_produced > 0:
                        remaining_in_workorder = original_workorder.qty_production - original_workorder.qty_produced
                        new_workorder.qty_production = remaining_in_workorder

                _logger.warning(f"🆕 Yeni Üretim Emri: {new_mo.name} — Miktar: {remaining_qty}")
                _logger.warning(f"🛠 Yeni üretim emrindeki iş emirleri ayarlandı: {new_mo.workorder_ids.mapped('name')}")

        return res
