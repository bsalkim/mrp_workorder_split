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
                _logger.warning("🔁 Parçalı üretim tespit edildi. Üretim emri draft'a çekilip bölünecek...")

                # İş emirlerini iptal et
                production.workorder_ids.write({'state': 'cancel'})

                # Üretim emrini draft'a çek
                production.write({'state': 'draft'})

                # Split işlemini tetikle
                split_wizard = self.env['mrp.production.split'].create({
                    'production_id': production.id,
                    'split_qty': produced_qty,
                })
                split_wizard.do_split()

                _logger.warning("✅ Split işlemi tamamlandı, üretim emri tekrar başlatılıyor...")

                # Üretim emrini tekrar onayla
                production.action_confirm()

        return res
