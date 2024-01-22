# -*- coding: utf-8 -*-
import datetime

import dateutil
from dateutil import relativedelta

from odoo import models, fields, api
import xlsxwriter
from odoo.addons.xlsx_report_base.models.base_xlsx_report_model import ReportXlsx

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class CertReport(ReportXlsx):
    def build_xlsx_report(self, workbook, data, objs):
        divisiones_query =  """SELECT div.id as id_division, div.name as nombre_division FROM ventas_division as div"""
        self.env.cr.execute(divisiones_query)
        division_map = self.env.cr.dictfetchall()

        bold = workbook.add_format({'bold': 1, 'border': True})
        bold_only = workbook.add_format({'bold': 1})
        borde = workbook.add_format({'border': True})
        centrado = format = workbook.add_format({'border': True})
        format.set_text_wrap()

        format = workbook.add_format({'border': True})
        format.set_text_wrap()
        # format.set_bold(1)
        format.set_align('center')
        format.set_align('vcenter')
        
        dos_decimal_bold=workbook.add_format({'bold': 1,'num_format':'0.00'})
        dos_decimal=workbook.add_format({'num_format':'0.00'})
        numero=1
        for division in division_map:
            worksheet = workbook.add_worksheet(division['nombre_division'])

            i = 4

            worksheet.merge_range(0, 0, 0, 5, 'Palmares Sucursal Matanzas', bold_only)
            worksheet.merge_range(1, 0, 1, 5, 'REGISTRO PARA EL CONTROL DE CERTIFICADOS Y AUTORIZACIONES COMERCIALES', bold_only)
            worksheet.write(1, 17, 'Fecha: %s' % data['current_date'].strftime("%d/%m/%Y"))
            worksheet.write(2, 0, 'División: %s' % division['nombre_division'])

            # Tabla
            # worksheet.merge_range(3, 2, 3, 4, 'Diario', format)
            # worksheet.merge_range(i, 0, i, 1, 'Departamentos', format)
            worksheet.write(i, 0, 'No.', format)
            worksheet.write(i, 1, 'Instalación', format)
            worksheet.write(i, 2, 'Dirección', format)

            worksheet.write(i, 3, 'No. de Cert.', format)
            worksheet.write(i, 4, 'Act. Fund', format)
            worksheet.write(i, 5, 'Otra Act.', format)
            worksheet.write(i, 6, 'F. de Emis.', format)
            worksheet.write(i, 7, 'F. de Venc.', format)
            worksheet.write(i, 8, 'Tomo', format)

            worksheet.write(i, 9, 'Folio', format)
            worksheet.write(i, 10, 'Asiento', format)
            worksheet.write(i, 11, 'Observ', format)
            worksheet.set_column(1,1,15)
            worksheet.set_column(2,2,25)
            worksheet.set_column(4,7,15)
            worksheet.set_column(11,11,25)
            i = 5
            # Crear lista de departamentos
            dpto_query =  """SELECT dpto.id as id_dpto, dpto.name as nombre_dpto, dpto.direccion as dir_dpto, dpto.document_count as cantidad 
                             FROM hr_department as dpto 
                             WHERE dpto.division_id=%s   
                          """ %(division['id_division'])
            self.env.cr.execute(dpto_query)
            dpto_map = self.env.cr.dictfetchall()
            
            for dpto in dpto_map:
                cert_query="""SELECT cc.name as ref, cl.name as afund, cl1.name as oact, 
                              cc.description as observ, cc.issue_date emitido, cc.expiry_date as vence,
                              cc.tomo as tomo, cc.folio as folio, cc.asiento as asiento 
                              FROM hr_certificado_comercial as cc
                              LEFT JOIN ccomercial_checklist as cl ON cc.document_name=cl.id
                              LEFT JOIN ccomercial_checklist as cl1 ON cc.otra_actividad=cl1.id
                              WHERE dpto_ref=%s 
                           """ %(dpto['id_dpto'])
                self.env.cr.execute(cert_query)
                cert_map = self.env.cr.dictfetchall()
                
                d_final=dpto['cantidad']
                if d_final:
                    worksheet.merge_range(i, 0, i+d_final-1, 0, numero ,format)
                    worksheet.merge_range(i, 1, i+d_final-1, 1, dpto["nombre_dpto"],format)
                    worksheet.merge_range(i, 2, i+d_final-1, 2, dpto["dir_dpto"],format)
                    for cert in cert_map:
                        worksheet.write(i, 3, cert['ref'],format)
                        worksheet.write(i, 4, cert['afund'],format)   
                        worksheet.write(i, 5, cert['oact'],format)
                        worksheet.write(i, 6, cert['emitido'],format)   
                        worksheet.write(i, 7, cert['vence'],format)   
                        worksheet.write(i, 8, cert['tomo'],format)
                        worksheet.write(i, 9, cert['folio'],format)  
                        worksheet.write(i, 10, cert['asiento'],format)
                        worksheet.write(i, 11, cert['observ'],format)  
                        i+=1
                    numero+=1
                         

