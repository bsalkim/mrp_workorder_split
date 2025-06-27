from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        _logger.warning("🧪 MODÜL TEST — button_finish() çalıştı")
        return super().button_finish()

    def action_done(self):
        _logger.warning("🧪 MODÜL TEST — action_done() çalıştı")
        return super().action_done()

    def action_finish(self):
        _logger.warning("🧪 MODÜL TEST — action_finish() çalıştı")
        return super().action_finish()

    def action_end(self):
        _logger.warning("🧪 MODÜL TEST — action_end() çalıştı")
        return super().action_end()

    def mark_done(self):
        _logger.warning("🧪 MODÜL TEST — mark_done() çalıştı")
        return super().mark_done()
