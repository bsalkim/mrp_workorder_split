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

                _logger.warning(f"➕ Yeni iş emri oluşturuluyor — {workorder.name} | Kalan: {remaining_qty}")

                self.env['mrp.workorder'].create({
                    'production_id': workorder.production_id.id,
                    'operation_id': workorder.operation_id.id,
                    'workcenter_id': workorder.workcenter_id.id,
                    'qty_produced': 0,
                    'state': 'ready',  # işleme hazır hale getirebilirsin
                })

        return res
