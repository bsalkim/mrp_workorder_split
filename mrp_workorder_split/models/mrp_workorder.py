from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        _logger.warning("✅ [MODÜL] record_production override edildi!")
        res = super().record_production()

        for workorder in self:
            production = workorder.production_id
            planned_qty = production.product_qty
            total_produced = sum(production.workorder_ids.mapped('qty_produced'))

            _logger.warning(f"📊 [MODÜL] Üretilen Toplam: {total_produced}, Planlanan: {planned_qty}, İş Emri: {workorder.name}")

            if total_produced < planned_qty:
                remaining_qty = planned_qty - total_produced

                _logger.warning(f"⏸ [MODÜL] Parçalı üretim tespit edildi — kalan {remaining_qty} adet")

                # Aynı ürün için yeni üretim emri oluştur
                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'product_qty': remaining_qty,
                    'product_uom_id': production.product_uom_id.id,
                    'bom_id': production.bom_id.id,
                    'origin': f"{production.name} - Split",
                    'company_id': production.company_id.id,
                })

                new_mo._generate_workorders()
                _logger.warning(f"✅ [MODÜL] Yeni üretim emri oluşturuldu: {new_mo.name} ({remaining_qty} adet)")

        return res
