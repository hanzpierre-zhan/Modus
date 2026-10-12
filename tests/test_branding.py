import io
from PIL import Image
from db import db
from models import TokenStore
from services.branding import LOGO_KEY


def test_logo_upload_persists_and_is_resized(auth_client, app):
    file = io.BytesIO()
    Image.new('RGB', (640, 320), 'blue').save(file, 'JPEG')
    file.seek(0)
    response = auth_client.post('/api/branding/logo', data={'file': (file, 'logo.jpg')})
    assert response.status_code == 200
    assert '/api/branding/logo?v=' in response.json['url']
    result = auth_client.get(response.json['url'])
    assert result.mimetype == 'image/png'
    assert Image.open(io.BytesIO(result.data)).size == (256, 128)
    page = auth_client.get('/salud')
    assert response.json['url'].encode() in page.data
    assert b'sidebar-logo-change' in page.data
    with app.app_context():
        TokenStore.query.filter_by(clave=LOGO_KEY).delete()
        db.session.commit()


def test_logo_rejects_invalid_file_and_preserves_default(auth_client):
    response = auth_client.post('/api/branding/logo', data={'file': (io.BytesIO(b'not an image'), 'fake.png')})
    assert response.status_code == 400
    assert auth_client.get('/api/branding/logo').status_code == 302


def test_logo_requires_admin_and_login(auth_client, client):
    assert client.get('/api/branding/logo').status_code == 401
    with auth_client.session_transaction() as session:
        session['rol'] = 'gestor'
    assert auth_client.post('/api/branding/logo', data={}).status_code == 403
