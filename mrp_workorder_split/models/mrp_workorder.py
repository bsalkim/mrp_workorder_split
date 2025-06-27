def record_production(self):
    _logger.warning("✅ [MODÜL] record_production override edildi!")
    res = super().record_production()

    for workorder in self:
        _logger.warning(f"📊 [MODÜL] {workorder.name} - Üretilen: {workorder.qty_produced}, Beklenen: {workorder.qty_to_produce}")

        if workorder.qty_produced < workorder.qty_to_produce:
            remaining_qty = workorder.qty_to_produce - workorder.qty_produced
            _logger.warning(f"⏸ [MODÜL] Parçalı üretim — kalan {remaining_qty} adet")

            production = workorder.production_id
            new_mo = self.env['mrp.production'].create({
                'product_id': production.product_id.id,
                'product_qty': remaining_qty,
                'product_uom_id': production.product_uom_id.id,
                'bom_id': production.bom_id.id,
                'origin': f"{production.name} - Split",
                'company_id': production.company_id.id,
            })

            new_mo._generate_workorders()
            _logger.warning(f"✅ [MODÜL] Yeni üretim emri oluşturuldu: {new_mo.name} ({remaining_qty} adet)")

    return res
