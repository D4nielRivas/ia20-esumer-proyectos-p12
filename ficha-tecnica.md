# Proyecto 12 · Del chat a la comanda

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](README.md) · 📄 [Ficha en PDF](proyecto-12-del-chat-a-la-comanda.pdf) · 🗂️ [Volver al índice de proyectos](../README.md) · 🗓️ [Flujo de trabajo y cronograma](../README.md#flujo-de-trabajo-y-cronograma)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de ML y flujo) siguen en la [ficha de especificación](README.md).

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **Machine Learning** | Regresión sobre datos tabulares (previsión de pedidos) |
| **Conexión modelo–flujo** | Lote |
| **Orquestación** | n8n + WhatsApp Business API + Loyverse TPV |
| **Base de conocimiento del RAG** | Políticas de la panadería |
| **Complejidad del despliegue** | Alto |
| **Código del proyecto** | `p12` |
| **Servicio en Cloud Run** | `chat-a-la-comanda` |
| **Proyecto de Google Cloud** | `ia20-p12-<equipo>` |
| **Orden en el Demo** | 7 de 7 |

## 1. Dónde entra el RAG

Es el proyecto que mejor enseña el límite del RAG: el menú y la disponibilidad **no** van al RAG porque cambian cada día y deben ser exactos. El RAG responde solo políticas: horarios, domicilios, cambios, alérgenos y pagos.

| ✅ Va al RAG | ❌ No va al RAG |
|---|---|
| Horarios, domicilios y zonas | Menú, disponibilidad y precios (Sheets) |
| Cambios, cancelaciones y medios de pago | Pedidos (Sheets + Loyverse) |
| Alérgenos por producto y aviso de privacidad | Previsión (regresión por lote) |

> Un buen diseño **no mete todo en el RAG**: lo que cambia cada día o debe ser exacto va en tablas y reglas, y lo sensible lo decide una persona.

## 2. Principios propios de la constitución

El archivo `.specify/memory/constitution.md` del equipo parte de los **7 principios comunes** (ver el [flujo de trabajo](../README.md#flujo-de-trabajo-y-cronograma)) y suma estos, propios del proyecto:

1. El LLM no confirma disponibilidad de memoria.
2. El RAG solo responde políticas.
3. Pedidos idempotentes; WhatsApp solo para órdenes.

## 3. Specs de Spec Kit

| Spec | Qué construye |
|---|---|
| `specs/001-politicas-rag-local/` | Servicio de políticas que n8n consulta cuando la intención del cliente es una consulta. |
| `specs/002-conversacion-y-pedido-n8n/` | Escenarios A a E de la ficha: menú, pedido, cocina, cierre y previsión. |
| `specs/003-despliegue-gcp/` | Copia de la spec de despliegue del ejemplo, con `CODIGO_PROYECTO=p12` y el servicio `chat-a-la-comanda`. |

Cada spec recorre el ciclo `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`.

## 4. Pruebas locales

- n8n local en Docker + simulador del webhook de WhatsApp.
- 30 conversaciones (pedido, faltantes, agotado, paso a humano).
- 15 preguntas de políticas; ningún pedido duplicado.

Las metas se registran en `informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 5. Google Cloud

- Cloud Run: `/politicas`.
- Vertex AI (Gemini y embeddings) · Cloud Storage.
- n8n Cloud (prueba) o una VM e2-small que se borra.

> Es el despliegue más complejo: ensayarlo dos veces.

Lo que se despliega se **borra el mismo día**, con evidencia en `informes/despliegue` e `informes/borrado`.

## 6. Guion del Demo (12 min)

**Desplegar** → Cambiar el menú → Pregunta de política → Pedido completo → Comanda y resumen → **Borrar**

## 7. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 1), instalar las herramientas y escribir la constitución con los principios de la sección 2. | — |
| 21 Nov | Crear la spec e implementarla | Escribir y aclarar `001-politicas-rag-local` y `002-conversacion-y-pedido-n8n`, generar plan y tareas, armar el set de prueba e implementar por historia. | P0 · spec |
| 22 al 27 Nov | Solución de temas locales | Correr las pruebas de la sección 4, corregir y calibrar hasta cumplir las metas. | P1 · `v1.0-local` |
| 28 y 29 Nov | Despliegue en la nube | Aplicar `003-despliegue-gcp`: desplegar, verificar y borrar (sección 5). | P2 · nube |
| 1 al 6 Dic | Bootcamp | No hay clase. | — |
| 12 y 13 Dic | Demo | Desplegar desde cero, presentar con el guion de la sección 6 y borrar con evidencia. | Demo · `v1.0-demo` |
