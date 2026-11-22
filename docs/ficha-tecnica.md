# Proyecto 12 · Del chat a la comanda

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](../README.md) · 📄 [Ficha en PDF](proyecto-12-del-chat-a-la-comanda.pdf) · 🧭 [Análisis de consistencia](analisis_consistencia_p12.md) · 📐 [Prompt de la spec](../PROMPT_SPEC.md)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: cómo se organiza el repositorio, qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs e historias se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de datos y flujo) siguen en la [ficha de especificación](../README.md). Si esta ficha y el README difieren, manda el README.

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **IA** | IA generativa (LLM de un proveedor aprobado, detrás de un adaptador: Ollama, API de Gemini con tope o Vertex AI) para conversación y extracción del pedido; RAG para las políticas; reglas determinísticas para validar y registrar |
| **Machine Learning** | Regresión por lote para la previsión de pedidos del día siguiente (solo informativa, historia de menor prioridad) |
| **API de pago** | Gemini `gemini-3.1-flash-lite`, tope de 1 USD para P12, solo para la evaluación final de la Fase 2 y el Demo Day |
| **Orquestación** | Servicio propio del chatbot en lugar de n8n (recorte pendiente de aprobación del docente, ver [`recortes_p12.md`](recortes_p12.md)); n8n queda para etapas posteriores |
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
├── README.md         # Ficha de especificación
├── PROMPT_SPEC.md    # Prompt con el que se genera la spec (Prompt 1 de Spec Kit)
├── docs/             # Esta ficha, la ficha de especificación en PDF, análisis de consistencia, recortes, informes (docs/informes/) y material del demo
│   └── otros/        # Referencias históricas: especificación v1.2 (no es fuente)
├── insumos/          # CSV del menú (plantilla semanal), base de conocimiento del RAG (base_conocimiento/), sets de prueba e historial para la previsión
├── .specify/ y specs/  # Spec Kit
└── src/ y tests/       # Implementación (Prompt 2)
```

Los nombres de carpeta van en minúscula.

## 2. Dónde entra el RAG

Es el proyecto que mejor enseña el límite del RAG: el menú del día, la disponibilidad y los precios **no** van al RAG porque cambian cada día y deben ser exactos. El RAG responde solo políticas: el horario fijo, la recogida en el sitio (para llevar o para consumir en el sitio) y que no hay domicilios, cómo se arma un pedido, cambios, cancelaciones, medios de pago, alérgenos (en general) y el aviso de privacidad. Las preguntas sensibles (alérgenos de un plato, uso o borrado de datos personales) no se responden de fondo: se escalan a una persona.

| ✅ Va al RAG (`insumos/base_conocimiento/`) | ❌ No va al RAG |
|---|---|
| Horario fijo (lunes a domingo, de 11:30 a 15:30, solo pedidos para el mismo día), recogida solo en el sitio y que no hay domicilios | Menú del día, disponibilidad y precios (PostgreSQL) |
| Cómo se arma un almuerzo (un principal, una sopa, un jugo), cambios, cancelaciones y medios de pago | Pedidos, conversaciones y alertas (PostgreSQL) |
| Política general de alérgenos y aviso de privacidad (Ley 1581) | Previsión de pedidos (regresión por lote, `prediccion_pedidos`) |
| Explicación al cliente de las reglas, por ejemplo por qué no hay domicilios | Validación del pedido: una opción por categoría en cada almuerzo, modalidad, ventana de recogida y total estimado (reglas determinísticas) |

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
| `specs/001-politicas-rag-local/` | Servicio de políticas que el chatbot consulta cuando la intención es `consulta_politica`; escala a una persona las preguntas sensibles. No responde menú, disponibilidad, precios ni pedidos. | H-1 |
| `specs/002-conversacion-y-pedido-servicio/` | Servicio propio del chatbot (sin n8n) y su capa de datos: esquema de PostgreSQL con restricciones y vistas, generación del menú del día desde la plantilla semanal, Forms de menú y agotados, conversación por WhatsApp con las validaciones al cliente, registro idempotente en `pedidos` y `detalle_pedido`, visualización de `pedidos` y `alertas` para cocina, operador y resumen diario en `v_resumen_diario`. Cubre los flujos A a E de la ficha, incluida la previsión de pedidos por lote. | H-2 a H-7 y H-9 |
| `specs/003-despliegue-gcp/` | No se crea en la sesión del Prompt 1: la entrega el docente como copia de la spec de despliegue del ejemplo, con `CODIGO_PROYECTO=p12` y el servicio `chat-a-la-comanda`. El docente pone el proyecto de Google Cloud, los scripts de despliegue y borrado y la configuración de la nube. Dentro de las specs 001 y 002, la Fase 2 queda como historia aparte (H-8). | H-8 |

El número de cada historia es también su orden de implementación, salvo H-9, que se agregó después: va después de H-7 y antes de H-8. Antes de H-1, la fase de *Setup* de las tareas deja la fundación común: perfiles `.env`, puertos y adaptadores (incluido el del LLM con `LLM_PROVEEDOR`), Dockerfile, `/salud`, `docker compose` y el esquema base.

| Historia | Spec | Qué entrega | Pruebas |
|---|---|---|---|
| **H-1** Políticas con citas | 001 | RAG sobre `insumos/base_conocimiento/` con citas validadas, «no lo encuentro» y escalamiento de las preguntas sensibles | P-15, P-16, P-17, P-19 y `insumos/preguntas_politicas.jsonl` |
| **H-2** Menú del día vigente | 002 | Ingesta de la plantilla semanal, generación del menú de cada fecha y consulta por categoría con precios | P-02 |
| **H-3** Pedido completo por WhatsApp ★ MVP | 002 | Conversación, P2 v1.1, validaciones (R1–R5, R8, R11, R12, R15), resumen con total estimado, confirmación y registro idempotente | P-04 a P-09 |
| **H-4** Cocina ve pedidos y alertas | 002 | `v_pedidos_operativa` y alertas en solo lectura, con roles | P-13 |
| **H-5** Forms de menú y agotados | 002 | Alta, cambio y agotado validados, auditados y visibles al bot en ≤ 1 minuto | P-01, P-03 |
| **H-6** Operador y plan B | 002 | Derivación, pausa y reactivación del bot, cambios y cancelaciones después de confirmar, y fallas sin confirmación falsa | P-10, P-11 |
| **H-7** Resumen diario y evaluación final | 002 | `v_resumen_diario`, evaluación completa con `insumos/conversaciones_prueba.jsonl`, `docs/informes/evaluacion_local`, entregables de despliegue e `infra/humo.jsonl` | P-12, P-14 y metas |
| **H-8** Fase 2 en GCP | 001 y 002 | La misma imagen en Cloud Run con el perfil `gcp`, prueba de humo y la misma evaluación contra la URL; la ejecuta el docente cuando H-1 a H-7 pasan la evaluación | Humo + evaluación |
| **H-9** Previsión de pedidos (menor prioridad) | 002 | Historial agregado sintético de 12 semanas, línea base (promedio por día de la semana y franja), regresión con corte cronológico, `prediccion_pedidos`, `GET /prevision` y sección en el resumen diario; solo informativa | P-18 |

El guion del Demo (sección 7) queda cubierto por H-1 a H-7; la previsión (H-9) aparece en el resumen diario si está lista.

## 5. Pruebas locales

- Servicio propio del chatbot en local + PostgreSQL 16 con pgvector en Docker + simulador del webhook de WhatsApp.
- Simulador de los Forms de menú, disponibilidad y agotados: páginas que llaman al mismo endpoint que usarán los Google Forms y escriben en `menu_del_dia`.
- n8n local en Docker: **no aplica** (queda para etapas posteriores).
- 30 conversaciones en `insumos/conversaciones_prueba.jsonl`: pedido completo de uno y de varios almuerzos, datos faltantes, agotado, dos opciones de una categoría en un almuerzo, pedido sin modalidad o con domicilio, hora fuera de la ventana, cambio o cancelación después de confirmar (se deriva al operador), paso a humano, reintento del webhook e inyección.
- 18 preguntas de políticas en `insumos/preguntas_politicas.jsonl`, de los 4 tipos que pide el curso: documento (6), fuera de alcance (4), sensible (4) y trampa (4), cada una con su comportamiento y su documento esperado. Metas: citas válidas 100 % en las de documento, «no lo encuentro» ≥ 90 % en las fuera de alcance, escalamiento ≥ 90 % en las sensibles y 0 trampas exitosas.
- Previsión: error frente a la línea base en las 2 semanas de prueba.
- Ningún pedido duplicado. Las pruebas corren con Ollama o adaptadores falsos; la API de Gemini solo en la evaluación final.

Las metas de la ficha (README §1.7) se registran en `docs/informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 6. Google Cloud (lo despliega el docente)

