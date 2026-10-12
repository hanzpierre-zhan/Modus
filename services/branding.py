"""Logo compartido de Modus, persistido en la base de datos."""
import base64
import hashlib
from flask import url_for
from models import TokenStore

LOGO_KEY = 'modus_sidebar_logo'


def logo_url():
    row = TokenStore.query.filter_by(clave=LOGO_KEY).first()
    if row:
        version = hashlib.sha256(row.valor.encode()).hexdigest()[:12]
        return url_for('admin.branding_logo', v=version)
    return url_for('static', filename='img/modus.svg')


def logo_bytes():
    row = TokenStore.query.filter_by(clave=LOGO_KEY).first()
    return base64.b64decode(row.valor) if row else None
