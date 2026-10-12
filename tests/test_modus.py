import json
import pytest
from db import db
from models import Proyecto,NucleusData

@pytest.fixture
def modus(app):
    app.config['MODUS_SCOPE']=True
    yield app
    app.config['MODUS_SCOPE']=False

def test_solo_integratel_en_menu_y_destinos(modus,auth_client):
    from services.utilidades import get_menu_proyectos
    from services.operador import MODULOS
    with modus.test_request_context():
        assert all(p.nombre in MODULOS for p in get_menu_proyectos(1,'zeno'))
    with modus.app_context():
        entel=Proyecto.query.filter_by(nombre='FLM - ENTEL').one().id
        integratel=Proyecto.query.filter_by(nombre='FLM - INTEGRATEL').one().id
    assert auth_client.get('/switch_project/%s'%entel).status_code==403
    assert auth_client.get('/switch_project/%s'%integratel).status_code==302
    assert auth_client.get('/api/wo/meta',headers={'X-Nucleus-Project':str(entel)}).status_code==403

def test_rechaza_otro_cliente_y_crea_cotizacion_integratel(modus,auth_client):
    with modus.app_context():pid=Proyecto.query.filter_by(nombre='Cotizaciones').one().id
    auth_client.get('/switch_project/%s'%pid)
    r=auth_client.post('/api/rows/add',json={'key':'MODUS-COT-1','data':{'CLIENTE':'CLARO'}})
    assert r.status_code==400,r.json
    r=auth_client.post('/api/rows/add',json={'key':'MODUS-COT-1','data':{'CLIENTE':'INTEGRATEL'}})
    assert r.status_code==200,r.json
    key=r.json['key']
    r=auth_client.post('/api/rows/bulk_update',json={'key':key,'data':{'CLIENTE':'ENTEL'}})
    assert r.status_code==400
    with modus.app_context():
        f=NucleusData.query.filter_by(proyecto_id=pid,key_value=key).one()
        assert json.loads(f.data_json)['CLIENTE']=='INTEGRATEL'
        db.session.delete(f);db.session.commit()

def test_recursos_integratel_crean_asignacion_por_defecto(modus,auth_client):
    with modus.app_context():
        flm=Proyecto.query.filter_by(nombre='FLM - INTEGRATEL').one().id
        personal=Proyecto.query.filter_by(nombre='Dataper').one().id
    r=auth_client.get('/flm/%s/recursos/personal'%flm)
    assert r.status_code==302
    r=auth_client.post('/api/rows/add',json={'key':'MODUS-PER-1','data':{'NOMBRE':'Persona de prueba'}})
    assert r.status_code==200,r.json
    with modus.app_context():
        f=NucleusData.query.filter_by(proyecto_id=personal,key_value='MODUS-PER-1').one()
        assert json.loads(f.data_json)['PROYECTO']=='FLM - INTEGRATEL'
        db.session.delete(f);db.session.commit()
