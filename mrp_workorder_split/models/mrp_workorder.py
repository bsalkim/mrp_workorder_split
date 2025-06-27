from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        _logger.info(f"✅ [MODÜL ÇALIŞTI] Bitir'e basıldı: {self.name} - {self.qty_produced}/{self.qty_to_produce}")
        
        # Orijinal işlevi çağır
        res = super().button_finish()

        for workorder in self:
            produced_qty = workorder.qty_produced
            planned_qty = workorder.qty_to_produce

            if produced_qty < planned_qty:
                remaining_qty = planned_qty - produced_qty
                _logger.info(f"➕ Yeni iş emri oluşturuluyor: {remaining_qty} adet")
                self.env['mrp.workorder'].create({
                    'production_id': workorder.production_id.id,
                    'operation_id': workorder.operation_id.id,
                    'workcenter_id': workorder.workcenter_id.id,
                    'qty_to_produce': remaining_qty,
                    'qty_produced': 0,
                })

        return res
