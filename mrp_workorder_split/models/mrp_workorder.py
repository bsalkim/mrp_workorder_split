from odoo import models, api
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.model
    def record_production(self):
        workorder = self

        self.env['ir.logging'].create({
            'name': "MRP SPLIT",
            'type': 'server',
            'level': 'WARNING',
            'dbname': self._cr.dbname,
            'message': f"✅ [MODÜL] record_production override edildi — {workorder.name}",
            'path': __name__,
            'line': 0,
            'func': 'record_production'
        })

        production = workorder.production_id
        expected_qty = workorder.qty_production
        produced_qty = workorder.qty_produced

        self.env['ir.logging'].create({
            'name': "MRP SPLIT",
            'type': 'server',
            'level': 'WARNING',
            'dbname': self._cr.dbname,
            'message': f"📊 Üretilen: {produced_qty}, Planlanan: {expected_qty}, İş Emri: {workorder.name}",
            'path': __name__,
            'line': 0,
            'func': 'record_production'
        })

        # Sadece parçalı üretim ve ilk/son dışında iş emrindeysek böl
        if 0 < produced_qty < expected_qty:
            self.env['ir.logging'].create({
                'name': "MRP SPLIT",
                'type': 'server',
                'level': 'WARNING',
                'dbname': self._cr.dbname,
                'message': f"🔁 Parçalı üretim tespit edildi. Üretim emri bölünüyor...",
                'path': __name__,
                'line': 0,
                'func': 'record_production'
            })

            remaining_qty = expected_qty - produced_qty

            # Yeni üretim emri oluştur
            new_mo = self.env['mrp.production'].create({
                'product_id': production.product_id.id,
                'bom_id': production.bom_id.id,
                'product_qty': remaining_qty,
                'origin': f"{production.name} - Kalan",
                'company_id': production.company_id.id,
                'location_src_id': production.location_src_id.id,
                'location_dest_id': production.location_dest_id.id,
            })

            new_mo.action_confirm()
            new_mo._generate_workorders()

        return super().record_production()