#             listaFilas=[]
#             laCadena='=SUM('

#             for id_unidad, unidad in division["unidades"].iteritems():
#                 uni_row=i
#                 # worksheet.merge_range(i, 0, i, 1, unidad["nombre_unidad"], bold_only)

#                 mapa_ventas_mensuales = self.ventas_mensual_por_departamento(data, id_unidad, cup=True)
#                 mapa_ventas_diaria = self.ventas_diarias_por_departamento(data, id_unidad, cup=True)
#                 mapa_ventas_anual = self.ventas_anual_por_departamento(data, id_unidad, cup=True)
#                 mapa_ventas_mensuales_ano_anterior = self.venta_ano_anterior_mensual_por_departamento(data, id_unidad, cup=True)
#                 mapa_ventas_anual_ano_anterior = self.venta_anual_anterior_anual_por_departamento(data, id_unidad, cup=True)

#                 mapa_presup_mesuales = self.presup_mensuales_por_departamento(data, id_unidad, cup=True)
#                 mapa_presup_diarios = self.presup_diarios_por_departamento(data, id_unidad, cup=True)
#                 mapa_presup_anual = self.presup_anuales_por_departamento(data, id_unidad, cup=True)

#                 i += 1
#                 c_d=0
#                 for id_departamento, departamentos in unidad["departamentos"].iteritems():
#                     if ((id_departamento in mapa_presup_anual) and (mapa_presup_anual[id_departamento]!=0)
#                     or (id_departamento in mapa_ventas_anual) and (mapa_ventas_anual[id_departamento]!=0)    
#                     or (id_departamento in mapa_presup_mesuales) and (mapa_presup_mesuales[id_departamento]!=0) 
#                     or (id_departamento in mapa_ventas_anual_ano_anterior) and (mapa_ventas_anual_ano_anterior[id_departamento]!=0)
#                     ):
#                         worksheet.merge_range(i, 0, i, 1, departamentos["nombre_departamento"])
#                 # Pintar ventas
#                         if id_departamento in mapa_ventas_mensuales:
#                             worksheet.write(i, 7, mapa_ventas_mensuales[id_departamento],dos_decimal)

#                         if id_departamento in mapa_ventas_diaria:
#                             worksheet.write(i, 3, mapa_ventas_diaria[id_departamento],dos_decimal)

#                         if id_departamento in mapa_ventas_anual:
#                             worksheet.write(i, 13, mapa_ventas_anual[id_departamento],dos_decimal)

#                         if id_departamento in mapa_ventas_mensuales_ano_anterior:
#                             worksheet.write(i, 5, mapa_ventas_mensuales_ano_anterior[id_departamento],dos_decimal)

#                         if id_departamento in mapa_ventas_anual_ano_anterior:
#                             worksheet.write(i, 11, mapa_ventas_anual_ano_anterior[id_departamento],dos_decimal)

