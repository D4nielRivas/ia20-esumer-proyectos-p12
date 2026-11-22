# Recortes y desvíos frente a la ficha y la guía del curso · P12

La guía de implementación del curso (22 Nov 2026) dice: «Mientras se decide, trabaje con el alcance de la ficha. Si un recorte se acepta, déjelo escrito en `docs/`». Este documento lista lo que el equipo propone distinto de la ficha del curso, por qué, y su estado. El alcance vigente del equipo está en el [`README.md`](../README.md).

| # | La ficha del curso pide | El equipo propone | Por qué | Estado |
|---|---|---|---|---|
| 1 | n8n + WhatsApp + Loyverse como orquestación | Servicio propio del chatbot (FastAPI) en lugar de n8n; sin Loyverse en esta fase | El servicio ya recibe el webhook, valida y registra; n8n agregaría otra pieza para desplegar, apagar y mantener, en el proyecto de despliegue más complejo. Loyverse depende de permisos y de una API sin validar, y no hace falta para que cocina consulte `pedidos` | **Resuelto por la guía del 22 Nov:** n8n, WhatsApp real y Loyverse quedan en la spec `003-automatizacion`, opcional y que por ahora no se hace. En esta fase el servicio propio del chatbot hace el flujo |
| 2 | Sin contenido económico (el prompt de referencia trata los precios como cambio de alcance) | El bot informa el precio del menú y un total estimado; no cobra ni pide datos de pago; se paga al recoger | Los insumos traen el precio por categoría y el cliente lo pregunta; un total estimado reduce las diferencias al recoger. No hay pagos en línea, facturación ni conciliación | **Pendiente de aprobación del docente**. Si no se aprueba, se quitan R15, el total estimado (P-02 y P-04) y la sección de precios de la política 04 |
| 3 | Regresión por lote para prever pedidos | ~~Dejarla en NA~~ → **retirado el 22 Nov**: se reincorpora como historia de menor prioridad (H-9), solo informativa | Se alinea con la ficha del curso y con el prompt de referencia del docente | Cerrado: se trabaja con el alcance de la ficha |
| 4 | Alérgenos por producto en el RAG | Política general de alérgenos en el RAG y escalamiento a una persona; sin alérgenos por plato | No hay datos de alérgenos por plato y no se pueden inventar; las preguntas de alérgenos son el tipo «sensible» del set de prueba | **Pendiente de confirmación del docente**. Si Tomasseli entrega los alérgenos por plato, se agregan al catálogo |
| 5 | Domicilios y zonas en el RAG | ~~Sin domicilios~~ → **22 Nov:** política de domicilios en el RAG (`07_domicilios.md`): 1 km a la redonda, cargo de $5.000 COP, mismo horario, transferencia previa que el operador confirma antes de despachar o efectivo total al domiciliario. El bot explica y deriva; el operador confirma la dirección y registra el pedido con modalidad `domicilio` | Se alinea con la guía. El bot no toma el domicilio de punta a punta para no sumar dirección, radio y pago a la conversación guiada | Alineado con la guía, con el domicilio a cargo del operador |

## Decisiones del equipo que no cambian el alcance del curso

Están documentadas en el README (Anexo A) y en [`analisis_consistencia_p12.md`](analisis_consistencia_p12.md):

- La unidad del pedido es el almuerzo, y la regla de una opción por categoría se valida en cada almuerzo.
- Solo hay pedidos para el mismo día, con 15 minutos de antelación.
- Después de confirmar, los cambios y cancelaciones los hace solo el operador.
- La retención es de 90 días para pedidos y 30 para conversaciones.
- El despliegue lo hace el docente, como dice la guía de implementación (sección 4).

## Decisiones del docente que el equipo adopta (22 Nov 2026)

Tomadas de la guía de implementación del curso y del prompt de referencia del docente; prevalecen sobre versiones anteriores de este repositorio:

