# Proyecto 12 · Del chat a la comanda

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](../README.md) · 📄 [Ficha en PDF (V1, histórica)](otros/V1%20proyecto-12-del-chat-a-la-comanda.pdf) · 🧭 [Análisis de consistencia](analisis_consistencia_p12.md) · 📐 [Prompt de la spec](../PROMPT_SPEC.md)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: cómo se organiza el repositorio, qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs e historias se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de datos y flujo) siguen en la [ficha de especificación](../README.md). Si esta ficha y el README difieren, manda el README.

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **IA** | IA generativa (LLM de un proveedor aprobado) para conversación y extracción del pedido; RAG para las políticas; reglas determinísticas para validar y registrar |
| **Machine Learning** | No aplica en este alcance (tampoco el «modelo tabular» del stack común) |
| **Orquestación** | No aplica en esta fase; n8n será el único orquestador en etapas posteriores |
| **Base de conocimiento del RAG** | Políticas de la panadería (`insumos/politicas/`) |
| **Complejidad del despliegue** | Alta |
| **Código del proyecto** | `p12` |
| **Servicio en Cloud Run** | `chat-a-la-comanda` |
| **Proyecto de Google Cloud** | `ia20-p12-<equipo>` (lo crea y administra el docente) |
| **Despliegue en GCP** | Lo hace el docente con el equipo presente, con la misma imagen probada en local |
| **Orden en el Demo** | 7 de 7 |

## 1. Repositorio del equipo

```text
ia20-esumer-proyectos-p12/
├── README.md         # Ficha de especificación
├── PROMPT_SPEC.md    # Prompt con el que se genera la spec (Prompt 1 de Spec Kit)
├── docs/             # Esta ficha, análisis de consistencia, informes y material del demo
│   └── otros/        # Referencias históricas: especificación v1.2 y PDF V1 (no son fuente)
├── insumos/          # CSV del menú (plantilla semanal) y políticas (insumos/politicas/)
├── .specify/ y specs/  # Spec Kit
└── src/ y tests/       # Implementación (Prompt 2)
```

Los nombres de carpeta van en minúscula.

## 2. Dónde entra el RAG

Es el proyecto que mejor enseña el límite del RAG: el menú del día, la disponibilidad y los precios **no** van al RAG porque cambian cada día y deben ser exactos. El RAG responde solo políticas: el horario fijo, la recogida en el sitio (para llevar o para consumir en el sitio) y que no hay domicilios, cómo se arma un pedido, cambios, cancelaciones y medios de pago.

| ✅ Va al RAG (`insumos/politicas/`) | ❌ No va al RAG |
|---|---|
| Horario fijo (lunes a domingo, de 11:30 a 15:30, solo pedidos para el mismo día), recogida solo en el sitio y que no hay domicilios | Menú del día, disponibilidad y precios (PostgreSQL) |
| Cómo se arma un almuerzo (un principal, una sopa, un jugo), cambios, cancelaciones y medios de pago | Pedidos, conversaciones y alertas (PostgreSQL) |
| Explicación al cliente de las reglas, por ejemplo por qué no hay domicilios | Validación del pedido: una opción por categoría en cada almuerzo, modalidad, ventana de recogida y total estimado (reglas determinísticas) |

> Un buen diseño **no mete todo en el RAG**: lo que cambia cada día o debe ser exacto va en tablas y reglas, y lo sensible lo decide una persona.

## 3. Principios propios de la constitución

