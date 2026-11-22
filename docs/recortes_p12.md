# Recortes y desvíos frente a la ficha del curso · P12

La guía de implementación del curso (22 Nov 2026) dice: «Mientras se decide, trabaje con el alcance de la ficha. Si un recorte se acepta, déjelo escrito en `docs/`». Este documento lista lo que el equipo propone distinto de la ficha del curso, por qué, y su estado. El alcance vigente del equipo está en el [`README.md`](../README.md).

| # | La ficha del curso pide | El equipo propone | Por qué | Estado |
|---|---|---|---|---|
| 1 | n8n + WhatsApp + Loyverse como orquestación | Servicio propio del chatbot (FastAPI) en lugar de n8n; sin Loyverse en esta fase | El servicio ya recibe el webhook, valida y registra; n8n agregaría otra pieza para desplegar y borrar, en el proyecto de despliegue más complejo. Loyverse depende de permisos y de una API sin validar, y no hace falta para que cocina consulte `pedidos` | El prompt de referencia del docente lo registra como «decisión del equipo»; la guía lo sigue listando como recorte en discusión. **Pendiente de confirmación del docente** |
| 2 | Sin contenido económico (el prompt de referencia trata los precios como cambio de alcance) | El bot informa el precio del menú y un total estimado; no cobra ni pide datos de pago; se paga al recoger | Los insumos traen el precio por categoría y el cliente lo pregunta; un total estimado reduce las diferencias al recoger. No hay pagos en línea, facturación ni conciliación | **Pendiente de aprobación del docente**. Si no se aprueba, se quitan R15, el total estimado (P-02 y P-04) y la sección de precios de la política 04 |
| 3 | Regresión por lote para prever pedidos | ~~Dejarla en NA~~ → **retirado el 22 Nov**: se reincorpora como historia de menor prioridad (H-9), solo informativa | Se alinea con la ficha del curso y con el prompt de referencia del docente | Cerrado: se trabaja con el alcance de la ficha |
| 4 | Alérgenos por producto en el RAG | Política general de alérgenos en el RAG y escalamiento a una persona; sin alérgenos por plato | No hay datos de alérgenos por plato y no se pueden inventar; las preguntas de alérgenos son el tipo «sensible» del set de prueba | **Pendiente de confirmación del docente**. Si Tomasseli entrega los alérgenos por plato, se agregan al catálogo |

## Decisiones del equipo que no cambian el alcance del curso

Están documentadas en el README (Anexo A) y en [`analisis_consistencia_p12.md`](analisis_consistencia_p12.md):

- La unidad del pedido es el almuerzo, y la regla de una opción por categoría se valida en cada almuerzo.
- Solo hay pedidos para el mismo día, con 15 minutos de antelación.
- Después de confirmar, los cambios y cancelaciones los hace solo el operador.
- La retención es de 90 días para pedidos y 30 para conversaciones.
- El despliegue lo hace el docente, como dice la guía de implementación (sección 4).
