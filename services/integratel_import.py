"""Formato Ticket ID de Integratel; conserva claves y gestión manual existente."""
import json
from db import db
from models import AppConfig

HEADERS = [
    'SLA Status', 'Ticket ID', 'Ticket Status', 'Business Status', 'SLA Target Time',
    'Process Display Name', 'Process Type', 'Current Phase', 'Ticket Created By',
    'Current Handler', 'Created At', 'Closure Time', 'Updated At', 'OLA Status',
    'OLA Target Time', 'Parent Process Display Name', 'Escalate or not', 'Exempt or not',
    'Escalation Level', 'Project', 'Module', 'Process Name', 'Title', 'Project Name',
]
ALIASES = {'Ticket ID': 'Número de WO', 'Ticket Status': 'Estado de la tarea (WO State)',
           'Created At': 'Fecha de creación (WO Creation date)'}


def prepare(df, manual_columns):
    """Detecta el formato nuevo sin aplicar cambios a archivos de otros módulos."""
    if 'Ticket ID' not in df.columns:
        return df, False
    if 'Número de WO' in df.columns:
        for ticket, wo in zip(df['Ticket ID'].fillna(''), df['Número de WO'].fillna('')):
            if str(wo).strip() and str(ticket).strip() != str(wo).strip():
                raise ValueError('Ticket ID y Número de WO no coinciden. No se importó el archivo.')
    keys = df['Ticket ID'].fillna('').astype(str).str.strip()
    if keys.eq('').any():
        raise ValueError('El archivo contiene Ticket ID vacíos. No se importó el archivo.')
    if keys.duplicated().any():
        raise ValueError('El archivo contiene Ticket ID duplicados. No se importó el archivo.')
    missing = [name for name in HEADERS if name not in df.columns]
    if missing:
        raise ValueError('El exportable de Integratel está incompleto. Faltan columnas: ' + ', '.join(missing))
    df = df.copy()
    df['Ticket ID'] = keys
    # El exportable es fuente de columnas importadas, nunca de gestión manual.
    protected = {name.casefold() for name in manual_columns}
    df = df[[name for name in df.columns if name.casefold() not in protected or name == 'Ticket ID']]
    return df, True


def compatible_row(data):
    data = dict(data)
    for source, legacy in ALIASES.items():
        if source in data:
            data[legacy] = data[source]
    return data


def configure(pid, columns, manual_columns):
    """Reemplaza solo las columnas importadas, manteniendo el layout manual."""
    def save(key, value):
        row = AppConfig.query.filter_by(proyecto_id=pid, clave=key).first()
        if row:
            row.valor = value
        else:
            db.session.add(AppConfig(proyecto_id=pid, clave=key, valor=value))
    manual = set(manual_columns)
    schema = [name for name in columns if name not in manual and name not in ALIASES.values()]
    save('app_schema', json.dumps(schema, ensure_ascii=False))
    save('primary_key', 'Ticket ID')
    layout_row = AppConfig.query.filter_by(proyecto_id=pid, clave='column_layout').first()
    layout = json.loads(layout_row.valor or '[]') if layout_row else []
    # Guarda atributos de ancho, visibilidad y orden relativo de cada manual.
    retained = [item for item in layout if item.get('field') in manual or item.get('field') in
                ('GESTOR', 'EDITADO POR', 'FECHA CAMBIO ESTADO', 'Tipo WO', 'CODIGO INTERNO')]
    known_manual = {item['field'] for item in retained}
    retained += [{'field': name, 'visible': True} for name in manual_columns if name not in known_manual]
    visible = [{'field': '_key', 'visible': True}]
    visible += [{'field': name, 'visible': True} for name in schema if name != 'Ticket ID']
    # _key ya representa Ticket ID; no duplicar la columna del identificador.
    visible += [{'field': 'Ticket ID', 'visible': False}]
    save('column_layout', json.dumps(visible + retained, ensure_ascii=False))
