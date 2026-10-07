"""motor de curvas de crecimiento
uso tablas abiertas: oms (lms por dia)
e intergrowth postnatal pretermino (valores por sd)
para prematuros uso intergrowth hasta 64 semanas postmenstruales"""

import csv
import math
import os

# carpeta con las tablas de referencia que baje de internet
_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'referencias')

# aca guardo las tablas ya leidas para no leer el disco en cada calculo
_cache = {}


def _lee_oms():
    # el csv trae secciones: semanas 0-13, meses 1-24 y meses 2-5 años
    # columnas por indicador y sexo: l, m, s 
    # devuelvo {medida: {sexo: [(edad_dias, l, m, s)]}} edad en dias
    cols = {
        'lhfa': (2, 5), 'wfa': (8, 11), 'bfa': (14, 17), 'hcfa': (20, 23),
    }
    res = {m: {'m': [], 'f': []} for m in cols}
    with open(os.path.join(_DIR, 'who2006.csv'), encoding='utf-8-sig') as f:
        filas = list(csv.reader(f))
    for fl in filas[4:]:
        if len(fl) < 26:
            continue
        try:
            wm = float(fl[0])
            anios = float(fl[1])
        except (ValueError, IndexError):
            continue
        # las primeras filas son semanas, despues meses sueltos
        if anios < 0.15 and wm <= 13:
            dias = wm * 7.0
        else:
            dias = anios * 365.25
        for med, (c0, c1) in cols.items():
            try:
                lm, mm, sm = float(fl[c0]), float(fl[c0 + 1]), float(fl[c0 + 2])
                lf, mf, sf = float(fl[c1]), float(fl[c1 + 1]), float(fl[c1 + 2])
            except (ValueError, IndexError):
                continue
            res[med]['m'].append((dias, lm, mm, sm))
            res[med]['f'].append((dias, lf, mf, sf))
    for med in res:
        for s in res[med]:
            res[med][s].sort()
    return res


def _lee_ig():
    # archivos con columnas: semana sd3neg sd2neg sd1neg sd0 sd1 sd2 sd3
    # peso en kg, talla y pc en cm, semanas 27 a 64
    res = {}
    for med, base in (('wfa', 'weight'), ('lfa', 'len'), ('hcfa', 'hc')):
        res[med] = {}
        for sexo, suf in (('m', 'male'), ('f', 'female')):
            serie = []
            with open(os.path.join(
                    _DIR, f'ig_png_{base}_{suf}_z.csv'), encoding='utf-8-sig') as f:
                for fl in csv.reader(f, delimiter=' '):
                    fl = [c for c in fl if c != '']
                    if len(fl) < 8:
                        continue
                    try:
                        serie.append((float(fl[0]), [float(x) for x in fl[1:8]]))
                    except ValueError:
                        continue
            serie.sort()
            res[med][sexo] = serie
    return res


def _tablas():
    # cargo una sola vez y reutilizo
    global _cache
    if not _cache:
        _cache = {'oms': _lee_oms(), 'ig': _lee_ig()}
    return _cache


def _interpola_vector(serie, x):
    # para las series de intergrowth donde cada fila es (semana, [7 valores])
    # devuelvo los 7 valores interpolados a la semana x
    if x <= serie[0][0]:
        return serie[0][1]
    if x >= serie[-1][0]:
        return serie[-1][1]
    for (xa, va), (xb, vb) in zip(serie, serie[1:]):
        if xa <= x <= xb:
            t = (x - xa) / (xb - xa) if xb != xa else 0
            return [a + (b - a) * t for a, b in zip(va, vb)]
    return serie[-1][1]


