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
TASK_HEADERS = ['Task Id', 'Createtime', 'Dispatch Time', 'Accept Time', 'Depart Time', 'Arrive Time', 'Complete Time', 'Require Finish Time', 'First Complete Time', 'Cancel Time', 'Cancel Operator', 'Cancel Reason', 'Task Status', 'Com Fault Speciality', 'Com Fault Sub Speciality', 'Com Fault Cause', 'Leave Observations', 'Site Id', 'Site Priority', 'Title', 'Description', 'Nro TOA', 'Company Supply', 'ZONA', 'DEPARTAMENTO', 'TORRERO', 'Task Type', 'Fm Office', 'Region', 'Site Id Name', 'Site location type', 'Sla', 'Sla Status', 'Suspend State', 'Create Operator', 'Fault First Occur Time', 'Schedule Operator', 'Schedule Time', 'Assign To Fme', 'Assign To Fme Full Name', 'Dispatch Operator', 'Depart Operator', 'Arrive Operator', 'Complete Operator', 'Reject Time', 'Reject Operator', 'Reject Des', 'Com Level 1 Aff Equip', 'Com Level 2 Aff Equip', 'Com Level 3 Aff Equip', 'Fault Type', 'Task Category', 'Task Subcategory', 'FME contrator', 'Contratista Sitio', 'Complete Operator Name', 'Reject Operator Name', 'Arrive Operator Name', 'Depart Operator Name', 'Dispatch Operator Name', 'Cancel Operator Name', 'Schedule Operator Name', 'Create Operator Name', 'Situación encontrada', 'Detalle de actuación realizada', 'Atención Incidencias', 'Remedy ID', 'First Pause Time', 'First Pause Operator', 'First Pause Reason', 'First Resume Operator', 'First Resume Time', 'Second Pause Time', 'Second Pause Reason', 'Second Pause Operator', 'Second Resume Time', 'Second Resume Operator', 'Third Pause Time', 'Third Pause Reason', 'Third Pause Operator', 'Third Resume Time', 'Third Resume Operator', 'Fourth Pause Time', 'Fourth Pause Reason', 'Fourth Pause Operator', 'Fourth Resume Time', 'Fourth Resume Operator', 'Fifth Pause Time', 'Fifth Pause Reason', 'Fifth Pause Operator', 'Fifth Resume Time', 'Fifth Resume Operator', 'Reject Flag', 'Reject Counter', 'Fuel Type']
TASK_ALIASES = {'Task Id': 'Número de WO', 'Task Status': 'Estado de la tarea (WO State)', 'Createtime': 'Fecha de creación (WO Creation date)', 'Site Id': 'Código Site', 'Site Id Name': 'Nombre de Site', 'Site Priority': 'Prioridad del Site'}
ALIASES = {'Ticket ID': 'Número de WO', 'Ticket Status': 'Estado de la tarea (WO State)',
           'Created At': 'Fecha de creación (WO Creation date)'}


def prepare(df, manual_columns):
    """Detecta el formato nuevo sin aplicar cambios a archivos de otros módulos."""
    key = 'Task Id' if 'Task Id' in df.columns else 'Ticket ID'
    headers = TASK_HEADERS if key == 'Task Id' else HEADERS
    if key not in df.columns:
        return df, False
    if 'Número de WO' in df.columns:
        for ticket, wo in zip(df[key].fillna(''), df['Número de WO'].fillna('')):
            if str(wo).strip() and str(ticket).strip() != str(wo).strip():
                raise ValueError(key + ' y Número de WO no coinciden. No se importó el archivo.')
    keys = df[key].fillna('').astype(str).str.strip()
    if keys.eq('').any():
        raise ValueError('El archivo contiene ' + key + ' vacíos. No se importó el archivo.')
    if keys.duplicated().any():
        raise ValueError('El archivo contiene ' + key + ' duplicados. No se importó el archivo.')
    missing = [name for name in headers if name not in df.columns]
    if missing:
        raise ValueError('El exportable de Integratel está incompleto. Faltan columnas: ' + ', '.join(missing))
    df = df.copy()
    df[key] = keys
    # El exportable es fuente de columnas importadas, nunca de gestión manual.
    protected = {name.casefold() for name in manual_columns}
    df = df[[name for name in df.columns if name.casefold() not in protected or name == key]]
    return df, True


def compatible_row(data):
    data = dict(data)
    for source, legacy in (TASK_ALIASES if 'Task Id' in data else ALIASES).items():
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
    key = 'Task Id' if 'Task Id' in columns else 'Ticket ID'
    aliases = TASK_ALIASES if key == 'Task Id' else ALIASES
    manual = set(manual_columns)
    schema = [name for name in columns if name not in manual and name not in aliases.values()]
    save('app_schema', json.dumps(schema, ensure_ascii=False))
    save('primary_key', key)
    layout_row = AppConfig.query.filter_by(proyecto_id=pid, clave='column_layout').first()
    layout = json.loads(layout_row.valor or '[]') if layout_row else []
    # Guarda atributos de ancho, visibilidad y orden relativo de cada manual.
    retained = [item for item in layout if item.get('field') in manual or (key != 'Task Id' and item.get('field') in
                ('GESTOR', 'EDITADO POR', 'FECHA CAMBIO ESTADO', 'Tipo WO', 'CODIGO INTERNO'))]
    known_manual = {item['field'] for item in retained}
    retained += [{'field': name, 'visible': True} for name in manual_columns if name not in known_manual]
    visible = [{'field': '_key', 'visible': True}]
    visible += [{'field': name, 'visible': True} for name in schema if name != key]
    # _key ya representa Ticket ID; no duplicar la columna del identificador.
    visible += [{'field': key, 'visible': False}]
    save('column_layout', json.dumps(visible + retained, ensure_ascii=False))