#                         # Pintar presupuestos
#                         if id_departamento in mapa_presup_mesuales:
#                             worksheet.write(i, 6, mapa_presup_mesuales[id_departamento],dos_decimal)

#                         if id_departamento in mapa_presup_diarios:
#                             worksheet.write(i, 2, mapa_presup_diarios[id_departamento],dos_decimal)
#                         a=0
#                         b=0
#                         if id_departamento in mapa_presup_anual: a=mapa_presup_anual[id_departamento]
#                         if id_departamento in mapa_presup_mesuales: b= mapa_presup_mesuales[id_departamento] 
#                         worksheet.write(i, 12, a+b,dos_decimal)
#                         c_d += 1
#                         i += 1
#                 if c_d!=0:
#                     worksheet.merge_range(uni_row, 0, uni_row, 1, unidad["nombre_unidad"], bold_only)
#                     worksheet.merge_range(i, 0, i, 1, 'Total Unidad', bold_only)
#                     # departent_count = len(unidad["departamentos"])
#                     departent_count =c_d
#                     for current_range in range(2, 17):

#                         if current_range == 4 or current_range == 8 or current_range == 14:
#                             for porc_eq in range(i - departent_count, i+1):
#                                 before_col = current_range - 1
#                                 before_before_col = current_range - 2

#                                 before_col_char = str(unichr(97 + before_col)).upper() + str(porc_eq + 1)
#                                 before_before_col_char = str(unichr(97 + before_before_col)).upper() + str(porc_eq + 1)
#                                 if porc_eq==i:
#                                     worksheet.write_formula(porc_eq, current_range, 'IFERROR(%s*100/%s,0)' % (before_col_char, before_before_col_char),dos_decimal_bold)
#                                 else:
#                                     worksheet.write_formula(porc_eq, current_range, 'IFERROR(%s*100/%s,0)' % (before_col_char, before_before_col_char),dos_decimal)


#                             continue #calcular super promedio

#                         if current_range == 9 or current_range == 15:
#                             for porc_eq in range(i - departent_count, i+1):
#                                 before_col = current_range - 2
#                                 before_before_col = current_range - 3

#                                 before_col_char = str(unichr(97 + before_col)).upper() + str(porc_eq + 1)
#                                 before_before_col_char = str(unichr(97 + before_before_col)).upper() + str(porc_eq + 1)
#                                 if porc_eq==i:
#                                     worksheet.write_formula(porc_eq, current_range, '%s-%s' % (before_col_char, before_before_col_char),dos_decimal_bold)
#                                 else:
#                                     worksheet.write_formula(porc_eq, current_range, '%s-%s' % (before_col_char, before_before_col_char),dos_decimal)

#                             continue  # calcular diferencia/promedio

#                         if current_range == 10 or current_range == 16:
#                             for porc_eq in range(i - departent_count, i + 1):
#                                 before_col = current_range - 3
#                                 before_before_col = current_range - 5

#                                 before_col_char = str(unichr(97 + before_col)).upper() + str(porc_eq + 1)
#                                 before_before_col_char = str(unichr(97 + before_before_col)).upper() + str(porc_eq + 1)
#                                 if porc_eq==i:
#                                     worksheet.write_formula(porc_eq, current_range, '%s-%s' % (before_col_char, before_before_col_char),dos_decimal_bold)
#                                 else:
#                                     worksheet.write_formula(porc_eq, current_range, '%s-%s' % (before_col_char, before_before_col_char),dos_decimal)

#                             continue  # calcular diferencia/promedio

#                         col_char = str(unichr(97 + current_range)).upper()