- Cloud Run: servicio `chat-a-la-comanda` (API y páginas, `PORT` 8080, mínimo 0 y máximo 2 instancias, `X-API-Key`), Cloud Run Job de ingesta y Cloud Run Job de previsión, con la misma imagen.
- Artifact Registry, repositorio `ia20`, con la imagen.
- Cloud SQL for PostgreSQL 16 (db-f1-micro) + pgvector (menú, pedidos, conversaciones, alertas, bitácora, fragmentos de políticas y previsión).
- Vertex AI (Gemini Flash y embeddings `text-multilingual-embedding-002`, dimensión 768) · Cloud Storage (documentos de políticas que lee la ingesta) · Secret Manager.
- WhatsApp Business API (o su entorno de prueba), con webhook `/webhook/whatsapp`, y Google Forms que llaman a `/formularios/menu`.
- n8n Cloud o n8n en Cloud Run: **no aplica** mientras el docente apruebe el recorte de n8n (`recortes_p12.md`).

El equipo entrega la imagen probada en local con lo que exige la Fase 1 (ver `PROMPT_SPEC.md`, sección «Integración»). El docente despliega con el equipo presente y borra todo el mismo día, incluida la instancia de Cloud SQL, con evidencia en `docs/informes/despliegue` y `docs/informes/borrado`. Es el despliegue más complejo: el docente lo ensaya antes de la sesión.

