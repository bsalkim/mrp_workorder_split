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

                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'bom_id': production.bom_id.id,
                    'product_qty': remaining_qty,
                    'origin': f"{production.name} - Kalan",
                    'company_id': production.company_id.id,
                    'location_src_id': production.location_src_id.id,
                    'location_dest_id': production.location_dest_id.id,
                })

                new_mo.action_confirm()

                for new_workorder, original_workorder in zip(new_mo.workorder_ids.sorted('id'), production.workorder_ids.sorted('id')):
                    if original_workorder.qty_produced >= original_workorder.qty_production:
                        new_workorder.qty_production = 0
                        new_workorder.qty_produced = 0
                        new_workorder.write({
                            'state': 'done',
                            'qty_production': 0
                        })

                _logger.warning(f"🆕 Yeni Üretim Emri: {new_mo.name} — Miktar: {remaining_qty}")
                _logger.warning(f"🛠 Yeni üretim emrindeki iş emirleri ayarlandı: {new_mo.workorder_ids.mapped('name')}")

        return res
