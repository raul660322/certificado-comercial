# -*- coding: utf-8 -*-
##############################################################################
#
#    Sucursal Palmares Matanzas
#    Copyright (C) 2017-TODAY Palmares (<http://intranet.var.palmares.cu).
#    Author: Raúl Sánchez(<http://intranet.var.palmares.cu>)
##############################################################################
from datetime import datetime,date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import operator

class HrCertificadoComercial(models.Model):
    _name = 'hr.certificado.comercial'
    _description = 'HR Certificados Comerciales'

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.expiry_date and i.mensaje:
                exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=90)
                if date_now >= exp_date:
                    mail_content = "  Estimado  " + i.employee_ref.name + ",<br>Su Certificado " + i.name + " de " + i.dpto_ref.name+ " vence en " + \
                                   str(i.expiry_date) + ". Por favor, debe renovarlo antes de la fecha de vencimiento"
                    main_content = {
                        'subject': _('Certificado-%s de %s Vence en %s') % (i.name, i.dpto_ref.name, i.expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee_ref.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            exp_date = fields.Date.from_string(each.expiry_date)
            if exp_date < date.today():
                raise Warning('Este certificado ha vencido.')
    
    name = fields.Char(string='Referencia', required=True, copy=False)
    document_name = fields.Many2one('ccomercial.checklist', string='Activ. Fundamental', required=True)
    otra_actividad=fields.Many2one('ccomercial.checklist', string='Otra')
    description = fields.Text(string='Descripción', copy=False)
    expiry_date = fields.Date(string='Fecha de Vencimiento', copy=False)
    employee_ref = fields.Many2one('hr.employee', domain="[('es_precios_dpto', '=', True)]", required=True, index=True, copy=False, string="Responsable")
    dpto_ref=fields.Many2one('hr.department', invisible=0, required=True, index=True, copy=False, string="Instalación")
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Adjunto",
                                         help='Aqui puede adjuntar sus documentos', copy=False)
    issue_date = fields.Date(string='Fecha de Emisión', default=fields.datetime.now(), copy=False)
    dias = fields.Integer(compute='_compute_dias', string='Fecha Advertencia', search='_value_search')
    mensaje = fields.Boolean(string='Enviar Mensaje',required=False,readonly=False,index=False,default=True)
    tomo=fields.Char(string=u'Tomo', size=4)
    folio = fields.Char(string=u'Folio', size=4)
    asiento = fields.Char(string=u'Asiento', size=4)
    direccion=fields.Text(string='Direccion',related='dpto_ref.direccion')
    

    @api.depends('expiry_date')
    def _compute_dias(self):
        for record in self:
            today = fields.Date.from_string(fields.Date.today())
            renew_date = fields.Date.from_string(record.expiry_date)
            diff_time = (renew_date - today).days
            record.dias = diff_time

    @api.multi
    def _value_search(self,operador,value):
        op={"==" : operator.eq ,"<":operator.lt,">":operator.ge}
        funcion=op[operador]
        recs=self.search([]).filtered(lambda x: funcion(x.dias, value))
        if recs:
            return [('id','in',[x.id for x in recs])]  


class HrEmployeePrecios(models.Model):
    _inherit = 'hr.employee'
    es_precios_dpto=fields.Boolean(string='Lleva Precios',required=False,readonly=False,index=False,default=False)


class HrDpto(models.Model):
    _inherit = 'hr.department'

    @api.multi
    @api.depends('document_ids')
    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.certificado.comercial'].search([('dpto_ref', '=', each.id)])
            each.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        domain = [
            ('dpto_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.certificado.comercial',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click para crear nuevos documentos
                        </p>'''),
            'limit': 80,
            'context': "{'dpto_visible': False, 'default_dpto_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Certificados', store=True)
    tipo = fields.Selection(
        string='Tipo',
        required=True,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('venta','Venta'), ('administracion','Administracion')]
    )
    direccion = fields.Text(string='Direccion')
    document_ids=fields.One2many(comodel_name='hr.certificado.comercial', inverse_name='dpto_ref')
   

class HrCcomercialAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.certificado.comercial', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Adjunto", invisible=1)
