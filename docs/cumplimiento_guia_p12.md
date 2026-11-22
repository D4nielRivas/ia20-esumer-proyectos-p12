# Cumplimiento de la guía del docente · P12

Revisión del repositorio `ia20-esumer-proyectos-p12` frente a la presentación 4 del curso (`4_propuestas_proyectos.pdf`: rúbrica del repositorio, rúbrica final y diapositivas del proyecto 12) y su versión en texto (`implementacion_proyectos.md`). Estado al **22 Nov 2026**, antes de correr `PROMPT_SPEC.md`.

Estados: ✅ cumple · 🟡 parcial · ⏳ corresponde a un corte posterior · ↔️ desvío que el equipo mantiene (ver [`recortes_p12.md`](recortes_p12.md)).

## 1. Rúbrica del repositorio · Corte 1 (desde el 22/11)

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| R1 | Nombre `ia20-esumer-proyectos-p<N>` | ✅ | `ia20-esumer-proyectos-p12` |
| R2 | Todo el trabajo en `main` | 🟡 | Todo está en `main`. En GitHub queda la rama `VeroArci`, sin commits que no estén en `main`; conviene borrarla |
| R3* | Raíz: README, PROMPT_SPEC, `docs/`, `insumos/` | ✅ | Raíz del repositorio |
| R4 | Archivos sin espacios, tildes ni símbolos | ✅ | `docs/otros/Comandos útiles.csv` pasó a `docs/otros/comandos_utiles.csv` (22 Nov) |
| R5 | `.gitignore` con los mínimos | ✅ | `.gitignore` con `.env`, `!.env.example`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `pgdata/`, `.DS_Store` y `.claude/settings.local.json` |
| R6* | Sin secretos, ni en el historial | ✅ | Búsqueda en todo el historial de Git sin llaves ni contraseñas (22 Nov) |
| R7 | Sin datasets ni binarios pesados | ✅ | El archivo más grande es la ficha en PDF (1,3 MB); el historial sintético pesa 236 KB |
| R8 | Commits `tipo(alcance): qué cambió` | 🟡 | El historial anterior tiene commits sin alcance y algunos «Delete …». Desde el 22 Nov los commits usan `tipo(alcance)`; el prompt fija `p12-spec:` para la spec y `test(usN)` y `feat(usN)` para implementar |
| R9 | README con integrantes y estado | ✅ | Sección «Integrantes y estado» del README |
| R10 | `PROMPT_SPEC.md` en la raíz y vigente | ✅ | Revisado el 22 Nov con todas las decisiones (D1 a D27) |

## 2. Rúbrica del repositorio · Cortes 2 a 4

| # | Criterio | Estado | Cómo queda previsto |
|---|---|---|---|
| S1 | `.specify/`, `CLAUDE.md` y `.claude/` | ⏳ Corte 2 | Los crea el Paso 0 de `PROMPT_SPEC.md` |
| S2* | Specs 001 local y 002 GCP completas | ⏳ Corte 2 | `specs/001-chat-y-politicas-local/` y `specs/002-despliegue-gcp/`, hasta `/speckit-analyze` |
| S3 | Commits `p12-spec:` por fase | ⏳ Corte 2 | Exigido en el Paso 0 del prompt |
| C1 | `app/` con api, front, dominio, servicios | ⏳ Corte 3 | Estructura fijada en el prompt (sección «Stack») y en el README (Anexo B) |
| C2 | `pyproject.toml` + `uv.lock` | ⏳ Corte 3 | Python 3.12 + uv |
| C3 | Stack del curso, sin sustitutos | ✅ en el diseño | Streamlit, FastAPI, scikit-learn en `app/models/vN/`, PostgreSQL 16 + pgvector, Ollama → Vertex AI |
| C4* | pytest en verde y `/evaluar` | ⏳ Corte 3 | `POST /evaluar` y TDD en el prompt |
| C5* | Se levanta solo con el README | ⏳ Corte 3 | El prompt exige una sección nueva de comandos en el README (criterio de aceptación de H-7) |
| C6 | ruff sin errores | ⏳ Corte 3 | Exigido en el prompt |
| D1* | Dockerfile probado + humo | ⏳ Corte 4 | Dockerfile, `.dockerignore`, `.gcloudignore` e `infra/humo.jsonl` en el prompt; imagen `linux/amd64` |
| D2 | GCP probado y apagado | ⏳ Corte 4 | Spec 002: el docente despliega, prueba con humo y deja Cloud Run en mínimo 0 y Cloud SQL detenida |
| D3 | Etiquetas `v1.0-local`, `v1.0-gcp`, `v1.0-demo` | ⏳ Cortes 3 y 4 | Fijadas en el prompt y en la ficha técnica §8 |

## 3. Rúbrica final