## 7. Guion del Demo (12 min)

El docente **despliega** → cambiar el menú (agotado por Form) → pregunta de política con citas → pedido de dos almuerzos con una validación → pedidos para cocina, cancelación por el operador y resumen diario con la previsión → el docente **borra**.

## 8. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 2), instalar las herramientas (uv, Spec Kit, Docker, Ollama) y escribir la constitución con los principios de la sección 3. | — |
| Hasta el 22 Nov | Fase 1 · Spec | Ajustar el prompt con la revisión del docente, armar los sets de prueba y correr `PROMPT_SPEC.md` para la constitución y las specs `001-politicas-rag-local` y `002-conversacion-y-pedido-servicio` (plan, tareas y análisis). | P0 · spec |
| 23 al 29 Nov | Fase 2 · Implementación local | Implementar con el Prompt 2, historia por historia (H-1 a H-7 y H-9), en local con Ollama; correr las pruebas de la sección 5, calibrar hasta cumplir las metas, usar la API de Gemini solo en la evaluación final y probar la imagen con `docker build` y `docker run`. | P1 · `v1.0-local` |
| 30 Nov al 6 Dic | Fase 3 · Google Cloud con el docente | El docente despliega la imagen con `003-despliegue-gcp`; se verifica con la prueba de humo y la evaluación (H-8) y se borra el mismo día. Sin clase el 5 y 6 de diciembre. | P2 · nube |
| 12 y 13 Dic | Demo | Etiqueta `v1.0-demo` el 12 de diciembre. El 13, el docente despliega desde cero; el equipo presenta con el guion de la sección 7; el docente borra con evidencia y revoca la key de Gemini. | Demo · `v1.0-demo` |
