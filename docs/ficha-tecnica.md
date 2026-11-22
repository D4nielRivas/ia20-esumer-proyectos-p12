# Proyecto 12 · Del chat a la comanda

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](../README.md) · 📄 [Ficha en PDF](proyecto-12-del-chat-a-la-comanda.pdf) · 🧭 [Análisis de consistencia](analisis_consistencia_p12.md) · 📐 [Prompt de la spec](../PROMPT_SPEC.md) · ✅ [Cumplimiento de la guía](cumplimiento_guia_p12.md) · ↔️ [Recortes y desvíos](recortes_p12.md)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: cómo se organiza el repositorio, qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs e historias se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de datos y flujo) siguen en la [ficha de especificación](../README.md). Si esta ficha y el README difieren, manda el README.

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **IA** | IA generativa (LLM de un proveedor aprobado, detrás de un adaptador: Ollama, API de Gemini con tope o Vertex AI) para conversación y extracción del pedido; RAG para las políticas; reglas determinísticas para validar y registrar |
| **Machine Learning** | Regresión por lote para la previsión de pedidos del día siguiente (solo informativa, historia de menor prioridad) |
| **API de pago** | Gemini `gemini-3.1-flash-lite`, tope de 1 USD para P12, solo para la evaluación final de la Fase 2 y el Demo Day |
| **Orquestación** | Servicio propio del chatbot; n8n, WhatsApp real y Loyverse quedan en la spec `003-automatizacion`, opcional (ver [`recortes_p12.md`](recortes_p12.md)) |
| **Base de conocimiento del RAG** | Políticas de la panadería (`insumos/base_conocimiento/`) |
| **Complejidad del despliegue** | Alta |
| **Código del proyecto** | `p12` |
| **Servicio en Cloud Run** | `chat-a-la-comanda` |
| **Proyecto de Google Cloud** | `ia20-p12-<equipo>`, us-central1, presupuesto de 10 USD (lo crea y administra el docente) |
| **Despliegue en GCP** | Lo hace el docente con el equipo presente, con la misma imagen probada en local |
| **Orden en el Demo** | 7 de 7 |

## 1. Repositorio del equipo

```text
ia20-esumer-proyectos-p12/
├── README.md         # Ficha, integrantes, estado y cómo correrlo
├── PROMPT_SPEC.md · .gitignore
├── docs/             # Ficha en PDF, ficha técnica, análisis de consistencia, recortes y desvíos, datos sintéticos, cumplimiento de la guía e informes (docs/informes/)
│   └── otros/        # Referencias históricas (especificación v1.2) y apuntes; no son fuente de la spec
├── insumos/          # Lo que recibe el equipo: base_conocimiento/ (RAG), CSV del menú, sets de prueba e historial sintético
├── scripts/          # generar_pedidos_sinteticos.py y pdf_ficha/ (genera la ficha en PDF)
├── CLAUDE.md · .claude/ · .specify/                     # Al correr Spec Kit
├── specs/001-chat-y-politicas-local/ · 002-despliegue-gcp/
├── pyproject.toml · uv.lock · .env.example               # Al implementar
├── docker-compose.yml                                    # PostgreSQL 16 + pgvector
├── app/              # config.py (perfil local | gcp), api/ (FastAPI), front/ (Streamlit), dominio/, servicios/, adaptadores/ y models/vN/ (modelo + metadata.json)
├── sql/ · tests/     # schema.sql y pruebas
├── Dockerfile · .dockerignore · .gcloudignore
└── infra/humo.jsonl
```

Los nombres de carpeta van en minúscula.

## 2. Dónde entra el RAG

Es el proyecto que mejor enseña el límite del RAG: el menú del día, la disponibilidad y los precios **no** van al RAG porque cambian cada día y deben ser exactos. El RAG responde solo políticas: el horario fijo, la recogida en el sitio (para llevar o para consumir en el sitio), los domicilios (1 km, cargo de $5.000 COP y formas de pago), cómo se arma un pedido, cambios, cancelaciones, medios de pago, alérgenos (en general) y el aviso de privacidad. Las preguntas sensibles (alérgenos de un plato, uso o borrado de datos personales) no se responden de fondo: se escalan a una persona.

