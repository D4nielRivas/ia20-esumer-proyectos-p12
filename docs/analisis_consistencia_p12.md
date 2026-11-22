# Análisis de consistencia · Proyecto 12 «Del chat a la comanda»

Registro de las inconsistencias encontradas entre `README.md`, `docs/ficha-tecnica.md`, `insumos/`, la especificación v1.2 (`docs/otros/`) y el marco del curso (`contenido-ia20-esumer/projects/README.md`), y de cómo se resolvió cada una (21 Nov 2026). El equipo tomó cada decisión; las que dependen del negocio las confirma Tomasseli en el piloto (README, Anexo A).

**Fuente de verdad:** `README.md`. La ficha técnica la complementa en lo técnico y `PROMPT_SPEC.md` la aplica a Spec Kit. Lo que esté en `docs/otros/` es histórico.

## A. Inconsistencias entre documentos

| # | Qué chocaba | Decisión | Dónde quedó |
|---|---|---|---|
| A1 | La v1.2 (Google Sheets, Loyverse, comanda impresa, n8n, Gmail, ML, domicilios, desayunos) frente al README | Manda el README; la v1.2 queda como histórica | README «Origen y alcance»; PROMPT_SPEC «Fuentes» |
| A2 | El README no mencionaba el RAG que define la ficha técnica | El RAG de políticas es alcance: se agregaron RF12, R14, P-15 a P-17 y filas en §2.4, §3.1 y §1.7 | README |
| A3 | P2 no distinguía una consulta de política ni podía señalar un domicilio, y sus campos estaban en inglés mientras las tablas están en español | P2 v1.1 en español: `intencion` (con `consulta_menu` y `consulta_politica`), `almuerzos[]`, `domicilio_solicitado` y nombres iguales a las columnas | README §3.6 |
| A4 | El modelo de datos (menú por fecha, con cupo, alérgenos y vigencia) frente a los insumos (plantilla semanal sin esos campos) | Nuevas tablas `categorias_menu`, `catalogo_items` y `plantilla_menu`; `menu_del_dia` se genera por fecha la primera vez que se consulta cada día; cupo opcional | README §3.2 y flujo A |
| A5 | Los insumos traen precios, pero la ficha excluía todo contenido económico | Precios informativos y total estimado; el bot no cobra; R15 | README ficha, R15, P-02, P-04 |
| A6 | Un `pedido_id` único no impide el duplicado si el webhook se reintenta | `pedidos.mensaje_origen_id` único y tabla `mensajes_procesados` | README RNF3, R5, §3.2, P-09 |
| A7 | La pausa del bot y la vista de conversaciones no tenían dónde guardarse | Tabla `conversaciones`, sin texto completo de los mensajes | README §3.2, RF8 |
| A8 | Los «7 principios comunes» se citaban, pero no estaban en el repo, y el Anexo B traía 5 distintos | Se copiaron los 7 del índice de proyectos del curso; los 5 del Anexo B quedan como «Principios de trabajo del curso» | README Anexo B; ficha técnica §3 |
| A9 | Los enlaces de la ficha técnica apuntaban a archivos inexistentes | Corregidos a `../README.md`, el PDF, el análisis y el prompt | Ficha técnica (cabecera) |
| A10 | Las historias «H-1 a H-7» no estaban definidas y se confundían con los hitos H1–H6 | Mapa H-1…H-8 propuesto y aprobado; el número es el orden de implementación | Ficha técnica §4; PROMPT_SPEC |
| A11 | Quién despliega: la ficha técnica y el curso dicen que el equipo aplica `003-despliegue-gcp`; el marco del prompt dice que despliega el docente | **Despliega el docente.** No hay spec 003 y el cronograma y el Demo quedaron ajustados. ⚠ Esto se aparta del índice del curso: confírmalo con el docente | Ficha técnica §4, §6, §7 y §8; README §4.4 |
| A12 | El stack común le asigna a p12 un «modelo tabular» | No aplica | Ficha técnica (cabecera) |
| A13 | El resumen diario (por estado, modalidad y canal) frente a P-12 (por estado y canal) | Por estado, modalidad y canal | README P-12 |
| A14 | El nombre de la carpeta (`ia20-esumer-proyecto-p12`) y la estructura `bitacora/…/h1…h6` frente al repo real y a la estructura del curso | Repo `ia20-esumer-proyectos-p12`, con spec y código en la raíz según la estructura del curso (`README.md`, `PROMPT_SPEC.md`, `docs/`, `insumos/`) | README ficha y Anexo B; ficha técnica §1 |
| A15 | Git registraba las carpetas como `Docs/` e `Insumos/`, con mayúscula, aunque el curso exige minúsculas (macOS no muestra la diferencia; GitHub sí) | Renombradas en Git a `docs/` e `insumos/` | Repositorio |
| A16 | El prompt vivía en `prompt/`, pero el curso pide `PROMPT_SPEC.md` en la raíz | Movido a `PROMPT_SPEC.md`; se eliminó `prompt/` | Repositorio |
| A17 | Las políticas de la ficha técnica §5 se guardaban en Cloud Storage, pero el stack exige que no haya estado en disco | Puerto «fuente de documentos» (carpeta local o `gs://`); solo la ingesta lee | PROMPT_SPEC «Integración» |
| A18 | El PDF de la ficha (V1, en `docs/otros/`) describía el alcance antiguo: Google Sheets, Loyverse, comanda impresa, n8n, ML y domicilios | Se regeneró desde el README actual y se movió a `docs/proyecto-12-del-chat-a-la-comanda.pdf`; la V1 se borró (22 Nov 2026) | `docs/` |

