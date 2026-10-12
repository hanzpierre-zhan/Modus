"""Vista de QA aislada: no cambia usuarios ni registros de modus.db."""
import os,sys,sqlite3,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
scratch=root/'scratch';scratch.mkdir(exist_ok=True)
folder=Path(tempfile.mkdtemp(prefix='preview-',dir=scratch))
source=sqlite3.connect('file:'+str(root/'modus.db').replace('\\','/')+'?mode=ro',uri=True)
target=sqlite3.connect(folder/'preview.db');source.backup(target);target.close();source.close()
os.environ['MODUS_DATABASE_URL']='sqlite:///'+str(folder/'preview.db').replace('\\','/')
from app import app
from db import db
from models import Usuario,ConformidadUsuario
from werkzeug.security import generate_password_hash
with app.app_context():
    u=Usuario(username='preview',password_hash=generate_password_hash('preview-local'),rol='zeno',nombre='Vista previa local')
    db.session.add(u);db.session.flush()
    db.session.add(ConformidadUsuario(usuario_id=u.id,version='2026-10-09'));db.session.commit()
app.run(host='127.0.0.1',port=5003,debug=False)
