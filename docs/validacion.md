# Verificación de la separación · 12/10/2026

- Nucleus: 132 pruebas de los flujos originales en base temporal.
- Modus: 132 pruebas heredadas más 3 pruebas del límite Integratel (135 en total).
- JavaScript renderizado: 5 módulos y 40 bloques sin errores de sintaxis.
- Base separada: `PRAGMA foreign_key_check` sin referencias inválidas.
- Vista local: login, navegación Integratel, detalle de WO y tema claro/oscuro revisados en navegador.
- Los adjuntos locales de los registros conservados mantienen sus rutas e identificadores. El manifiesto no encontró referencias a archivos locales faltantes en la selección.

Las pruebas automatizadas se ejecutan en bases aisladas. Las conexiones a Render, B2, OneDrive y SharePoint no se verificaron contra servicios de producción: Modus no tiene esas credenciales ni está desplegado.

La copia de operación proviene de la base local y contiene 1 WO Integratel, 1 cotización y 53 rendiciones. El maestro compartido de Sites, Generadores y los demás recursos requieren clasificación de operador antes de la migración final; no se asignaron registros de otros operadores para llenar estas tablas.