def _interpola(puntos, x, idx=None):
    # interpolo lineal entre los dos puntos que encierran a x
    # puntos es lista de tuplas ordenadas, comparo por [0]
    if x <= puntos[0][0]:
        return puntos[0] if idx is None else puntos[0][idx]
    if x >= puntos[-1][0]:
        return puntos[-1] if idx is None else puntos[-1][idx]
    for a, b in zip(puntos, puntos[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0
            if idx is None:
                return tuple(av + (bv - av) * t for av, bv in zip(a, b))
            return a[idx] + (b[idx] - a[idx]) * t
    return puntos[-1] if idx is None else puntos[-1][idx]


def z_lms(valor, l, m, s):
    # formula clasica de cole, si l es 0 uso logaritmo
    if valor <= 0 or m <= 0 or s <= 0:
        return None
    if abs(l) < 1e-9:
        return math.log(valor / m) / s
    return ((valor / m) ** l - 1) / (l * s)


def valor_lms(z, l, m, s):
    # inversa: que valor corresponde a ese z
    if m <= 0 or s <= 0:
        return None
    if abs(l) < 1e-9:
        return m * math.exp(s * z)
    base = 1 + l * s * z
    if base <= 0:
        return None
    return m * base ** (1 / l)


# mapa de medida del sistema a indicador de cada estandar
_MEDIDAS = {
    'peso': ('wfa', 'wfa'),
    'talla': ('lhfa', 'lfa'),
    'pc': ('hcfa', 'hcfa'),
}


def es_pretermino(eg_semanas):
    return (eg_semanas or 0) < 37


def z_score(sexo, medida, edad_dias=None, pma_semanas=None,
            valor=None, eg_semanas=40):
    # devuelvo el z de una medicion o None si no se puede
    # sexo m/f, medida peso/talla/pc, valor en g o cm segun medida
    # para prematuros con pma hasta 64 semanas uso intergrowth
    # si no uso oms con edad en dias desde el nacimiento
    if not valor or valor <= 0:
        return None
    if sexo not in ('m', 'f') or medida not in _MEDIDAS:
        return None
    ind_oms, ind_ig = _MEDIDAS[medida]
    tab = _tablas()
    # rama de prematuros con intergrowth
    if es_pretermino(eg_semanas) and pma_semanas is not None and pma_semanas <= 64:
        serie = tab['ig'][ind_ig][sexo]
        if not serie or pma_semanas < serie[0][0]:
            return None
        vals = _interpola_vector(serie, pma_semanas)
        # la tabla de peso viene en kg, yo trabajo en gramos
        v = valor / 1000.0 if medida == 'peso' else valor
        # busco entre que lineas de sd cae e interpolo el z
        grilla = [-3, -2, -1, 0, 1, 2, 3]
        if v <= vals[0]:
            return -3.0
        if v >= vals[-1]:
            return 3.0
        for i in range(6):
            if vals[i] <= v <= vals[i + 1]:
                t = (v - vals[i]) / (vals[i + 1] - vals[i]) if vals[i + 1] != vals[i] else 0
                return round(grilla[i] + t, 2)
        return None
    if edad_dias is None:
        return None
    # rama de termino (o prematuro mayor) con oms
    serie = tab['oms'][ind_oms][sexo]
    if not serie:
        return None
    _, l, m, s = _interpola(serie, edad_dias)
    v = valor / 1000.0 if medida == 'peso' else valor
    z = z_lms(v, l, m, s)
    return round(z, 2) if z is not None else None


def curva(sexo, medida, pretermino=True, zs=(-1.88, -0.67, 0, 0.67, 1.88)):
    """devuelvo las lineas de referencia p3/p25/p50/p75/p97
    como lista de {x, valores} donde x es semana pma o dia de vida"""
    if sexo not in ('m', 'f') or medida not in _MEDIDAS:
        return []
    ind_oms, ind_ig = _MEDIDAS[medida]
    tab = _tablas()
    lineas = []
    if pretermino:
        serie = tab['ig'][ind_ig][sexo]
        if not serie:
            return []
        for z in zs:
            pts = []
            for sem, vals in serie:
                grilla = [-3, -2, -1, 0, 1, 2, 3]
                if z <= -3:
                    v = vals[0]
                elif z >= 3:
                    v = vals[-1]
                else:
                    v = None
                    for i in range(6):
                        if grilla[i] <= z <= grilla[i + 1]:
                            t = z - grilla[i]
                            v = vals[i] + (vals[i + 1] - vals[i]) * t
                            break
                if medida == 'peso':
                    v = v * 1000.0
                pts.append([round(sem, 2), round(v, 1)])
            lineas.append({'z': z, 'puntos': pts})
    else:
        serie = tab['oms'][ind_oms][sexo]
        if not serie:
            return []
        for z in zs:
            pts = []
            for dias, l, m, s in serie:
                v = valor_lms(z, l, m, s)
                if v is None:
                    continue
                if medida == 'peso':
                    v = v * 1000.0
                pts.append([round(dias, 1), round(v, 1)])
            lineas.append({'z': z, 'puntos': pts})
    return lineas
