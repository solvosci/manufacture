# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.mdc.controllers.check_point import CheckPoint
from datetime import date

_logger = logging.getLogger(__name__)

class CrumbsCheckPoint(CheckPoint):
    
    @http.route("/mdc/cp/crumbs/<int:chkpoint_id>", type='http', auth='none')
    def cp_crumbs(self, chkpoint_id, **kwargs):
        try:
            _logger.info("[cp_crumbs] Page requested for chkpoint_id=%d" % chkpoint_id)
            cp_user = self._get_cp_user_and_lang_context(request)
            # TODO this is the first non-dependent ws page, this is a workaround
            #ws_session_data = ws_rfid_server.get_session_data(request.env, simul=('rfidsimul' in kwargs))
            ws_session_data = {
                'simul': True,
                'session_id': 'fake',
                'wsapi_url': 'fake'
            }
            chkpoint = request.env['mdc.chkpoint'].sudo(cp_user).browse(chkpoint_id)
            client_ip = self._get_client_ip()
            #self._check_client(checkpoint=chkpoints, client_ip=client_ip, simul=ws_session_data['simul'])
            shifts = request.env['mdc.shift'].sudo(cp_user).search([], order='shift_code')
            current_date = date.today()
            # TODO move to method, since is used later in cp_crumbs_lotactive() method
            lots = request.env['mdc.lot'].sudo(cp_user).search(
                ['|', '&', '&',('start_date','<=',current_date), ('finished','=',False), ('end_date','>=',current_date),
                      '&', '&',('start_date','<=',current_date), ('finished','=',False), ('end_date','=',False)
                ], order='name')
            #employees = request.env['mdc.workstation'].sudo(cp_user).search([('line_id', '=', 'la de migas')], order='code')
            # TODO employees sort?
            employees = request.env['mdc.workstation'].sudo().search(
                ['&',('line_id','=', chkpoint.line_id.id),('crumbs_seat', '=', True)]
            ).mapped("current_employee_id")
            return request.render(
                'mdc_crumbs.chkpoint_crumbs',
                {'title': chkpoint.name, 
                 'chkpoints': chkpoint, 
                 'shifts': shifts,
                 'lots': lots,
                 'employees': employees,
                 'ws_session_data': ws_session_data,
                 'client_ip': client_ip
                 }
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route("/mdc/cp/crumbs/<int:chkpoint_id>/employee", type='json', auth='none')
    def cp_crumbs_employee(self, chkpoint_id, **kwargs):
        cp_user = self._get_cp_user_and_lang_context(request)
        shift = request.jsonrequest['shift']
        chkpoint = request.env['mdc.chkpoint'].sudo(cp_user).browse(chkpoint_id)
        employees = request.env['mdc.workstation'].sudo().search(
            [('line_id','=', chkpoint.line_id.id),('crumbs_seat','=', True),('shift_id', '=', shift)],
            limit=12
        ).mapped("current_employee_id").sorted(key=lambda x: x.name)
        employees_return = []

        for employee in employees:
            employees_return.append((employee.id, employee.name, employee.workstation_id.id))
        return json.dumps(employees_return)
        
    @http.route("/mdc/cp/crumbs/<int:chkpoint_id>/lotactive", type='json', auth='none')
    def cp_crumbs_lotactive(self, chkpoint_id):
        cp_user = self._get_cp_user_and_lang_context(request)
        lots = request.env['mdc.lot'].sudo(cp_user).search(
        ['|', '&', '&',('start_date','<=',date.today()), ('finished','=',False), ('end_date','>=',date.today()),
                '&', '&',('start_date','<=',date.today()), ('finished','=',False), ('end_date','=',False)
        ], order='name')

        lots_return = {}
        for lot in lots:
            # TODO "XXXcode" key, why not use JSON nested structure?
            lots_return.update({lot.id: lot.name, str(lot.id) + "code": lot.lot_code})
        return json.dumps(lots_return)

    @http.route("/mdc/cp/crumbs/<int:chkpoint_id>/createCrumb", type='json', auth='none')
    def cp_crumbs_create(self, chkpoint_id, **kwargs):
        # TODO change method name
        cp_user = self._get_cp_user_and_lang_context(request)
        created = True
        data = dict(request.jsonrequest)
        createdJson = {}
        # TODO "Cleansed" typo
        # TODO this method has a lot of repeated code, bad practice
        if data['type'] == "NotCleansed":
            data['chkpoint_id'] = chkpoint_id
            data['product_id'] = request.env['mdc.lot'].sudo(cp_user).browse(int(data['lot'])).product_id.id
            DataCrumbs = request.env['mdc.data_crumbs'].sudo(cp_user)
            dataCrumbs = DataCrumbs.from_cp_create(data)
            if 'error' in dataCrumbs:
                createdJson['error'] = dataCrumbs['error']
                created = False

        elif data['type'] == "Cleansed":
            data['chkpoint_id'] = chkpoint_id
            DataCrumbs = request.env['mdc.data_crumbs'].sudo(cp_user)
            dataCrumbs = DataCrumbs.from_cp_update(data)
            if 'error' in dataCrumbs:
                createdJson['error'] = dataCrumbs['error']
                created = False

        # TODO this method has a lot of repeated code, bad practice
        if(created):
            if dataCrumbs["clean_weight"]:
                createdJson = {
                    'created': created,
                    'weight': "{0:.2f}".format(dataCrumbs["clean_weight"]),
                }
            else:
                createdJson = {
                    'created': created,
                    'weight': "{0:.2f}".format(dataCrumbs["gross_weight"]),
                }


        return createdJson
    