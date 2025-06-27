from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        _logger.info(f"💡 [MODÜL ÇALIŞTI] Workorder: {self.name} - Produced: {self.qty_produced} / Planned: {self.qty_to_produce}")
        res = super().record_production()
        for workorder in self:
            produced_qty = workorder.qty_produced
            planned_qty = workorder.qty_to_produce

            if produced_qty < planned_qty:
                remaining_qty = planned_qty - produced_qty
                _logger.info(f"⏳ Yeni iş emri oluşturuluyor: Kalan {remaining_qty} adet")
                self.env['mrp.workorder'].create({
                    'production_id': workorder.production_id.id,
                    'operation_id': workorder.operation_id.id,
                    'workcenter_id': workorder.workcenter_id.id,
                    'qty_to_produce': remaining_qty,
                    'qty_produced': 0,
                })
        return res
