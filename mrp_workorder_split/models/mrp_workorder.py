import logging
from odoo import models

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        self.ensure_one()
        _logger.warning(f"✅ [MODÜL] record_production override edildi — {self.name}")

        production = self.production_id
        produced = self.qty_producing
        expected = production.product_qty
        _logger.warning(f"📊 Üretilen: {produced}, Planlanan: {expected}, İş Emri: {self.name}")

        # Standart üretim işlemini yap
        result = super().record_production()

        # Parçalı üretim kontrolü (sadece son iş emri değilse ve eksik üretildiyse)
        if produced < expected and not self == production.workorder_ids[-1]:
            _logger.warning("🔁 Parçalı üretim tespit edildi. MO bölme işlemi başlatılıyor.")

            # Üretim emrini kopyalıyoruz
            defaults = {
                'product_qty': expected - produced,
                'origin': production.name,
            }
            _logger.warning(f"📎 Üretim Emri Kopyalanıyor... {production.name}")
            new_mo = production.copy(default=defaults)

            _logger.warning(f"✅ Yeni Üretim Emri: {new_mo.name} | Miktar: {new_mo.product_qty}")

            # Yeni üretim emrini aktive et
            new_mo.action_confirm()
            new_mo.action_assign()
            new_mo._create_workorder_lines()
            _logger.warning(f"🛠 Yeni üretim emrinde iş emirleri oluşturuldu: {new_mo.workorder_ids.mapped('name')}")

        return result