#                         range_row_ini = col_char + str(i - departent_count + 1)
#                         range_row_end = col_char + str(i)
#                         if departent_count!=0:
#                             worksheet.write_formula(i, current_range, '=SUM(%s:%s)' % (range_row_ini, range_row_end),dos_decimal_bold)
#                         else:
#                             worksheet.write(i, current_range, 0, dos_decimal_bold)
#                     i += 1
#                     listaFilas.append(str(i))
#                     laCadena=laCadena+'%'+'s,'
#                 else:
#                     i=uni_row
#             #Pintar los totales de la División
#             worksheet.merge_range(i, 0, i, 1, 'Total División', dos_decimal_bold)
#             laCadena=laCadena[0:len(laCadena)-1]+')'
#             for current_range in range(2, 17):
#                 col_char = str(unichr(97 + current_range)).upper()
#                 listaCeldas=[]
#                 for j in range(len(listaFilas)):  
#                     listaCeldas.append(col_char+listaFilas[j])            
#                 tuplaCeldas=tuple(listaCeldas)
#                 if len(listaFilas)!=0:
#                     worksheet.write_formula(i, current_range, laCadena % tuplaCeldas, dos_decimal_bold)
#                 else:
#                     worksheet.write(i, current_range, 0, dos_decimal_bold)    
#             #Pintar los % en la fila del total de la División 
#             porc_eq=i
#             for current_range in (4,8,14):
#                 before_col = current_range - 1
#                 before_before_col = current_range - 2
#                 before_col_char = str(unichr(97 + before_col)).upper() + str(porc_eq+1)
#                 before_before_col_char = str(unichr(97 + before_before_col)).upper() + str(porc_eq+1)
#                 worksheet.write_formula(porc_eq, current_range, 'IFERROR(%s*100/%s,0)' % (before_col_char, before_before_col_char), dos_decimal_bold)
            
#             divisionsRowsList.append((i,division['nombre_division']))
        
#         #Pintar nueva hoja para resumen Empresa x Divisiones    
#         worksheet = workbook.add_worksheet('Resumen Empresa')

#         i = 4

#         worksheet.merge_range(0, 0, 0, 5, 'Palmares Sucursal Matanzas', bold_only)
#         worksheet.merge_range(1, 0, 1, 5, 'Cumplimiento de Plan Ingresos MN.', bold_only)
#         worksheet.write(1, 14, 'Fecha: %s' % data['current_date'].strftime("%d/%m/%Y"))
#         worksheet.write(2, 0, 'Resumen Empresa',bold_only)

#         # Tabla Diario
#         worksheet.merge_range(3, 2, 3, 4, 'Diario', format)
#         worksheet.merge_range(i, 0, i, 1, 'Divisiones', format)
#         worksheet.write(i, 2, 'Plan', format)
#         worksheet.write(i, 3, 'Año actual', format)
#         worksheet.write(i, 4, '%', format)

#         # Tabla Mensual
#         worksheet.merge_range(3, 5, 3, 10, 'Acumulado Mensual', format)
#         worksheet.write(i, 5, 'Año anterior', format)
#         worksheet.write(i, 6, 'Presup', format)
#         worksheet.write(i, 7, 'Año actual', format)
#         worksheet.write(i, 8, '%', format)
#         worksheet.write(i, 9, 'Dif/Pr', format)
#         worksheet.write(i, 10, 'Dif/AA', format)

