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

                match = re.match(r'(.*?)(-\d+)?$', production.name)
                main_number = match.group(1) if match else production.name

                # Eğer ilk defa parçalı üretim yapılıyorsa ana kaydı -001 ile güncelle
                if not match.group(2):
                    production.name = f"{main_number}-001"
                    main_number = production.name
                    _logger.warning(f"🔧 Ana üretim emrinin adı güncellendi: {main_number}")

                base_match = re.match(r'(.*?)(-\d+)?$', main_number)
                base_number = base_match.group(1) if base_match else main_number

                # Tüm dallanmalar dahil, başı base_number ile başlayanları getir
                existing_mos = self.env['mrp.production'].search([('name', 'like', f"{base_number}-%")])
                existing_suffixes = []
                for mo in existing_mos:
                    # Sadece ilk tireden sonraki sayıyı al, -001-002 gibi dallanmaları atla
                    m = re.match(rf'{re.escape(base_number)}-(\d+)(?:-.*)?$', mo.name)
                    if m:
                        existing_suffixes.append(int(m.group(1)))

                suffix = 1
                while suffix in existing_suffixes:
                    suffix += 1

                new_name = f"{base_number}-{str(suffix).zfill(3)}"

                remaining_qty = expected_qty - produced_qty

                new_mo = self.env['mrp.production'].create({
                    'product_id': production.product_id.id,
                    'bom_id': production.bom_id.id,
                    'product_qty': remaining_qty,
                    'origin': base_number,
                    'company_id': production.company_id.id,
                    'location_src_id': production.location_src_id.id,
                    'location_dest_id': production.location_dest_id.id,
                    'name': new_name,
                })

                new_mo.action_confirm()

                for new_workorder, original_workorder in zip(new_mo.workorder_ids.sorted('id'), production.workorder_ids.sorted('id')):
                    if original_workorder.qty_produced >= original_workorder.qty_production:
                        done_qty = original_workorder.qty_production
                        new_workorder.write({
                            'qty_production': done_qty,
                            'qty_produced': done_qty,
                            'state': 'done',
                        })

                production.write({'product_qty': produced_qty})

                _logger.warning(f"🆕 Yeni Üretim Emri: {new_mo.name} — Miktar: {remaining_qty}")
                _logger.warning(f"🛠 Yeni üretim emrindeki iş emirleri ayarlandı: {new_mo.workorder_ids.mapped('name')}")

        return res