## B. Ambigüedades del alcance

| # | Ambigüedad | Decisión |
|---|---|---|
| B1 | «Una opción por categoría» con varios menús; ME y MS son categorías distintas | La unidad es el almuerzo: 1 principal (ME **o** MS), 1 sopa y 1 jugo; un pedido puede tener varios almuerzos; R12 se valida por almuerzo |
| B2 | ¿Son obligatorios la sopa y el jugo? | Vienen incluidos y el cliente elige cuáles; puede pedir «sin sopa» o «sin jugo», y queda en notas |
| B3 | Ventana de pedido y hora límite | Solo pedidos para el mismo día; recogida entre máx(11:30, confirmación + 15 min) y 15:30, con margen configurable |
| B4 | Política de cancelación | Antes de confirmar, en la conversación; después, solo con el operador y sin penalidad |
| B5 | Medios de pago | Al recoger: efectivo, tarjeta o transferencia (Nequi o Daviplata); el bot no cobra |
| B6 | Retención de datos (Ley 1581) | Pedidos 90 días y conversaciones 30, configurables |
| B7 | Alérgenos: la ficha los mostraba, pero los insumos no los traen | Fuera de esta fase; se quitaron del modelo y de la vista de cocina. **Revisado el 22 Nov (D3):** política general en el RAG y escalamiento a una persona |
| B8 | RNF2 (99 % mensual) frente a un despliegue que escala a cero y se borra el mismo día | RNF2 retirado; el número se conserva para no alterar las referencias |
| B9 | RNF1 (≤ 10 s) frente al arranque en frío | Se mide en caliente; el arranque en frío se documenta aparte |
| B10 | Existencias por opción, por ingrediente o por conteo | Disponibilidad booleana por opción y fecha; cupo opcional |
| B11 | `es_fijo` sin definir | Es informativo: la opción se repite todos los días |
| B12 | `insumos/menus_diarios` (duplicado sin cabecera) y `Comandos útiles.csv` (apuntes de git) dentro de insumos | El duplicado se borró; los apuntes se movieron a `docs/otros/` |
| B13 | No había documentos de políticas para el RAG | Se escribieron cuatro borradores v0.1 para que Tomasseli los valide; el 22 Nov se sumaron alérgenos y aviso de privacidad (seis en total, en `insumos/base_conocimiento/`) |
| B14 | ¿Ollama cuenta como «proveedor aprobado»? | Sí, para el perfil local; Vertex AI para el perfil gcp |
| B15 | La vista de cocina en la nube necesita acceso protegido | La página pide la `X-API-Key` y la envía sin guardarla; cocina solo lee |

## C. Pendientes (no los resuelve el equipo)

- Validar con Tomasseli los borradores de `insumos/base_conocimiento/`, los precios vigentes, los responsables de cada Form y del resumen diario, y el responsable de privacidad.
- Aprobación del docente para los recortes de `docs/recortes_p12.md` (n8n, precios y alérgenos por plato).
- Historial real de pedidos para reemplazar el sintético de la previsión.

## D. Revisión del docente (22 Nov 2026)

Fuentes: `contenido-ia20-esumer/projects/guias/4_propuestas_proyectos.pdf`, `implementacion_proyectos.md` y el prompt de referencia de P12 (`seleccionados/proyecto-12-del-chat-a-la-comanda/PROMPT_SPEC.md`). El docente revisó el repo en su estado del 21 Nov (carpetas `Docs/` e `Insumos/`, prompt en `prompt/`, sin políticas), así que varios pendientes ya estaban resueltos.