- **Specs:** `001-chat-y-politicas-local` (todo lo local: políticas, conversación, pedido y previsión), `002-despliegue-gcp` (la especifica el equipo y la ejecuta el docente) y `003-automatizacion` (opcional; por ahora no va). Reemplazan a `001-politicas-rag-local`, `002-conversacion-y-pedido-servicio` y `003-despliegue-gcp`.
- **Front en Streamlit** como segundo servicio (puerto 8501) que consume FastAPI por `API_URL`; FastAPI es solo el back. Reemplaza las páginas HTML + JavaScript servidas por FastAPI.
- **Previsión servida desde FastAPI:** un comando entrena la regresión de scikit-learn y la guarda con joblib en `app/models/vN/`; FastAPI la carga una vez y `GET /prevision` la sirve y escribe en `prediccion_pedidos`. Sin Cloud Run Job de previsión.
- **Despliegue «probado y apagado»** (rúbrica del PDF, criterio D2 y puerta P2): el docente despliega, prueba con humo y deja Cloud Run con mínimo 0 instancias y Cloud SQL detenida hasta el Demo Day, que se enciende y se vuelve a apagar. Reemplaza el «se borra el mismo día».
- **Datos sintéticos:** `scripts/generar_pedidos_sinteticos.py` → `insumos/historial_pedidos.csv`, con los supuestos en [`datos_sinteticos.md`](datos_sinteticos.md). Diferencia con la guía: la estacionalidad es la semanal más una tendencia leve; no hay efecto mensual ni de quincena.

## Desvíos frente a la guía del docente que el equipo mantiene (22 Nov 2026)

Guía de referencia: presentación 4 (`4_propuestas_proyectos.pdf`) y su versión en texto (`implementacion_proyectos.md`). Cada desvío está en el README (Anexo A) y su razonamiento, en [`analisis_consistencia_p12.md`](analisis_consistencia_p12.md).

| Tema | La guía dice | El equipo hace | Por qué |
|---|---|---|---|
| Conversación | Agente conversacional que toma el pedido | Conversación guiada por reglas (opciones numeradas y estado por conversación); el LLM clasifica la intención y extrae del texto libre hacia el mismo estado (D17) | La guía advierte que `qwen2.5:3b` se equivoca seguido con el JSON del pedido; así la exactitud del pedido no depende del LLM |
| Canal y formularios en la nube | Orquestación con Make o n8n contra la URL de Cloud Run; WhatsApp real en la spec 003 | En la nube, el mismo simulador de WhatsApp que llama Streamlit y los formularios de Streamlit; la firma `X-Hub-Signature-256` solo con una prueba unitaria (D18) | WhatsApp real y n8n están en la 003, que no va; un Google Form necesitaría Apps Script |
| Roles de la base | Mínimo privilegio | Tres roles de PostgreSQL (`p12_admin`, `p12_app`, `p12_cocina`) y claves de API por perfil en FastAPI (D21) | Cumple P-13 con menos configuración en local y en Cloud SQL |
| Construcción de la imagen | Imagen en Artifact Registry; estructura con `.gcloudignore` | Build local `linux/amd64` y `docker push`; nada en Cloud Storage. Se conservan `.dockerignore` (lo usa el build) y `.gcloudignore` (lo pide la estructura) (D22) | `--source` y Cloud Build suben el código a un bucket |
| Set de políticas | 15 preguntas de políticas | 18 preguntas: 6 de documento, 4 fuera de alcance, 4 sensibles y 4 trampa | Supera el mínimo con al menos 4 de cada tipo |
| Alérgenos | Alérgenos por producto en el RAG | Política general y escalamiento a una persona (recorte 4) | No hay datos por plato y no se pueden inventar |
| Carpeta de informes | `reportes/` en la raíz (estructura del PDF) | `docs/informes/` (evaluación local y despliegue), como la guía en texto y la columna «Metas locales» | Decisión del equipo del 22 Nov; los informes son documentación que produce el equipo |
| Ruta del RAG | Ruta común `/preguntar` | `POST /politicas`, como la nombra la diapositiva de P12 | La diapositiva de P12 usa `/politicas` |

## Diferencias en el material del docente

Para comentarle al docente; el repositorio sigue el PDF de la presentación 4:

- El prompt de referencia de P12 (`seleccionados/proyecto-12-…/PROMPT_SPEC.md`) y una tabla de la Fase 2 de `implementacion_proyectos.md` dicen `insumos/politicas/`; el PDF, la recomendación 1 y la columna «Insumos en su sitio» dicen `insumos/base_conocimiento/`, que es la que usa el repo.
- `implementacion_proyectos.md` §9 dice «borrar el mismo día con evidencia»; el PDF (rúbrica final y criterio D2) y la misma guía en §4 dicen «probar y dejar apagado». El repo sigue el PDF.
- La spec de despliegue del ejemplo, de la que debe partir la `002-despliegue-gcp`, no está en el repositorio del curso.
