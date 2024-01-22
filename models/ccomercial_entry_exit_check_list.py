# -*- coding: utf-8 -*-
##############################################################################
#
#    Sucursal Palmares Matanzas
#    Copyright (C) 2017-TODAY Palmares (<http://intranet.var.palmares.cu).
#    Author: Raúl Sánchez(<http://intranet.var.palmares.cu>)
##############################################################################
from odoo import models, fields, api


class CcomercialEntryDocuments(models.Model):
    _name = 'ccomercial.checklist'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Documentos"


    name = fields.Char(string='Nombre del Documento', copy=False, required=1)
    document_type = fields.Selection([('entry', 'Entrada'),
                                      ('exit', 'Salida'),
                                      ('other', 'Otro'),('certificado', 'Certificado')], string='Tipo de Documento', required=1)


