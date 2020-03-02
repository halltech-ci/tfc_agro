# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

# class tfc_custom(models.Model):
#     _name = 'tfc_custom.tfc_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class SaleOrder(models.Model):
    _inherit='sale.order'
    
    
    vehicle_number=fields.Char(string='Vehicle Number')
    driver_name=fields.Char(string="Driver Name")
    driver_contacts=fields.Char(string="Driver Contact")
    customer_order_ref=fields.Char(string="Customer Order Ref")
    sale_approver=fields.Many2one('res.users', string="Approver")
    
    #Lot methods
    @api.model
    def get_move_from_line(self, line):
        move = self.env['stock.move']
        # i create this counter to check lot's univocity on move line
        lot_count = 0
        for p in line.order_id.picking_ids:
            for m in p.move_lines:
                move_line_id = m.move_line_ids.filtered(
                    lambda line: line.lot_id)
                if move_line_id and line.lot_id == move_line_id[:1].lot_id:
                    move = m
                    lot_count += 1
                    # if counter is 0 or > 1 means that something goes wrong
                    if lot_count != 1:
                        raise UserError(_('Can\'t retrieve lot on stock'))
        return move

    @api.model
    def _check_move_state(self, line):
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state == 'confirmed':
                move._action_assign()
                move.refresh()
            if move.state != 'assigned':
                raise UserError(_('Can\'t reserve products for lot %s') %
                                line.lot_id.name)
        return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self.with_context(sol_lot_id=True))\
            .action_confirm()
        for line in self.order_line:
            if line.lot_id:
                unreserved_moves = line.move_ids.filtered(
                    lambda move: move.product_uom_qty !=
                    move.reserved_availability
                )
                if unreserved_moves:
                    raise UserError(
                        _('Can\'t reserve products for lot %s')
                        % line.lot_id.name
                    )
            self._check_move_state(line)
        return res
    
    
    
    #Inherit create method to add custom sequence in sale order
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order.sequence') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.sequence') or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result
    
class SaleOrderLine(models.Model):
    _inherit='sale.order.line'
    
    lot_id=fields.Many2one('stock.production.lot', string='Lot', copy=False)
    lot_quantity=fields.Float(string="Quantity in Lot", related='lot_id.product_qty', default=1.00, 
                              required=True, digits=dp.get_precision('Product Unit of Measure')
    )
    amount_letter=fields.Text(string='Montant en lettre')
        
    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids=[] #On itialise la liste des lots disponible
            
        #Si le produit existe et il existe un entrepot pour le devis
        if self.product_id and self.order_id.warehouse_id:
            #Je recupere le nom du stock
            location = self.order_id.warehouse_id.lot_stock_id
            #product_quantity = self.lot_quantity#product qty in sale order line
            quants = self.env['stock.quant'].read_group([
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', location.id),
                ('quantity', '>', 0),
                ('lot_id', '!=', False)
                ], ['lot_id'], 'lot_id')           
            available_lot_ids = [quant['lot_id'][0] for quant in quants]
        self.lot_id = False
        return {
            'domain':{'lot_id':[('id', 'in', available_lot_ids)]}
        }
    #When choose one lot we compare qty in lot and orderd qty
    '''
    @api.onchange('lot_id')
    def _compare_product_qty_in_lot(self):
        if self.product_uom.id != self.lot_id.product_uom_id.id:
            raise UserError(_('Quantity in lot must be greater than ordered quantity'))
        if self.product_uom_qty > self.lot_id.product_qty:
            raise UserError(_('Quantity in lot must be greater than ordered quantity'))
        return
             
    '''     
            
        
    
