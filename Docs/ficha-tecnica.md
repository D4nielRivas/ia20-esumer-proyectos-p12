# Proyecto 12 · Del chat a la comanda

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](README.md) · 📄 [Ficha en PDF](proyecto-12-del-chat-a-la-comanda.pdf) · 🗂️ [Volver al índice de proyectos](../README.md) · 🗓️ [Flujo de trabajo y cronograma](../README.md#flujo-de-trabajo-y-cronograma)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de ML y flujo) siguen en la [ficha de especificación](README.md).

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **IA** | IA generativa (LLM de un proveedor aprobado) para conversación y extracción del pedido; reglas determinísticas para validar y registrar |
| **Machine Learning** | No aplica en este alcance |
| **Orquestación** | n8n, como único orquestador en etapas posteriores |
| **Base de conocimiento del RAG** | Políticas de la panadería |
| **Complejidad del despliegue** | Alto |
| **Código del proyecto** | `p12` |
| **Servicio en Cloud Run** | `chat-a-la-comanda` |
| **Proyecto de Google Cloud** | `ia20-p12-<equipo>` |
| **Orden en el Demo** | 7 de 7 |

## 1. Dónde entra el RAG

Es el proyecto que mejor enseña el límite del RAG: el menú del día y la disponibilidad **no** van al RAG porque cambian cada día y deben ser exactos. El RAG responde solo políticas: el horario fijo, la recogida en el sitio (para llevar o para consumir en el sitio) y que no hay domicilios, además de cambios, cancelaciones y medios de pago.

| ✅ Va al RAG | ❌ No va al RAG |
|---|---|
| Horario fijo (lunes a domingo, de 11:30 a 15:30), recogida solo en el sitio (para llevar o para consumir en el sitio) y que no hay domicilios | Menú del día y disponibilidad (PostgreSQL) |
| Cambios, cancelaciones y medios de pago | Pedidos y alertas (PostgreSQL) |
| Explicación al cliente de las reglas, por ejemplo por qué no hay domicilios | Validación del pedido: una opción por categoría, modalidad y hora de recogida (reglas determinísticas) |

> Un buen diseño **no mete todo en el RAG**: lo que cambia cada día o debe ser exacto va en tablas y reglas, y lo sensible lo decide una persona.

## 2. Principios propios de la constitución
El archivo `.specify/memory/constitution.md` del equipo parte de los **7 principios comunes** (ver el [flujo de trabajo](../README.md#flujo-de-trabajo-y-cronograma)) y suma estos, propios del proyecto:

1. El LLM no confirma disponibilidad de memoria.
2. El RAG solo responde políticas.
3. Pedidos sin duplicados (identificador único); WhatsApp solo para órdenes.
4. Cocina consulta directamente `pedidos` y `alertas`: la información es unidireccional y no hay generación adicional de comanda.
5. Una opción por categoría, recogida en el sitio y horario fijo se validan con reglas determinísticas, no con el RAG.


## 3. Specs de Spec Kit

| Spec | Qué construye |
|---|---|
| `specs/001-politicas-rag-local/` | Servicio de políticas que el servicio propio del chatbot consulta cuando la intención del cliente es una consulta de políticas: horario fijo de lunes a domingo de 11:30 a 15:30, recogida solo en el sitio (para llevar o para consumir en el sitio, sin domicilios), cambios, cancelaciones y medios de pago. No responde menú, disponibilidad ni pedidos. |
| `specs/002-conversacion-y-pedido-servicio/` | Servicio propio del chatbot (sin n8n) y su capa de datos: esquema de PostgreSQL con restricciones y vistas, Forms de actualización de menú y disponibilidad, conversación por WhatsApp con las validaciones al cliente, registro del pedido en `pedidos` y `detalle_pedido`, visualización de `pedidos` y `alertas` para cocina, y resumen diario en `v_resumen_diario`. Cubre los flujos A a D de la ficha de especificación. |
| `specs/003-despliegue-gcp/` | Copia de la spec de despliegue del ejemplo, con `CODIGO_PROYECTO=p12` y el servicio `chat-a-la-comanda`, adaptada para incluir Cloud SQL for PostgreSQL y el borrado de todos los recursos el mismo día. |

Cada spec recorre el ciclo `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`.

## 4. Pruebas locales

- Servicio propio del chatbot en local + PostgreSQL local en Docker + simulador del webhook de WhatsApp.
- n8n local en Docker: **NA** (n8n queda para etapas posteriores).
- Simulador de los Forms de menú, disponibilidad y agotados (cambios validados que escriben en `menu_del_dia`).
- 30 conversaciones: pedido completo, datos faltantes, agotado, dos opciones de una misma categoría, pedido sin modalidad o con solicitud de domicilio, hora fuera de 11:30 a 15:30, cambio o cancelación, y paso a humano.
- 15 preguntas de políticas; ningún pedido duplicado.


Las metas se registran en `informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 5. Google Cloud

- Cloud Run: servicio `chat-a-la-comanda`, con `/politicas` y el endpoint del webhook de WhatsApp (nombre por definir).
- Cloud SQL for PostgreSQL (base de datos de pedidos y menús).
- Vertex AI (Gemini y embeddings) · Cloud Storage (documentos de políticas).
- WhatsApp Business API (o su entorno de prueba) y Forms de actualización de menú.
- n8n Cloud (prueba) o una VM e2-small que se borra: **NA**.

> Es el despliegue más complejo: ensayarlo dos veces.

Lo que se despliega se **borra el mismo día**, incluida la instancia de Cloud SQL, con evidencia en `informes/despliegue` e `informes/borrado`.

## 6. Guion del Demo (12 min)

**Desplegar** → Cambiar el menú → Pregunta de política → Pedido completo → Pedidos para cocina y resumen → **Borrar**

## 7. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 1), instalar las herramientas y escribir la constitución con los principios de la sección 2. | — |
| 21 Nov | Crear la spec e implementarla | Escribir y aclarar `001-politicas-rag-local` y `002-conversacion-y-pedido-servicio`, generar plan y tareas, armar el set de prueba e implementar por historia (H-1 a H-7). | P0 · spec |
| 22 al 27 Nov | Solución de temas locales | Correr las pruebas de la sección 4, corregir y calibrar hasta cumplir las metas. | P1 · `v1.0-local` |
| 28 y 29 Nov | Despliegue en la nube | Aplicar `003-despliegue-gcp`: desplegar, verificar y borrar (sección 5). | P2 · nube |
| 1 al 6 Dic | Bootcamp | No hay clase. | — |
| 12 y 13 Dic | Demo | Desplegar desde cero, presentar con el guion de la sección 6 y borrar con evidencia. | Demo · `v1.0-demo` |