#         # Tabla Anual
#         worksheet.merge_range(3, 11, 3, 16, 'Acumulado Anual', format)
#         worksheet.write(i, 11, 'Año Anterior', format)
#         worksheet.write(i, 12, 'Presup', format)
#         worksheet.write(i, 13, 'Año actual', format)
#         worksheet.write(i, 14, '%', format)
#         worksheet.write(i, 15, 'Dif/Pr', format)
#         worksheet.write(i, 16, 'Dif/AA', format)
# #Toma valores de las hojas de cada División        
#         j=5
#         for d in divisionsRowsList:
#             worksheet.merge_range(j, 0, j, 1, d[1], bold_only)
#             fila=str(d[0]+1)
#             for current_range in range(2,17):
#                 col_char = "'"+d[1]+"'!"+str(unichr(97 + current_range)).upper() + fila
#                 worksheet.write_formula(j, current_range, col_char, dos_decimal)    
#             j+=1            
# # Total Empresa
#         worksheet.merge_range(j, 0, j, 1, 'Total Empresa', bold_only)
#         for current_range in range(2,17):
#             col_char = str(unichr(97 + current_range)).upper()
#             range_row_ini = col_char + str(j - len(divisionsRowsList) + 1)
#             range_row_end = col_char + str(j)
#             worksheet.write_formula(j, current_range, '=SUM(%s:%s)' % (range_row_ini, range_row_end),dos_decimal_bold)
# # Calcula % totales
#         porc_eq=j
#         for current_range in (4,8,14):
#             before_col = current_range - 1
#             before_before_col = current_range - 2
#             before_col_char = str(unichr(97 + before_col)).upper() + str(porc_eq+1)
#             before_before_col_char = str(unichr(97 + before_before_col)).upper() + str(porc_eq+1)
#             worksheet.write_formula(porc_eq, current_range, 'IFERROR(%s*100/%s,0)' % (before_col_char, before_before_col_char),dos_decimal_bold)

#         return "Cumplimiento Plan Ingresos en Moneda Nacional (%s)" % data['current_date'].strftime("%d-%m-%Y")


#     def ventas_mensual_por_departamento(self, data, id_unidad, cup=False):
#         ventas_mensual_query = """SELECT SUM(ventas_ventas.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_ventas
#                         INNER JOIN hr_department v ON ventas_ventas.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE fecha::date <= '%s'::date AND extract(year from '%s'::date) = extract(year from fecha) AND extract(month from '%s'::date) = extract(month from fecha)  AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('vnacional' if cup else 'vdivisa',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(ventas_mensual_query)
#         mapa_ventas_mensuales = {}
#         for ventas in self.env.cr.dictfetchall():
#             mapa_ventas_mensuales[ventas["id_departamento"]] = ventas["nacional"]
#         return mapa_ventas_mensuales

#     def ventas_anual_por_departamento(self, data, id_unidad, cup=False):
#         ventas_year_query = """SELECT SUM(ventas_ventas.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_ventas
#                         INNER JOIN hr_department v ON ventas_ventas.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE fecha::date <= '%s'::date AND extract(year from '%s'::date) = extract(year from fecha) AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('vnacional' if cup else 'vdivisa',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(ventas_year_query)
#         mapa_ventas_year = {}
#         for ventas in self.env.cr.dictfetchall():
#             mapa_ventas_year[ventas["id_departamento"]] = ventas["nacional"]
#         return mapa_ventas_year

#     def ventas_diarias_por_departamento(self, data, id_unidad, cup=False):
#         ventas_dia_query = """SELECT SUM(ventas_ventas.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_ventas
#                         INNER JOIN hr_department v ON ventas_ventas.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE fecha::date = '%s'::date AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('vnacional' if cup else 'vdivisa',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(ventas_dia_query)
#         mapa_ventas_mensuales = {}
#         for ventas in self.env.cr.dictfetchall():
#             mapa_ventas_mensuales[ventas["id_departamento"]] = ventas["nacional"]
#         return mapa_ventas_mensuales

#     def presup_mensuales_por_departamento(self, data, id_unidad, cup=False):
#         presup_mes_query = """SELECT MAX(ventas_presupuesto.%s * extract(day from '%s'::date))  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_presupuesto
#                         INNER JOIN hr_department v ON ventas_presupuesto.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE extract(year from '%s'::date) = extract(year from fecha) AND extract(month from '%s'::date) = extract(month from fecha)  AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('"pnacionalDiario"' if cup else '"pdivisaDiario"',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(presup_mes_query)
#         mapa_presup_mensuales = {}
#         for presup in self.env.cr.dictfetchall():
#             mapa_presup_mensuales[presup["id_departamento"]] = presup["nacional"]
#         return mapa_presup_mensuales

