from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.model
    def record_production(self):
        _logger.warning("✅ [MODÜL] record_production override edildi — %s", self.name)

        for workorder in self:
            production = workorder.production_id
            produced_qty = sum(workorder.qty_produced for workorder in production.workorder_ids)
            expected = production.product_qty
            _logger.warning("📊 Üretilen: %s, Planlanan: %s, İş Emri: %s", produced_qty, expected, workorder.name)

            # Eğer tamamı üretildiyse ya da son iş emri değilse, bir şey yapma
            if production.state != 'progress':
                _logger.warning("⏭ Üretim emri aktif değil, bölme işlemi atlandı.")
                return super().record_production()

            if produced_qty >= expected:
                _logger.warning("✅ Tüm miktar zaten üretildi, bölme yapılmayacak.")
                return super().record_production()

            # Üretim emrini böl
            remaining_qty = expected - produced_qty
            _logger.warning("✂ Üretim emri bölünüyor... Kalan miktar: %s", remaining_qty)

            routing = production.bom_id.routing or production.routing_id
            new_mo = production.copy({
                'product_qty': remaining_qty,
                'origin': f"{production.name} (Devam)",
                'state': 'confirmed',
                'workorder_ids': False,
                'qty_produced': 0.0,
                'qty_producing': 0.0,
                'move_raw_ids': False,
                'move_finished_ids': False,
                'date_planned_start': production.date_planned_start,
                'date_planned_finished': production.date_planned_finished,
                'bom_id': production.bom_id.id,
                'routing_id': routing.id if routing else None,
            })

            _logger.warning("🆕 Yeni üretim emri oluşturuldu: %s", new_mo.name)

            new_mo._onchange_move_raw()
            new_mo._create_update_move_finished()
            new_mo._create_workorders()

        return super().record_production()