| Puerta | Lo que se evalúa | Estado |
|---|---|---|
| P0 · Spec (25/11) | Prompt claro en alcance, stack, datos y restricciones del curso | ✅ `PROMPT_SPEC.md` |
| | El prompt crea las specs 001 local y 002 GCP | ✅ Nombres de la guía: `001-chat-y-politicas-local` y `002-despliegue-gcp` |
| | Constitución con los principios del proyecto | ✅ Los 7 comunes más los 8 propios (ficha técnica §3), que incluyen los tres de la diapositiva de P12 |
| | Set de prueba con los 4 tipos de pregunta | ✅ `insumos/preguntas_politicas.jsonl`: 18 preguntas (6, 4, 4 y 4) |
| P1 · `v1.0-local` (29/11) | Stack completo, pruebas en verde y Dockerfile probado | ⏳ |
| P2 · Nube | P12: Dockerfile, `.env.example` y humo listos para el docente; desplegar, probar con humo y dejar apagado | ⏳ Previsto en la spec 002 |
| Demo Day (13/12) | Guion en 12 minutos, demo en vivo y respuestas | ⏳ Guion en la ficha técnica §7 |
| Proceso | Commits por historia en `main`, backlog y ficha al día, uso real de Spec Kit | 🟡 Ficha al día; el resto empieza con la implementación |
| Bono (+5) | Spec 003 de automatización funcionando | No se hace por ahora (opcional) |

## 4. Diapositivas del proyecto 12

| Tema | La guía pide | Estado | Dónde |
|---|---|---|---|
| Stack | Streamlit · FastAPI · regresión (datos sintéticos) · PostgreSQL + pgvector · LLM | ✅ | README §3.1 y Anexo A; PROMPT_SPEC «Stack» |
| RAG | Sí, solo políticas; menú y pedidos en tablas | ✅ | README R14; ficha técnica §2 |
| Va al RAG | Horarios, domicilios y zonas | ✅ | `01_horario_y_recogida.md` y `07_domicilios.md` |
| | Cambios, cancelaciones y medios de pago | ✅ | `03_cambios_y_cancelaciones.md` y `04_medios_de_pago.md` |
| | Alérgenos por producto y aviso de privacidad | ↔️ / ✅ | Alérgenos: política general y escalamiento (recorte 4, pendiente del docente). Privacidad: `06_aviso_privacidad.md` |
| No va al RAG | Menú, disponibilidad y precios; pedidos; previsión (regresión en FastAPI) | ✅ | Tablas de PostgreSQL y `GET /prevision` |
| Principios | El LLM no confirma disponibilidad de memoria; el RAG solo responde políticas; pedidos idempotentes y WhatsApp solo para órdenes | ✅ | Ficha técnica §3 (principios 1 a 3) |
| Specs | `001-chat-y-politicas-local`, `002-despliegue-gcp` (lo despliega el docente), `003-automatizacion` (opcional) | ✅ | PROMPT_SPEC; ficha técnica §4 |
| Pruebas locales | Simulador del webhook + chat en Streamlit | ✅ | Ficha técnica §5 |
| | 30 conversaciones (pedido, faltantes, agotado, humano) | ✅ | `insumos/conversaciones_prueba.jsonl` |
| | 15 preguntas de políticas; ningún pedido duplicado | ✅ ↔️ | 18 preguntas (supera el mínimo); idempotencia con R5 y RNF3 |
| Google Cloud | Cloud Run: Streamlit + FastAPI (`/politicas`, previsión) | ✅ | PROMPT_SPEC, ficha técnica §6 |
| | Vertex AI (Gemini y embeddings) · Cloud SQL | ✅ | Ficha técnica §6 |
| | El equipo entrega Dockerfile, `.env.example` y humo | ✅ previsto | PROMPT_SPEC «Integración» |
| | El despliegue lo hace el docente | ✅ | Spec 002 |
| Guion del Demo | Encender → Cambiar el menú → Pregunta de política → Pedido completo → Comanda y resumen → Apagar | ✅ | Ficha técnica §7; README §4.4 |
| Datos sintéticos | Script con semilla fija y supuestos en `docs/datos_sinteticos.md` | ✅ ↔️ | `scripts/generar_pedidos_sinteticos.py`; la estacionalidad es semanal más tendencia (diferencia documentada) |
| Gasto | API de Gemini con tope de 1 USD para P12 | ✅ | README R18; PROMPT_SPEC |

## 5. Desvíos y pendientes

- **Desvíos que el equipo mantiene:** conversación guiada, simulador y formularios de Streamlit también en la nube, tres roles de PostgreSQL, build local sin Cloud Storage, 18 preguntas, alérgenos sin datos por plato, `POST /politicas` en vez de `/preguntar` e informes en `docs/informes/`. Detalle en [`recortes_p12.md`](recortes_p12.md).
- **Pendientes del docente:** precios informativos (recorte 2), alérgenos (recorte 4), la spec de despliegue del ejemplo para la 002 y si en P12 el equipo escribe los scripts de despliegue de `infra/`.
- **Diferencias en el material del docente:** `insumos/politicas/` frente a `insumos/base_conocimiento/`, y «borrar el mismo día» frente a «dejar apagado». El repositorio sigue el PDF.
- **Siguiente paso:** correr `PROMPT_SPEC.md` antes de la puerta P0 (25 Nov).
