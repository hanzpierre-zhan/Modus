# Importación FLM–Integratel en Modus

Formato de referencia: ExportResult_20261012164418.xlsx (12 de octubre de 2026).
Solo afecta importaciones base de **FLM - INTEGRATEL** en Modus.

- El identificador es **Ticket ID**, mostrado como **Ticket ID (WO)**.
- Las 24 columnas del exportable reemplazan el esquema de columnas importadas.
- Las columnas manuales mantienen configuración, valores y atributos de layout.
- Las claves internas de registros, evidencias y cruces no cambian: se usa el
  valor completo de Ticket ID, sin transformar prefijos ni fechas.
- Compatibilidad interna: Ticket ID → Número de WO; Ticket Status → Estado de
  la tarea (WO State); Created At → Fecha de creación (WO Creation date).
  Estos alias no se muestran como columnas importadas duplicadas.
- Title no se interpreta automáticamente como Nombre de Site ni se inventan
  equivalencias para otras columnas del formato antiguo.
- Al importar otra vez el mismo ticket se actualiza la fila existente.
- Se rechazan identificadores vacíos, duplicados o inconsistentes con Número
  de WO antes de guardar filas.
- Tras activar el formato nuevo se siguen aceptando archivos antiguos con
  Número de WO; no reemplazan el esquema nuevo ni duplican registros.
- Los registros anteriores no presentes en el archivo conservan sus datos;
  la consolidación por ausencia sigue dependiendo de la configuración existente.

La carga inicial local agregó 5.577 tickets; preservó el registro previo y sus
datos manuales (5.578 filas en total). No hubo ignorados ni consolidados.
Se validó primero sobre una copia de la base local y se guardó una copia de
respaldo antes de aplicar la importación. La carga local no carga la base Neon
del despliegue: allí se debe desplegar el cambio e importar el exportable.