#     def presup_diarios_por_departamento(self, data, id_unidad, cup=False):
#         presup_dia_query = """SELECT MAX(ventas_presupuesto.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_presupuesto
#                         INNER JOIN hr_department v ON ventas_presupuesto.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE extract(month from '%s'::date) = extract(month from fecha)
#                         AND extract(year from '%s'::date) = extract(year from fecha) AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('"pnacionalDiario"' if cup else '"pdivisaDiario"',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(presup_dia_query)
#         mapa_presup_dia = {}
#         for presup in self.env.cr.dictfetchall():
#             mapa_presup_dia[presup["id_departamento"]] = presup["nacional"]
#         return mapa_presup_dia

#     def presup_anuales_por_departamento(self, data, id_unidad, cup=False):
#         presup_anual_query = """SELECT SUM(ventas_presupuesto.%s)  AS nacional,
#                                                    v.id as id_departamento
#                            FROM ventas_presupuesto
#                            INNER JOIN hr_department v ON ventas_presupuesto.departamento_id = v.id
#                            INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                            INNER JOIN ventas_division vd ON u.division_id = vd.id
#                            WHERE extract(month from '%s'::date) > extract(month from fecha) AND extract(year from '%s'::date) = extract(year from fecha) AND u.id = %s
#                            GROUP BY v.id
#                                 """ % ('"pnacional"' if cup else '"pdivisa"',
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        data['current_date'].strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))
#         self.env.cr.execute(presup_anual_query)
#         mapa_presup_anual = {}
#         for presup in self.env.cr.dictfetchall():
#             mapa_presup_anual[presup["id_departamento"]] = presup["nacional"]
#         return mapa_presup_anual

# # Ventas año anterior

#     def venta_ano_anterior_mensual_por_departamento(self, data, id_unidad, cup=False):
#         previous_year = data['current_date'] - relativedelta.relativedelta(years=1)

#         venta_ano_anterior_mensual_query = """SELECT SUM(ventas_ventas.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_ventas
#                         INNER JOIN hr_department v ON ventas_ventas.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE fecha::date <= '%s'::date AND extract(year from '%s'::date) = extract(year from fecha) AND extract(month from '%s'::date) = extract(month from fecha)  AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('vnacional' if cup else 'vdivisa',
#                                        previous_year.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        previous_year.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        previous_year.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad)) 

#         self.env.cr.execute(venta_ano_anterior_mensual_query)
#         mapa_venta_ano_anterior_mes = {}
#         for ventas in self.env.cr.dictfetchall():
#             mapa_venta_ano_anterior_mes[ventas["id_departamento"]] = ventas["nacional"]
#         return mapa_venta_ano_anterior_mes

#     def venta_anual_anterior_anual_por_departamento(self, data, id_unidad, cup=False):
#         previous_year = data['current_date'] - relativedelta.relativedelta(years=1)

#         ventas_year_anterior_query = """SELECT SUM(ventas_ventas.%s)  AS nacional,
#                                                 v.id as id_departamento
#                         FROM ventas_ventas
#                         INNER JOIN hr_department v ON ventas_ventas.departamento_id = v.id
#                         INNER JOIN ventas_unidad u ON v.unidad_id = u.id
#                         INNER JOIN ventas_division vd ON u.division_id = vd.id
#                         WHERE fecha::date <= '%s'::date AND extract(year from '%s'::date) = extract(year from fecha) AND u.id = %s
#                         GROUP BY v.id
#                                 """ % ('vnacional' if cup else 'vdivisa',
#                                        previous_year.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        previous_year.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                                        str(id_unidad))



#         self.env.cr.execute(ventas_year_anterior_query)
#         mapa_ventas_year_anterior = {}
#         for ventas in self.env.cr.dictfetchall():
#             mapa_ventas_year_anterior[ventas["id_departamento"]] = ventas["nacional"]
#         return mapa_ventas_year_anterior


CertReport('report.cert_xlsx',
            'hr.certificado.comercial', store=True)