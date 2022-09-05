from odoo import api, models, fields, _

class BaseStructure(models.AbstractModel):
    _inherit = 'mdc.base.structure'

    @api.multi
    def _get_chkpoint_categ_selection(self):
        categ_list = super()._get_chkpoint_categ_selection()
        categ_list.append(('CRUMBS', _('Crumbs')))
        return categ_list

class Workstation(models.Model):

    _inherit = 'mdc.workstation'

    crumbs_seat = fields.Boolean(
        'Crumbs Seat',
        default=False)
