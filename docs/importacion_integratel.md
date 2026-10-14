# Importación FLM–Integratel en Modus

Formato vigente: Export_All_Tab_custom.xlsx (corrección del 14 de octubre de 2026).
Reemplaza el exportable Ticket ID que se proporcionó por error.
Solo afecta importaciones base de **FLM - INTEGRATEL** en Modus.

- El identificador es **Task Id**, mostrado como **Task Id (WO)**.
- Las 95 columnas del exportable reemplazan el esquema de columnas importadas.
- `Sla` pertenece al archivo fuente y se conserva; no es el SLA calculado retirado.
- Las columnas manuales mantienen configuración, valores y atributos de layout.
- Las claves internas de registros, evidencias y cruces no cambian: se usa el
  valor completo de Task Id, sin transformar prefijos ni fechas.
- Compatibilidad interna: Task Id → Número de WO; Task Status → Estado de
  la tarea (WO State); Createtime → Fecha de creación (WO Creation date).
  Site Id, Site Id Name y Site Priority alimentan sus equivalentes de site.
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

La carga corregida local actualiza 1.851 registros y agrega 154 (2.005 tareas).
Por petición del usuario se eliminaron los 3.726 registros activos ausentes,
con respaldo previo. Quedan exactamente 2.005 tareas del archivo correcto.
La gestión manual de las tareas coincidentes se conserva. No hubo ignorados
ni consolidados en la importación.
Se validó primero sobre una copia de la base local y se guardó una copia de
respaldo antes de aplicar la importación. La carga local no carga la base Neon
del despliegue: allí se debe desplegar el cambio e importar el exportable.
