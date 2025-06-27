from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        res = super().record_production()

        for workorder in self:
            production = workorder.production_id
            planned_qty = production.product_qty

            # Toplam üretilen miktarı hesapla
            total_produced = sum(production.workorder_ids.mapped('qty_produced'))

            if total_produced < planned_qty:
                _logger.warning(f"⏸ Parçalı üretim tespit edildi: {total_produced}/{planned_qty}")

                # Üretim emrinin yeni kopyasını oluştur
                remaining_qty = planned_qty - total_produced
                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'product_qty': remaining_qty,
                    'product_uom_id': production.product_uom_id.id,
                    'bom_id': production.bom_id.id,
                    'origin': f"{production.name} - Split",
                    'company_id': production.company_id.id,
                })

                # Yeni üretim emri için iş emirleri oluştur
                new_mo._generate_workorders()

                _logger.warning(f"✅ Yeni üretim emri oluşturuldu: {new_mo.name} ({remaining_qty} adet)")

        return res
