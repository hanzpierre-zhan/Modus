import io
import json
import pandas as pd
from db import db
from models import AppConfig, Proyecto, NucleusData
from services.integratel_import import HEADERS


def setup_project(app, client, name='FLM - INTEGRATEL'):
    with app.app_context():
        pid = Proyecto.query.filter_by(nombre=name).one().id
        manual = [{'nombre': 'GESTION_PRUEBA', 'tipo': 'texto', 'opciones': []}]
        for key, value in [('manual_columns', json.dumps(manual)), ('primary_key', 'Número de WO'),
                           ('app_schema', json.dumps(['Número de WO', 'Columna antigua'])),
                           ('column_layout', json.dumps([{'field': 'GESTION_PRUEBA', 'visible': False, 'width': 180}]))]:
            row = AppConfig.query.filter_by(proyecto_id=pid, clave=key).first()
            if row: row.valor = value
            else: db.session.add(AppConfig(proyecto_id=pid, clave=key, valor=value))
        NucleusData.query.filter_by(proyecto_id=pid).delete()
        db.session.add(NucleusData(proyecto_id=pid, key_value='CM-1', data_json=json.dumps(
            {'Número de WO': 'CM-1', 'GESTION_PRUEBA': 'conservar', 'Estado de la tarea (WO State)': 'Running'})))
        db.session.commit()
    with client.session_transaction() as session:
        session['current_proyecto_id'] = pid
        session['current_proyecto_nombre'] = name
    return pid


def upload(client, rows):
    data = pd.DataFrame(rows).to_csv(index=False).encode('utf-8')
    return client.post('/api/import/process', data={'file': (io.BytesIO(data), 'export.csv'), 'type': 'base'})


def test_new_format_updates_key_preserves_manuals_and_replaces_schema(app, auth_client):
    pid = setup_project(app, auth_client)
    row = dict.fromkeys(HEADERS, '')
    row.update({'Ticket ID': 'CM-1', 'Ticket Status': 'Completed', 'Created At': '2026-10-01', 'GESTION_PRUEBA': 'no pisar'})
    response = upload(auth_client, [row])
    assert response.status_code == 200, response.json
    assert response.json['updated'] == 1
    assert response.json['added'] == 0
    assert response.json['pk'] == 'Ticket ID'
    with app.app_context():
        data = json.loads(NucleusData.query.filter_by(proyecto_id=pid, key_value='CM-1').one().data_json)
        assert data['GESTION_PRUEBA'] == 'conservar'
        assert data['Número de WO'] == data['Ticket ID'] == 'CM-1'
        assert data['Estado de la tarea (WO State)'] == 'Completed'
        assert json.loads(AppConfig.query.filter_by(proyecto_id=pid, clave='app_schema').one().valor) == HEADERS
        assert json.loads(AppConfig.query.filter_by(proyecto_id=pid, clave='manual_columns').one().valor)[0]['nombre'] == 'GESTION_PRUEBA'
        layout = json.loads(AppConfig.query.filter_by(proyecto_id=pid, clave='column_layout').one().valor)
        assert {'field': 'GESTION_PRUEBA', 'visible': False, 'width': 180} in layout
    repeat = upload(auth_client, [row])
    assert repeat.json['added'] == 0
    old = upload(auth_client, [{'Número de WO': 'CM-1', 'Estado de la tarea (WO State)': 'Running'}])
    assert old.status_code == 200, old.json
    with app.app_context():
        assert json.loads(AppConfig.query.filter_by(proyecto_id=pid, clave='app_schema').one().valor) == HEADERS
        assert NucleusData.query.filter_by(proyecto_id=pid).count() == 1


def test_invalid_ticket_identifiers_do_not_write(app, auth_client):
    pid = setup_project(app, auth_client)
    for rows in [[{'Ticket ID': ''}], [{'Ticket ID': 'same'}, {'Ticket ID': 'same'}],
                 [{'Ticket ID': 'CM-1', 'Número de WO': 'different'}], [{'Ticket ID': 'CM-1'}]]:
        response = upload(auth_client, rows)
        assert response.status_code == 400, response.json
    with app.app_context():
        assert NucleusData.query.filter_by(proyecto_id=pid).count() == 1
        assert AppConfig.query.filter_by(proyecto_id=pid, clave='primary_key').one().valor == 'Número de WO'


def test_other_module_does_not_switch_to_ticket_schema(app, auth_client):
    pid = setup_project(app, auth_client, 'Cotizaciones')
    response = upload(auth_client, [{'Número de WO': 'CM-1', 'Ticket ID': 'external'}])
    assert response.status_code == 200, response.json
    with app.app_context():
        assert AppConfig.query.filter_by(proyecto_id=pid, clave='primary_key').one().valor == 'Número de WO'
