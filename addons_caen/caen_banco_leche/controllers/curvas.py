"""datos para las curvas de crecimiento, punto 5
junto mediciones del bebe con las lineas de referencia
prematuros: intergrowth por semanas postmenstruales
termino: oms por dias de vida"""

from odoo import http
from odoo.http import request

from ..models import curvas


class CurvasController(http.Controller):
    # pagina de datos en json para el grafico
    # la llama el componente owl de curvas con el id del paciente
    @http.route('/caen/curvas/<int:patient_id>', type='jsonrpc', auth='user')
    def datos(self, patient_id):
        bebe = request.env['caen.paciente'].browse(patient_id)
        if not bebe.exists():
            return {'error': 'paciente inexistente'}
        sexo = bebe.sexo or 'm'
        eg = (bebe.gestational_age_weeks or 0) + (bebe.gestational_age_days or 0) / 7.0
        prematuro = curvas.es_pretermino(bebe.gestational_age_weeks or 40)
        # junto todas las mediciones: nacimiento mas evolucion diaria
        puntos = {'peso': [], 'talla': [], 'pc': []}
        if bebe.birth_date:
            base = bebe.birth_date
            if bebe.birth_weight_g:
                puntos['peso'].append(self._punto(base, base, eg, bebe.birth_weight_g))
            if bebe.birth_height_cm:
                puntos['talla'].append(self._punto(base, base, eg, bebe.birth_height_cm))
            if bebe.head_circumference_cm:
                puntos['pc'].append(self._punto(base, base, eg, bebe.head_circumference_cm))
        evos = request.env['caen.evolucion_diaria'].search(
            [('patient_id', '=', bebe.id)], order='record_date')
        for ev in evos:
            if not ev.record_date or not bebe.birth_date:
                continue
            if ev.weight_g:
                puntos['peso'].append(self._punto(bebe.birth_date, ev.record_date, eg, ev.weight_g))
            if ev.height_cm:
                puntos['talla'].append(self._punto(bebe.birth_date, ev.record_date, eg, ev.height_cm))
            if ev.head_circumference_cm:
                puntos['pc'].append(self._punto(bebe.birth_date, ev.record_date, eg, ev.head_circumference_cm))
        # calculo el z de cada punto con el estandar que corresponde
        for med in puntos:
            for p in puntos[med]:
                p['z'] = curvas.z_score(sexo, med, edad_dias=p['dias'],
                                        pma_semanas=p['pma'], valor=p['valor'],
                                        eg_semanas=eg)
        # etiquetas de percentiles para el grafico
        nombres = {-1.88: 'P3', -0.67: 'P25', 0: 'P50', 0.67: 'P75', 1.88: 'P97'}
        refs = {}
        for med in ('peso', 'talla', 'pc'):
            refs[med] = [{'nombre': nombres[l['z']], 'puntos': l['puntos']}
                         for l in curvas.curva(sexo, med, pretermino=prematuro)]
        return {
            'paciente': bebe.name,
            'sexo': sexo,
            'prematuro': prematuro,
            'eje': 'semanas postmenstruales' if prematuro else 'dias de vida',
            'puntos': puntos,
            'refs': refs,
        }

    def _punto(self, nacimiento, fecha, eg, valor):
        # dias de vida y semanas postmenstruales del dia de la medicion
        dias = (fecha - nacimiento).days
        return {'dias': dias, 'pma': round(eg + dias / 7.0, 2),
                'x': round(eg + dias / 7.0, 2), 'valor': valor, 'fecha': str(fecha)}
