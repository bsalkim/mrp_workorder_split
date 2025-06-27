def record_production(self):
    self.ensure_one()
    workorder = self
    production = workorder.production_id

    # loglama
    _logger.warning("✅ [MODÜL] record_production override edildi!")
    _logger.warning("📊 [MODÜL] Üretilen Toplam: %s, Planlanan: %s, İş Emri: %s",
                    workorder.qty_produced, production.product_qty, workorder.name)

    result = super().record_production()

    if workorder.qty_produced < production.product_qty:
        remaining_qty = production.product_qty - workorder.qty_produced
        _logger.warning("🛠️ [MODÜL] Üretim tamamlanmadı. Yeni üretim emri oluşturuluyor. Kalan: %s", remaining_qty)

        new_mo = self.env['mrp.production'].create({
            'product_id': production.product_id.id,
            'product_qty': remaining_qty,
            'product_uom_id': production.product_uom_id.id,
            'bom_id': production.bom_id.id,
            'origin': f"{production.name} - Split",
            'company_id': production.company_id.id,
            'routing_id': production.bom_id.routing_id.id if production.bom_id.routing_id else None,
        })
        new_mo._onchange_move_raw()
        new_mo._create_workorder_routing()
        _logger.warning("✅ [MODÜL] Yeni Üretim Emri oluşturuldu: %s", new_mo.name)

    return
