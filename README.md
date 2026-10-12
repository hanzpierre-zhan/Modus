# Modus

**M.O.D.U.S. — Módulos de Operación, Despacho, Umbrales y Seguimiento.**

Aplicación independiente para la operación Integratel, creada desde Nucleus el 12/10/2026. Incluye FLM Integratel, Personal, Materiales, Sites, Mapa, Generadores, Combustible, Cotizaciones, Rendición, Liquidaciones, Usuarios y Analytics.

## Ejecutar localmente

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\iniciar.ps1
```

Abrir http://127.0.0.1:5002. Los usuarios conservados mantienen sus credenciales locales. La cuenta de vista previa solo existe en una base temporal de QA.

## Independencia

- Base local: `modus.db`. El archivo original de Nucleus permanece intacto.
- Adjuntos: `instance/evidencia` y `static/evidencia`, conservando los identificadores de los registros para mantener sus enlaces.
- Cookie `modus_session`; preferencias de tema `modus-theme`.
- Configuración externa `MODUS_DATABASE_URL`, `MODUS_SECRET_KEY`, `MODUS_B2_*`, `MODUS_OD_*`. No se reutiliza `DATABASE_URL` de Nucleus.
- No se copiaron tokens cloud. Usar almacenamiento propio de Modus al desplegar.
- En una base nueva sin usuarios, definir `MODUS_ADMIN_USERNAME` y `MODUS_ADMIN_PASSWORD`; no se crea un administrador con contraseña predeterminada.
- `instance/session.key` estabiliza la sesión local; no se versiona. En producción configurar `MODUS_SECRET_KEY` explícitamente.
- Los módulos y las escrituras se limitan a Integratel. No basta ocultar los otros operadores en el menú.

## Datos separados

Se utilizó la **base local** de Nucleus, no la base actual de Render. El resumen está en [docs/separacion.json](docs/separacion.json). Los registros de catálogos sin identificación de operador no se asignan automáticamente; deben revisarse antes de la migración definitiva. No se borró ningún dato de Nucleus.

Los avisos históricos se omitieron porque no contienen una referencia al registro que permita separarlos por operador; Modus genera sus avisos nuevos normalmente.

No se han creado servicios de hosting ni se ha desplegado Modus. `Procfile` mantiene `gunicorn app:app`. Configurar una base y almacenamiento exclusivos antes de publicar.

## Verificar

```powershell
python -m pytest tests -q
```

Las pruebas heredadas utilizan una base temporal y desactivan el límite de operador para verificar compatibilidad. `tests/test_modus.py` activa ese límite y comprueba navegación, restricciones de escritura y recursos Integratel. La vista de QA opcional se inicia con `python tools/vista_previa.py` en el puerto 5003 y usa una copia temporal independiente.