El archivo `.specify/memory/constitution.md` parte de los **7 principios comunes del curso**, listados en el [Anexo B de la ficha](../README.md#los-7-principios-comunes-de-la-constitución): fundamentado o nada; curaduría antes que código; local primero, nube igual; evaluación antes de desplegar; persona en el circuito; privacidad y seguridad; y costo cero en reposo. A esos suma estos, propios del proyecto:

1. El LLM no confirma disponibilidad ni precios de memoria: los toma de las tablas.
2. El RAG solo responde políticas, con citas.
3. Pedidos sin duplicados (`pedido_id` y `mensaje_origen_id` únicos); WhatsApp solo para órdenes.
4. Cocina consulta directamente `pedidos` y `alertas`: la información es unidireccional y no hay generación adicional de comanda.
5. Una opción por categoría en cada almuerzo, recogida en el sitio y ventana de recogida se validan con reglas determinísticas, no con el LLM ni con el RAG.

## 4. Specs e historias de Spec Kit

| Spec | Qué construye | Historias |
|---|---|---|
| `specs/001-politicas-rag-local/` | Servicio de políticas que el chatbot consulta cuando la intención es `consulta_politica`. No responde menú, disponibilidad, precios ni pedidos. | H-1 |
| `specs/002-conversacion-y-pedido-servicio/` | Servicio propio del chatbot (sin n8n) y su capa de datos: esquema de PostgreSQL con restricciones y vistas, generación del menú del día desde la plantilla semanal, Forms de menú y agotados, conversación por WhatsApp con las validaciones al cliente, registro idempotente en `pedidos` y `detalle_pedido`, visualización de `pedidos` y `alertas` para cocina, operador y resumen diario en `v_resumen_diario`. Cubre los flujos A a D de la ficha. | H-2 a H-7 |
| Fase 2 (GCP) | Historia aparte dentro de cada spec. No hay spec `003-despliegue-gcp`: el docente pone el proyecto de Google Cloud, los scripts de despliegue y borrado y la configuración de la nube. | H-8 |

El número de cada historia es también su orden de implementación. Antes de H-1, la fase de *Setup* de las tareas deja la fundación común: perfiles `.env`, puertos y adaptadores, Dockerfile, `/salud`, `docker compose` y el esquema base.

| Historia | Spec | Qué entrega | Pruebas |
|---|---|---|---|
| **H-1** Políticas con citas | 001 | RAG sobre `insumos/politicas/` con citas validadas y «no lo encuentro» | P-15, P-16, P-17 y las 15 preguntas |
| **H-2** Menú del día vigente | 002 | Ingesta de la plantilla semanal, generación del menú de cada fecha y consulta por categoría con precios | P-02 |
| **H-3** Pedido completo por WhatsApp ★ MVP | 002 | Conversación, P2 v1.1, validaciones (R1–R5, R8, R11, R12, R15), resumen con total estimado, confirmación y registro idempotente | P-04 a P-09 |
| **H-4** Cocina ve pedidos y alertas | 002 | `v_pedidos_operativa` y alertas en solo lectura, con roles | P-13 |
| **H-5** Forms de menú y agotados | 002 | Alta, cambio y agotado validados, auditados y visibles al bot en ≤ 1 minuto | P-01, P-03 |
| **H-6** Operador y plan B | 002 | Derivación, pausa y reactivación del bot, cambios y cancelaciones después de confirmar, y fallas sin confirmación falsa | P-10, P-11 |
| **H-7** Resumen diario y evaluación final | 002 | `v_resumen_diario`, evaluación completa, `informes/evaluacion_local`, entregables de despliegue e `infra/humo.jsonl` | P-12, P-14 y metas |
| **H-8** Fase 2 en GCP | 001 y 002 | La misma imagen en Cloud Run con el perfil `gcp`, prueba de humo y la misma evaluación contra la URL; la ejecuta el docente cuando H-1 a H-7 pasan la evaluación | Humo + evaluación |

El guion del Demo (sección 7) queda cubierto por H-1 a H-7.

## 5. Pruebas locales

- Servicio propio del chatbot en local + PostgreSQL 16 con pgvector en Docker + simulador del webhook de WhatsApp.
- Simulador de los Forms de menú, disponibilidad y agotados: páginas que llaman al mismo endpoint que usarán los Google Forms y escriben en `menu_del_dia`.
- n8n local en Docker: **no aplica** (queda para etapas posteriores).
- 30 conversaciones: pedido completo de uno y de varios almuerzos, datos faltantes, agotado, dos opciones de una categoría en un almuerzo, pedido sin modalidad o con domicilio, hora fuera de la ventana, cambio o cancelación después de confirmar (se deriva al operador), paso a humano, reintento del webhook e inyección.
- 15 preguntas de políticas, con al menos 3 sin evidencia y 2 de inyección; ningún pedido duplicado.

Las metas de la ficha (README §1.7) se registran en `informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 6. Google Cloud (lo despliega el docente)

- Cloud Run: servicio `chat-a-la-comanda` (API y páginas, `min-instances 0`) y Cloud Run Job de ingesta con la misma imagen.
- Cloud SQL for PostgreSQL 16 + pgvector (menú, pedidos, conversaciones, alertas, bitácora y fragmentos de políticas).
- Vertex AI (Gemini Flash y embeddings `text-multilingual-embedding-002`, dimensión 768) · Cloud Storage (documentos de políticas que lee la ingesta) · Secret Manager.
- WhatsApp Business API (o su entorno de prueba), con webhook `/webhook/whatsapp`, y Google Forms que llaman a `/formularios/menu`.
- n8n Cloud o una VM: **no aplica**.

El equipo entrega la imagen probada en local con lo que exige la Fase 1 (ver `PROMPT_SPEC.md`, sección «Integración»). El docente despliega con el equipo presente y borra todo el mismo día, incluida la instancia de Cloud SQL, con evidencia en `informes/despliegue` e `informes/borrado`. Es el despliegue más complejo: el docente lo ensaya antes de la sesión.

## 7. Guion del Demo (12 min)

El docente **despliega** → cambiar el menú (agotado por Form) → pregunta de política con citas → pedido de dos almuerzos con una validación → pedidos para cocina, cancelación por el operador y resumen diario → el docente **borra**.

## 8. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 2), instalar las herramientas (uv, Spec Kit, Docker, Ollama) y escribir la constitución con los principios de la sección 3. | — |
| 21 Nov | Crear la spec e implementarla | Correr `PROMPT_SPEC.md` para escribir y aclarar `001-politicas-rag-local` y `002-conversacion-y-pedido-servicio`, generar plan y tareas, armar el set de prueba e implementar historia por historia (H-1 a H-7). | P0 · spec |
| 22 al 27 Nov | Solución de temas locales | Correr las pruebas de la sección 5, corregir y calibrar hasta cumplir las metas, y probar la imagen con `docker build` y `docker run`. | P1 · `v1.0-local` |
| 28 y 29 Nov | Despliegue en la nube con el docente | El docente despliega la imagen, se verifica con la prueba de humo y la evaluación (H-8) y se borra el mismo día. | P2 · nube |
| 1 al 6 Dic | Bootcamp | No hay clase. | — |
| 12 y 13 Dic | Demo | El docente despliega desde cero; el equipo presenta con el guion de la sección 7; el docente borra con evidencia. | Demo · `v1.0-demo` |
