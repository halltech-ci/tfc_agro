# -*- coding: utf-8 -*-

from odoo import models, fields, api

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

picking_code = ['outgoing', 'incoming', 'internal']
class StockPicking(models.Model):
    _inherit="stock.picking"
    
    driver_name = fields.Char(string='Driver Name', related = 'group_id.sale_id.driver_name')
    vehicle_number = fields.Char(string='Vehicle Number', related='group_id.sale_id.vehicle_number')
    driver_contacts = fields.Char(string="Driver Phone Number", related='group_id.sale_id.driver_contacts')
    driver_company = fields.Char(string="Driver Company")
    chargeur = fields.Char(string="Chargeur")
    
    
    
    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
            #vals['name'] = self.env['ir.sequence'].next_by_code('stock.outgoing.sequence') or _('/')
            code = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).code
            #code = picking_code.get('picking_type_code') 
            if code == 'outgoing':
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.outgoing.sequence')
            elif code == 'incoming':
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.incoming.sequence')
            elif code == 'internal':
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.internal.sequence')
            else:
                vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
            
        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals.get('move_lines', []) + vals.get('move_ids_without_package', []):
                if len(move) == 3 and move[0] == 0:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        res = super(StockPicking, self).create(vals)
        res._autoconfirm_picking()
        return res

    
    '''
    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
            #vals['name'] = self.env['ir.sequence'].next_by_code('stock.outgoing.sequence') or _('/')
            if not vals.get('sale_id', False):
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.outgoing.sequence') or _('/')
            if not vals.get('purchase_id', False):
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.incoming.sequence') or _('/')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.internal.sequence') or _('/')
    

        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals.get('move_lines', []) + vals.get('move_ids_without_package', []):
                if len(move) == 3 and move[0] == 0:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']
        res = super(StockPicking, self).create(vals)
        res._autoconfirm_picking()
        return res
    '''