| # | Qué pide el docente | Estado antes | Decisión del equipo | Dónde quedó |
|---|---|---|---|---|
| D1 | `PROMPT_SPEC.md` en la raíz, rama `main`, Paso 0 apuntando al repo del equipo, `docs/` e `insumos/` en minúscula | Ya cumplido el 21 Nov (A15, A16) | Paso 0 apunta a `D4nielRivas/ia20-esumer-proyectos-p12` y verifica `main` | PROMPT_SPEC |
| D2 | Base de conocimiento en `insumos/base_conocimiento/` (guía general); el prompt de referencia de P12 usa `insumos/politicas/` | `insumos/politicas/` | `insumos/base_conocimiento/`, como la guía general | Todo el repo |
| D3 | RAG con alérgenos por producto y aviso de privacidad («faltan alérgenos y políticas») | Cuatro políticas, sin alérgenos ni privacidad | `05_alergenos.md` (política general, sin datos por plato) y `06_aviso_privacidad.md` (borrador v0.1); las preguntas de alérgenos de un plato y de datos personales se escalan (R16) | `insumos/base_conocimiento/`, README R16, P-19 |
| D4 | Set de prueba con los 4 tipos (documento, fuera de alcance, sensible y trampa), mínimo 15, cada una con su documento esperado («falta el tipo sensible») | No existía | 18 preguntas (6, 4, 4 y 4) y las 30 conversaciones de la ficha técnica, validadas contra el menú de cada día | `insumos/preguntas_politicas.jsonl`, `insumos/conversaciones_prueba.jsonl` |
| D5 | Previsión de pedidos por regresión por lote («Regresión en NA» marcada como recorte en discusión) | NA | Se reincorpora como H-9, de menor prioridad: día siguiente, franjas de 30 minutos y opción; historial sintético de 12 semanas (10 + 2, corte cronológico); `GET /prevision` y resumen diario | README RF13, R17, §2.5, P-18; ficha técnica §4 |
| D6 | n8n + WhatsApp + Loyverse (recorte en discusión) | Back propio | Se mantiene el back propio y se documenta como recorte pendiente | `docs/recortes_p12.md` |
| D7 | Precios: el prompt de referencia los trata como cambio de alcance | Precios informativos | Se mantienen y se documentan como recorte pendiente | `docs/recortes_p12.md` |
| D8 | API de Gemini para P12 (tope de 1 USD), con caché, contador `uso_llm`, temperatura 0 y máximo 400 tokens, solo para la evaluación final y el Demo | No estaba | Adaptador `LLM_PROVEEDOR=ollama|gemini`, tablas `uso_llm` y `cache_llm`, regla R18 | README §3.2, R18, §3.4; PROMPT_SPEC |
| D9 | Despliegue: lo hace el docente; la spec 003 la entrega el docente | «No hay spec 003» | El docente entrega `specs/003-despliegue-gcp/`; Cloud Run con máximo 2 instancias, db-f1-micro, Artifact Registry, us-central1 y 10 USD | Ficha técnica §4 y §6 |
| D10 | Evaluación en `docs/informes/evaluacion_local`; comandos locales en una sección nueva del README; commits «p12-spec:» solo con archivos de la spec | `informes/`, `docs/ejecucion_local.md`, «p12:» | Se alinea con el docente | PROMPT_SPEC, ficha técnica |
| D11 | Cronograma: spec hasta el 22 Nov, local del 23 al 29 Nov, Google Cloud del 30 Nov al 6 Dic, `v1.0-demo` el 12 Dic y Demo el 13 Dic | Fechas anteriores | Se actualiza | Ficha técnica §8 |
| D12 | Contrato de rutas escrito, con JSON de entrada y salida | Rutas listadas sin JSON | La spec lo deja en `contracts/` (el prompt lo exige) | PROMPT_SPEC |
| D13 | Orden de las specs (guía del 22 Nov): `001-chat-y-politicas-local`, `002-despliegue-gcp` (la ejecuta el docente) y `003-automatizacion` (opcional) | `001-politicas-rag-local`, `002-conversacion-y-pedido-servicio` y `003-despliegue-gcp` | Se adoptan los nombres del docente: H-1 a H-7 y H-9 en la 001; la 002 la especifica el equipo y el docente la despliega (H-8). Reemplaza D9 en lo que toca a la spec | PROMPT_SPEC, ficha técnica §4, §6 y §8, README Anexo A |
| D14 | Front en Streamlit (segundo servicio, puerto 8501); FastAPI solo back | Páginas HTML + JavaScript servidas por FastAPI | Se adopta Streamlit | PROMPT_SPEC, README §3.1, §4.1 y Anexo A, ficha técnica §5 y §6 |
| D15 | Modelos de ML en Python dentro de FastAPI (`app/models/vN/`, cargados una vez y expuestos como ruta) | Comando por lote y Cloud Run Job de previsión | Un comando entrena y guarda con joblib; FastAPI carga el modelo y `GET /prevision` calcula y guarda en `prediccion_pedidos` la previsión del día siguiente, si no existe; sin Cloud Run Job de previsión | PROMPT_SPEC, README §2.5 y §3.1, ficha técnica §4 y §6 |
| D16 | Datos sintéticos con `scripts/generar_pedidos_sinteticos.py` → `insumos/historial_pedidos.csv` y supuestos en `docs/datos_sinteticos.md` | `scripts/generar_historial.py` → `insumos/historial_pedidos.jsonl`, sin documento de supuestos | Se renombran y se documentan; la estacionalidad queda como semanal más tendencia (sin efecto mensual ni de quincena), señalado como diferencia | `docs/datos_sinteticos.md`, README §2.5 |
