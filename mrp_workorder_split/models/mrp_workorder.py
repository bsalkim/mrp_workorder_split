import logging
from odoo import models
import re

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

                # Ana üretim numarasını bul
                match = re.match(r'(.*?)(-\d+)?$', production.name)
                base_name = match.group(1) if match else production.name

                # Var olan kopyaları bul
                existing_mos = self.env['mrp.production'].search([('name', 'like', f"{base_name}-%")])
                existing_suffixes = []
                for mo in existing_mos:
                    m = re.match(rf'{re.escape(base_name)}-(\d+)$', mo.name)
                    if m:
                        existing_suffixes.append(int(m.group(1)))

                suffix = 1
                while suffix in existing_suffixes:
                    suffix += 1

                new_name = f"{base_name}-{str(suffix).zfill(3)}"

                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'bom_id': production.bom_id.id,
                    'product_qty': remaining_qty,
                    'origin': base_name,
                    'company_id': production.company_id.id,
                    'location_src_id': production.location_src_id.id,
                    'location_dest_id': production.location_dest_id.id,
                    'name': new_name,
                })

                new_mo.action_confirm()

                # Tamamlanmış iş emirlerini güncelle
                for new_workorder, original_workorder in zip(new_mo.workorder_ids.sorted('id'), production.workorder_ids.sorted('id')):
                    if original_workorder.qty_produced >= original_workorder.qty_production:
                        done_qty = original_workorder.qty_production
                        new_workorder.write({
                            'qty_production': done_qty,
                            'qty_produced': done_qty,
                            'state': 'done',
                        })

                # Ana üretim emrinin miktarını kalan adete güncelle
                production.write({'product_qty': produced_qty})

                _logger.warning(f"🆕 Yeni Üretim Emri: {new_mo.name} — Miktar: {remaining_qty}")
                _logger.warning(f"🛠 Yeni üretim emrindeki iş emirleri ayarlandı: {new_mo.workorder_ids.mapped('name')}")

        return res
