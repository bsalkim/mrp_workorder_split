from odoo import models
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        res = super().record_production()

        for workorder in self:
            production = workorder.production_id
            produced = workorder.qty_produced
            expected = workorder.qty_production  # float değer
            operations = production.workorder_ids.sorted(key=lambda w: w.operation_id.sequence)

            _logger.warning(f"✅ [MODÜL] record_production override edildi — {workorder.name}")
            _logger.warning(f"📊 Üretilen: {produced}, Planlanan: {expected}, İş Emri: {workorder.name}")

            if expected == 0 or produced >= expected:
                continue  # tam üretim yapıldı, işlem yok

            if len(operations) < 3:
                continue  # ortadaki iş emri değilse işlem yapma

            if workorder == operations[0] or workorder == operations[-1]:
                _logger.warning("🔕 İlk veya son iş emri — üretim bölünmeyecek.")
                continue  # ilk veya son değilse devam et

            # Parçalı üretim ortadaki bir iş emrinde gerçekleşti
            remaining_qty = expected - produced
            _logger.warning(f"🛠 Parçalı üretim ortada — {remaining_qty} adetlik yeni üretim emri oluşturulacak.")

            routing = production.bom_id.routing_id
            new_mo = self.env['mrp.production'].create({
                'product_id': production.product_id.id,
                'product_qty': remaining_qty,
                'bom_id': production.bom_id.id,
                'product_uom_id': production.product_uom_id.id,
                'origin': f"{production.name} - Kalan",
                'company_id': production.company_id.id,
                'routing_id': routing.id if routing else None,
            })

            _logger.warning(f"📦 Yeni üretim emri oluşturuldu: {new_mo.name} ({remaining_qty} adet)")

            new_mo._create_workorder()

        return res
