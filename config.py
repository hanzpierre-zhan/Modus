# -*- coding: utf-8 -*-
"""Configuración por entorno (12-factor). Las claves se leen de variables de
entorno. DATABASE_URL se resuelve en tiempo de create_app() para permitir
override en tests y despliegues."""
import os
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _normalizar_db_url(url):
    """Convierte postgres:// -> postgresql+psycopg2://, limpia channel_binding
    y asegura sslmode=require para conexiones cloud.

    Fuerza el driver psycopg2 (postgresql+psycopg2://) porque SQLAlchemy 2.x
    usa por defecto psycopg v3 cuando solo se especifica 'postgresql://',
    y el paquete instalado es psycopg2-binary, no psycopg.
    """
    if not url:
        return url
    u = url.strip()
    if u.startswith('sqlite:'):
        return u
    # Normalizar esquemas antiguos y forzar driver psycopg2
    if u.startswith('postgres://'):
        u = 'postgresql+psycopg2://' + u[len('postgres://'):]
    elif u.startswith('postgresql://'):
        u = 'postgresql+psycopg2://' + u[len('postgresql://'):]
    # Eliminar parámetro channel_binding (no soportado por psycopg2)
    u = re.sub(r'[?&]channel_binding=[^&]*', '', u)
    if 'sslmode=' not in u:
        sep = '&' if '?' in u else '?'
        u = f'{u}{sep}sslmode=require'
    return u


class Config:
    """Configuración base — válida para todos los entornos."""
    TESTING = False
    DEBUG = False
    MODUS_SCOPE = True
    SESSION_COOKIE_NAME = 'modus_session'
    _sk = os.environ.get('MODUS_SECRET_KEY')
    if not _sk:
        # Generar una clave aleatoria para evitar el default inseguro
        import secrets
        _key_dir = os.path.join(BASE_DIR,'instance')
        os.makedirs(_key_dir,exist_ok=True)
        _key_file=os.path.join(_key_dir,'session.key')
        if os.path.isfile(_key_file):
            with open(_key_file,encoding='utf-8') as _f:_sk=_f.read().strip()
        else:
            _sk = secrets.token_urlsafe(64)
            with open(_key_file,'x',encoding='utf-8') as _f:_f.write(_sk)
        # No la persistimos en disco; en producción debe definirse SECRET_KEY
    SECRET_KEY = _sk
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    _INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(_INSTANCE_DIR, exist_ok=True)
    EVIDENCIA_DIR = os.path.join(_INSTANCE_DIR, 'evidencia')
    EVIDENCIA_MAX_LADO = int(os.environ.get('EVIDENCIA_MAX_LADO', 1280))
    EVIDENCIA_CALIDAD = int(os.environ.get('EVIDENCIA_CALIDAD', 80))
    # Backblaze B2
    B2_ENDPOINT_URL = os.environ.get('MODUS_B2_ENDPOINT_URL', '')
    B2_KEY_ID = os.environ.get('MODUS_B2_KEY_ID', '')
    B2_APP_KEY = os.environ.get('MODUS_B2_APP_KEY', '')
    B2_BUCKET = os.environ.get('MODUS_B2_BUCKET', '')
    B2_REGION = os.environ.get('MODUS_B2_REGION', 'us-west-004')
    # OneDrive backup 1
    OD_CLIENT_ID = os.environ.get('MODUS_OD_CLIENT_ID', '')
    OD_CLIENT_SECRET = os.environ.get('MODUS_OD_CLIENT_SECRET', '')
    OD_REFRESH_TOKEN = os.environ.get('MODUS_OD_REFRESH_TOKEN', '')
    OD_ENABLED = bool(OD_CLIENT_ID and OD_REFRESH_TOKEN)
    # OneDrive backup 2
    OD_CLIENT_ID_2 = os.environ.get('MODUS_OD_CLIENT_ID_2', '')
    OD_CLIENT_SECRET_2 = os.environ.get('MODUS_OD_CLIENT_SECRET_2', '')
    OD_REFRESH_TOKEN_2 = os.environ.get('MODUS_OD_REFRESH_TOKEN_2', '')
    OD_ENABLED_2 = bool(OD_CLIENT_ID_2 and OD_REFRESH_TOKEN_2)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pool optimizado para Postgres remoto (Neon): cada conexión nueva cuesta
    # ~0.5-1s (TLS), así que se reutilizan agresivamente y se reciclan antes
    # del idle-timeout de Neon (~5 min). pre_ping evita conexiones muertas.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 10,
        'pool_recycle': 280,
        'pool_timeout': 30,
        'connect_args': {'connect_timeout': 10},
    }

    @classmethod
    def get_sqlalchemy_uri(cls):
        url = os.environ.get('MODUS_DATABASE_URL', '').strip()
        if url:
            return _normalizar_db_url(url)
        return 'sqlite:///' + os.path.join(BASE_DIR, 'modus.db').replace('\\', '/')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'test-secret'
    MODUS_SCOPE = False  # Permite ejecutar las pruebas heredadas en una DB temporal.


def get_default_config():
    env = os.environ.get('FLASK_ENV', '').strip().lower()
    return {'development': DevelopmentConfig,
            'testing': TestingConfig}.get(env, ProductionConfig)
