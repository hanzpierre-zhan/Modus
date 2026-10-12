"""Límite de Integratel aplicado en lectura, navegación y escritura."""
import json
from flask import current_app,request,session,jsonify
from sqlalchemy import event
from werkzeug.exceptions import BadRequest
from db import db
from models import Proyecto,NucleusData,AppConfig
from services.recursos_flm import familia,normalizar

MODULOS=frozenset({'FLM - INTEGRATEL','Dataper','Material','Site Name','Generadores','Combustible','Cotizaciones','SITE','Rendicion','Liquidaciones'})
ETIQUETAS={'proyecto','cliente','nombredelproyecto','nombreproyecto','operador'}

def adaptar_datos(nombre,datos):
    out=dict(datos)
    for campo,valor in out.items():
        if normalizar(campo) in ETIQUETAS and str(valor or '').strip() and familia(valor)!='INTEGRATEL':
            raise BadRequest('Modus solo admite registros de Integratel.')
    campo={'Cotizaciones':'CLIENTE','Rendicion':'Nombre del proyecto','Dataper':'PROYECTO','Material':'PROYECTO'}.get(nombre)
    if campo and not any(normalizar(k)==normalizar(campo) and str(v or '').strip() for k,v in out.items()):
        out[campo]='FLM - INTEGRATEL' if nombre in ('Dataper','Material') else 'INTEGRATEL'
    return out

def preparar_configuracion():
    for config in AppConfig.query.filter(AppConfig.clave.in_(('manual_columns','app_schema'))).all():
        try:cols=json.loads(config.valor)
        except ValueError:continue
        if not isinstance(cols,list):continue
        for c in cols:
            if not isinstance(c,dict):continue
            if isinstance(c.get('opciones'),list):
                c['opciones']=[v for v in c['opciones'] if familia(v) in ('','INTEGRATEL')]
            if normalizar(c.get('nombre')) in ETIQUETAS:
                c['opciones']=['FLM - INTEGRATEL'] if c.get('nombre')=='PROYECTO' else ['INTEGRATEL']
        config.valor=json.dumps(cols,ensure_ascii=False)
    db.session.commit()

def instalar(app):
    @app.before_request
    def limitar_destino():
        if not current_app.config.get('MODUS_SCOPE'):return
        payload=request.get_json(silent=True) if request.is_json else {}
        valores=[]
        for mapping in (request.args,request.form,request.view_args or {},payload or {}):
            for k in ('pid','proyecto_id','flm_id'):
                if mapping.get(k) is not None:valores.append(mapping[k])
        if request.headers.get('X-Nucleus-Project'):valores.append(request.headers['X-Nucleus-Project'])
        for v in valores:
            try:p=db.session.get(Proyecto,int(v))
            except (ValueError,TypeError):return jsonify(error='Proyecto inválido.'),400
            if not p or p.nombre not in MODULOS:return jsonify(error='Este proyecto no pertenece a Modus.'),403
        nombre=session.get('current_proyecto_nombre')
        if isinstance(payload,dict):
            cambios=payload.get('data')
            if isinstance(cambios,dict):adaptar_datos(nombre,cambios)
            if payload.get('field') is not None:
                adaptar_datos(nombre,{payload['field']:payload.get('value')})
        if session.get('user_id') and nombre and nombre not in MODULOS:
            p=Proyecto.query.filter_by(nombre='FLM - INTEGRATEL').first()
            session['current_proyecto_id']=p.id;session['current_proyecto_nombre']=p.nombre
    if not getattr(instalar,'evento',False):
        @event.listens_for(db.session,'before_flush')
        def validar_escrituras(sess,*args):
            if not current_app.config.get('MODUS_SCOPE'):return
            for obj in list(sess.new)+list(sess.dirty):
                if isinstance(obj,Proyecto) and obj.nombre not in MODULOS:
                    raise BadRequest('Modus solo dispone de los módulos de Integratel.')
                if isinstance(obj,NucleusData):
                    p=db.session.get(Proyecto,obj.proyecto_id)
                    if not p or p.nombre not in MODULOS:raise BadRequest('Proyecto ajeno a Modus.')
                    obj.data_json=json.dumps(adaptar_datos(p.nombre,json.loads(obj.data_json or '{}')),ensure_ascii=False)
        instalar.evento=True
