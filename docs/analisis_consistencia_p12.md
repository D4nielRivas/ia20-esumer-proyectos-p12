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
| A9 | Los enlaces de la ficha técnica apuntaban a archivos inexistentes | Corregidos a `../README.md`, `otros/V1 …pdf`, el análisis y el prompt | Ficha técnica (cabecera) |
| A10 | Las historias «H-1 a H-7» no estaban definidas y se confundían con los hitos H1–H6 | Mapa H-1…H-8 propuesto y aprobado; el número es el orden de implementación | Ficha técnica §4; PROMPT_SPEC |
| A11 | Quién despliega: la ficha técnica y el curso dicen que el equipo aplica `003-despliegue-gcp`; el marco del prompt dice que despliega el docente | **Despliega el docente.** No hay spec 003 y el cronograma y el Demo quedaron ajustados. ⚠ Esto se aparta del índice del curso: confírmalo con el docente | Ficha técnica §4, §6, §7 y §8; README §4.4 |
| A12 | El stack común le asigna a p12 un «modelo tabular» | No aplica | Ficha técnica (cabecera) |
| A13 | El resumen diario (por estado, modalidad y canal) frente a P-12 (por estado y canal) | Por estado, modalidad y canal | README P-12 |
| A14 | El nombre de la carpeta (`ia20-esumer-proyecto-p12`) y la estructura `bitacora/…/h1…h6` frente al repo real y a la estructura del curso | Repo `ia20-esumer-proyectos-p12`, con spec y código en la raíz según la estructura del curso (`README.md`, `PROMPT_SPEC.md`, `docs/`, `insumos/`) | README ficha y Anexo B; ficha técnica §1 |
| A15 | Git registraba las carpetas como `Docs/` e `Insumos/`, con mayúscula, aunque el curso exige minúsculas (macOS no muestra la diferencia; GitHub sí) | Renombradas en Git a `docs/` e `insumos/` | Repositorio |
| A16 | El prompt vivía en `prompt/`, pero el curso pide `PROMPT_SPEC.md` en la raíz | Movido a `PROMPT_SPEC.md`; se eliminó `prompt/` | Repositorio |
| A17 | Las políticas de la ficha técnica §5 se guardaban en Cloud Storage, pero el stack exige que no haya estado en disco | Puerto «fuente de documentos» (carpeta local o `gs://`); solo la ingesta lee | PROMPT_SPEC «Integración» |

## B. Ambigüedades del alcance

| # | Ambigüedad | Decisión |
|---|---|---|
| B1 | «Una opción por categoría» con varios menús; ME y MS son categorías distintas | La unidad es el almuerzo: 1 principal (ME **o** MS), 1 sopa y 1 jugo; un pedido puede tener varios almuerzos; R12 se valida por almuerzo |
| B2 | ¿Son obligatorios la sopa y el jugo? | Vienen incluidos y el cliente elige cuáles; puede pedir «sin sopa» o «sin jugo», y queda en notas |
| B3 | Ventana de pedido y hora límite | Solo pedidos para el mismo día; recogida entre máx(11:30, confirmación + 15 min) y 15:30, con margen configurable |
| B4 | Política de cancelación | Antes de confirmar, en la conversación; después, solo con el operador y sin penalidad |
| B5 | Medios de pago | Al recoger: efectivo, tarjeta o transferencia (Nequi o Daviplata); el bot no cobra |
| B6 | Retención de datos (Ley 1581) | Pedidos 90 días y conversaciones 30, configurables |
| B7 | Alérgenos: la ficha los mostraba, pero los insumos no los traen | Fuera de esta fase; se quitaron del modelo y de la vista de cocina |
| B8 | RNF2 (99 % mensual) frente a un despliegue que escala a cero y se borra el mismo día | RNF2 retirado; el número se conserva para no alterar las referencias |
| B9 | RNF1 (≤ 10 s) frente al arranque en frío | Se mide en caliente; el arranque en frío se documenta aparte |
| B10 | Existencias por opción, por ingrediente o por conteo | Disponibilidad booleana por opción y fecha; cupo opcional |
| B11 | `es_fijo` sin definir | Es informativo: la opción se repite todos los días |
| B12 | `insumos/menus_diarios` (duplicado sin cabecera) y `Comandos útiles.csv` (apuntes de git) dentro de insumos | El duplicado se borró; los apuntes se movieron a `docs/otros/` |
| B13 | No había documentos de políticas para el RAG | Se escribieron cuatro borradores v0.1 en `insumos/politicas/` para que Tomasseli los valide |
| B14 | ¿Ollama cuenta como «proveedor aprobado»? | Sí, para el perfil local; Vertex AI para el perfil gcp |
| B15 | La vista de cocina en la nube necesita acceso protegido | La página pide la `X-API-Key` y la envía sin guardarla; cocina solo lee |

## C. Pendientes (no los resuelve el equipo)

- Validar con Tomasseli los borradores de `insumos/politicas/`, los precios vigentes, los responsables de cada Form y del resumen diario, y el responsable de privacidad.
- Confirmar con el docente que el despliegue en GCP lo hace el docente (A11).
- Construir los sets de prueba (30 conversaciones y 15 preguntas): los define la spec y los construyen las tareas.