| ✅ Va al RAG (`insumos/base_conocimiento/`) | ❌ No va al RAG |
|---|---|
| Horario fijo (lunes a domingo, de 11:30 a 15:30, solo pedidos para el mismo día), recogida en el sitio y domicilios (1 km a la redonda, cargo de $5.000 COP, transferencia previa o efectivo al domiciliario) | Menú del día, disponibilidad y precios (PostgreSQL) |
| Cómo se arma un almuerzo (un principal, una sopa, un jugo), cambios, cancelaciones y medios de pago | Pedidos, conversaciones y alertas (PostgreSQL) |
| Política general de alérgenos y aviso de privacidad (Ley 1581) | Previsión de pedidos (regresión por lote, `prediccion_pedidos`) |
| Explicación al cliente de las reglas, por ejemplo cómo funciona el domicilio y por qué lo atiende una persona | Validación del pedido: una opción por categoría en cada almuerzo, modalidad, ventana de recogida y total estimado (reglas determinísticas) |

> Un buen diseño **no mete todo en el RAG**: lo que cambia cada día o debe ser exacto va en tablas y reglas, y lo sensible lo decide una persona.

## 3. Principios propios de la constitución

El archivo `.specify/memory/constitution.md` parte de los **7 principios comunes del curso**, listados en el [Anexo B de la ficha](../README.md#los-7-principios-comunes-de-la-constitución): fundamentado o nada; curaduría antes que código; local primero, nube igual; evaluación antes de desplegar; persona en el circuito; privacidad y seguridad; y costo cero en reposo. A esos suma estos, propios del proyecto:

1. El LLM no confirma disponibilidad ni precios de memoria: los toma de las tablas.
2. El RAG solo responde políticas, con citas.
3. Pedidos sin duplicados (`pedido_id` y `mensaje_origen_id` únicos); WhatsApp solo para órdenes.
4. Cocina consulta directamente `pedidos` y `alertas`: la información es unidireccional y no hay generación adicional de comanda.
5. Una opción por categoría en cada almuerzo, recogida en el sitio y ventana de recogida se validan con reglas determinísticas, no con el LLM ni con el RAG.
6. Las preguntas sensibles las responde una persona, no el bot.
7. La previsión es solo informativa: nunca cambia disponibilidad, cupos ni la aceptación de pedidos.
8. El gasto del LLM de pago tiene tope en el código.

## 4. Specs e historias de Spec Kit

| Spec | Qué construye | Historias |
|---|---|---|
| `specs/001-chat-y-politicas-local/` | Todo lo local en una spec. **Parte A:** servicio de políticas que el chatbot consulta cuando la intención es `consulta_politica`; escala a una persona las preguntas sensibles; no responde menú, disponibilidad, precios ni pedidos. **Parte B:** servicio propio del chatbot (sin n8n) y su capa de datos: esquema de PostgreSQL con restricciones y vistas, generación del menú del día desde la plantilla semanal, Forms de menú y agotados, conversación por WhatsApp con las validaciones, registro idempotente en `pedidos` y `detalle_pedido`, `pedidos` y `alertas` para cocina, operador, resumen diario en `v_resumen_diario` y previsión de pedidos servida por FastAPI. Front en Streamlit. | H-1 a H-7 y H-9 |
| `specs/002-despliegue-gcp/` | Despliegue en Google Cloud de la misma imagen, a partir de la spec de despliegue del ejemplo del curso, con `CODIGO_PROYECTO=p12` y el servicio `chat-a-la-comanda`. **La especifica el equipo** (spec, plan y tareas) en la sesión del Prompt 1; **el despliegue lo ejecuta el docente**. El equipo deja listos el Dockerfile, `.env.example` e `infra/humo.jsonl`. | H-8 |
| `specs/003-automatizacion/` | **Opcional; por ahora no va** y no se crea en la sesión del Prompt 1: canal real de WhatsApp Business (con la firma `X-Hub-Signature-256` activa) y orquestación (n8n o servicio propio, por definir), Loyverse y avisos. | — |

Orden y nombres según la guía de implementación del curso (22 Nov 2026).

El número de cada historia es también su orden de implementación, salvo H-9, que se agregó después: va después de H-7 y antes de H-8. Antes de H-1, la fase de *Setup* de las tareas deja la fundación común: perfiles `.env`, puertos y adaptadores (incluido el del LLM con `LLM_PROVEEDOR`), Dockerfile, `/salud`, `docker compose` y el esquema base.

| Historia | Spec | Qué entrega | Pruebas |
|---|---|---|---|
| **H-1** Políticas con citas | 001 (parte A) | RAG sobre `insumos/base_conocimiento/` con citas validadas, «no lo encuentro» y escalamiento de las preguntas sensibles | P-15, P-16, P-17, P-19 y `insumos/preguntas_politicas.jsonl` |
| **H-2** Menú del día vigente | 001 (parte B) | Ingesta de la plantilla semanal, generación del menú de cada fecha y consulta por categoría con precios | P-02 |
| **H-3** Pedido completo por WhatsApp ★ MVP | 001 (parte B) | Conversación, P2 v1.1, validaciones (R1–R5, R8, R11, R12, R15), resumen con total estimado, confirmación y registro idempotente | P-04 a P-09 |
| **H-4** Cocina ve pedidos y alertas | 001 (parte B) | `v_pedidos_operativa` y alertas en solo lectura, con el rol `p12_cocina` y su clave de API | P-13 |
| **H-5** Forms de menú y agotados | 001 (parte B) | Alta, cambio y agotado validados, auditados y visibles al bot en ≤ 1 minuto | P-01, P-03 |
| **H-6** Operador y plan B | 001 (parte B) | Derivación, pausa y reactivación del bot, cambios y cancelaciones después de confirmar, y fallas sin confirmación falsa | P-10, P-11 |
| **H-7** Resumen diario y evaluación final | 001 (parte B) | `v_resumen_diario`, evaluación completa con `insumos/conversaciones_prueba.jsonl`, `docs/informes/evaluacion_local`, entregables de despliegue e `infra/humo.jsonl` | P-12, P-14 y metas |
| **H-8** Fase 2 en GCP | 002 | La misma imagen en Cloud Run con el perfil `gcp`, prueba de humo y la misma evaluación contra la URL; la ejecuta el docente cuando H-1 a H-7 pasan la evaluación | Humo + evaluación |
| **H-9** Previsión de pedidos (menor prioridad) | 001 (parte B) | Historial agregado sintético de 12 semanas (`insumos/historial_pedidos.csv`, generado por `scripts/generar_pedidos_sinteticos.py`; supuestos en [`datos_sinteticos.md`](datos_sinteticos.md)), línea base (promedio por día de la semana y franja), regresión de scikit-learn con corte cronológico guardada en `app/models/vN/` y cargada por FastAPI, `GET /prevision`, `prediccion_pedidos` y sección en el resumen diario; solo informativa | P-18 |

El guion del Demo (sección 7) queda cubierto por H-1 a H-7; la previsión (H-9) aparece en el resumen diario si está lista.

## 5. Pruebas locales

- Servicio propio del chatbot en local + PostgreSQL 16 con pgvector en Docker + simulador del webhook de WhatsApp.
- Front en Streamlit (segundo servicio, puerto 8501) que consume FastAPI por `API_URL`: vista de chat sobre el simulador del webhook, vista de cocina, vista del operador y resumen diario con la previsión.
- Simulador de los Forms de menú, disponibilidad y agotados: pantallas de Streamlit que llaman a `POST /formularios/menu` (el mismo endpoint que usarían los Google Forms de la spec 003) y escriben en `menu_del_dia`.
- n8n local en Docker: **no aplica** (queda para etapas posteriores).
- 30 conversaciones en `insumos/conversaciones_prueba.jsonl`: pedido completo de uno y de varios almuerzos, datos faltantes, agotado, dos opciones de una categoría en un almuerzo, pedido sin modalidad o con domicilio, hora fuera de la ventana, cambio o cancelación después de confirmar (se deriva al operador), paso a humano, reintento del webhook e inyección.
- 18 preguntas de políticas en `insumos/preguntas_politicas.jsonl`, de los 4 tipos que pide el curso: documento (6), fuera de alcance (4), sensible (4) y trampa (4), cada una con su comportamiento y su documento esperado. Metas: citas válidas 100 % en las de documento, «no lo encuentro» ≥ 90 % en las fuera de alcance, escalamiento ≥ 90 % en las sensibles y 0 trampas exitosas.
- Previsión: error frente a la línea base en las 2 semanas de prueba.
- Ningún pedido duplicado. Las pruebas corren con Ollama o adaptadores falsos; la API de Gemini solo en la evaluación final.

Las metas de la ficha (README §1.7) se registran en `docs/informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 6. Google Cloud (lo despliega el docente)

- Cloud Run: dos servicios, `chat-a-la-comanda` (FastAPI con el modelo de previsión dentro, `PORT` 8080, mínimo 0 y máximo 2 instancias, `X-API-Key`) y el front en Streamlit (mínimo 0), y un Cloud Run Job de ingesta con la misma imagen. La previsión no lleva Cloud Run Job: la sirve FastAPI.
- Se especifica en `specs/002-despliegue-gcp/`; la escribe el equipo y la ejecuta el docente.
- Artifact Registry, repositorio `ia20`, con la imagen. Se construye en el portátil con `docker buildx build --platform linux/amd64` (el Mac es ARM), se sube con `docker push` y se despliega con `gcloud run deploy --image`. No se usan `--source` ni Cloud Build, que suben el código a un bucket.
- **Nada en Cloud Storage:** políticas, CSV, historial y modelo van en la imagen; los datos, en Cloud SQL; las evidencias, en `docs/informes/`.
- Cloud SQL for PostgreSQL 16 (db-f1-micro) + pgvector (menú, pedidos, conversaciones, alertas, bitácora, fragmentos de políticas y previsión).
- Vertex AI (Gemini Flash y embeddings `text-multilingual-embedding-002`, dimensión 768) · Secret Manager.
- Canal y formularios: los mismos que en local (simulador de WhatsApp que llama Streamlit, con el formato de WhatsApp Cloud API, y formularios de Streamlit contra `/webhook/whatsapp` y `/formularios/menu`). La firma del webhook solo se cubre con una prueba unitaria. WhatsApp Business real y Google Forms quedan para la spec 003.
- n8n Cloud o n8n en Cloud Run: **no aplica** en esta fase; queda en la spec `003-automatizacion`, opcional.

El equipo entrega la imagen probada en local con lo que exige la Fase 1 (ver `PROMPT_SPEC.md`, sección «Integración»). El docente despliega con el equipo presente, prueba con humo y la deja apagada hasta el Demo Day (Cloud Run con mínimo 0 instancias y la instancia de Cloud SQL detenida, que solo cobra el almacenamiento), con evidencia en `docs/informes/despliegue`. Es el despliegue más complejo: el docente lo ensaya antes de la sesión.

## 7. Guion del Demo (12 min)

El docente **enciende** → cambiar el menú (agotado por Form) → pregunta de política con citas → pedido de dos almuerzos con una validación → pedidos para cocina (comanda), cancelación por el operador y resumen diario con la previsión → el docente **apaga**.

## 8. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 2), instalar las herramientas (uv, Spec Kit, Docker, Ollama) y escribir la constitución con los principios de la sección 3. | — |
| Hasta el 22 Nov | Fase 1 · Spec | Ajustar el prompt con la revisión del docente, armar los sets de prueba y correr `PROMPT_SPEC.md` para la constitución y las specs `001-chat-y-politicas-local` y `002-despliegue-gcp` (plan, tareas y análisis). | P0 · spec |
| 23 al 29 Nov | Fase 2 · Implementación local | Implementar con el Prompt 2, historia por historia (H-1 a H-7 y H-9), en local con Ollama; correr las pruebas de la sección 5, calibrar hasta cumplir las metas, usar la API de Gemini solo en la evaluación final y probar la imagen con `docker build` y `docker run`. | P1 · `v1.0-local` |
| 30 Nov al 6 Dic | Fase 3 · Google Cloud con el docente | El docente despliega la imagen con `002-despliegue-gcp`; se verifica con la prueba de humo y la evaluación (H-8) y queda apagado, con evidencia. Etiqueta `v1.0-gcp`. Sin clase el 5 y 6 de diciembre. | P2 · nube |
| 12 y 13 Dic | Demo | Etiqueta `v1.0-demo` el 12 de diciembre. El 13, el docente enciende el despliegue; el equipo presenta con el guion de la sección 7; el docente lo vuelve a apagar y revoca la key de Gemini. | Demo · `v1.0-demo` |
