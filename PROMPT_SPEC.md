# 📐 Prompt 1 · Crear solo la spec con Spec Kit · Proyecto 12 «Del chat a la comanda»

Con este prompt se generan **solo los artefactos de especificación** (constitución, `CLAUDE.md`, `.claude/` y `specs/<feature>/`). No se escribe código de la aplicación: el flujo termina en `/speckit-analyze`. Para implementar después, use el Prompt 2 · Implementar la spec.

Parte de la guía 01 del curso y del prompt de referencia que el docente preparó para P12 (`contenido-ia20-esumer/projects/seleccionados/proyecto-12-del-chat-a-la-comanda/PROMPT_SPEC.md`, revisión del 22 Nov 2026), con las decisiones del equipo. Lo que el equipo hace distinto a la ficha del curso está en [`docs/recortes_p12.md`](docs/recortes_p12.md).

## Antes de pegar el prompt

- [x] `PROMPT_SPEC.md` en la raíz, rama `main`, `docs/` e `insumos/` en minúscula.
- [x] `insumos/base_conocimiento/` con un documento por tema: horario y recogida, cómo pedir, cambios y cancelaciones, medios de pago, alérgenos y aviso de privacidad (borradores v0.1).
- [x] `insumos/preguntas_politicas.jsonl`: 18 preguntas de 4 tipos (documento, fuera de alcance, sensible y trampa).
- [x] `insumos/conversaciones_prueba.jsonl`: las 30 conversaciones de la ficha técnica §5.
- [x] `insumos/Comandos útiles.csv` fuera de `insumos/` (ahora en `docs/otros/`).
- [ ] El historial para la previsión (`insumos/historial_pedidos.jsonl`) no existe: lo define la spec y lo genera una tarea, como dato sintético documentado.

## Cómo usarlo

1. Ubíquese en la raíz del repo del proyecto, en la rama `main`:

   ```bash
   cd ia20-esumer-proyectos-p12
   claude --permission-mode acceptEdits
   ```

2. Pegue el prompt completo de abajo.
3. Revise y apruebe `spec.md`, `plan.md` y `tasks.md` de cada spec antes de pasar al Prompt 2.

> 🔌 Lea la sección **«Integración»** del prompt antes de usarlo: todo se construye en local y al final el docente despliega en Google Cloud la misma imagen.
>
> 🧭 Todas las decisiones de alcance están en el `README.md` (Anexo A) y su razonamiento en [`docs/analisis_consistencia_p12.md`](docs/analisis_consistencia_p12.md). Si alguna cambia, cámbiela primero en el README y después en este prompt.
>
> Revise el flag `--no-git` con `specify init --help`, por si su versión de Spec Kit lo nombra distinto.

## Prompt

```text
# Rol
Actúa como ingeniero de software senior y experto en Spec Kit (Spec-Driven Development) y Claude Code.

# Objetivo
Especificar con Spec Kit el «Proyecto 12 · Del chat a la comanda» de Panadería Tomasseli (código p12, servicio de Cloud Run «chat-a-la-comanda»):
- un chatbot de WhatsApp que presenta el menú del día disponible con sus precios, toma el pedido por almuerzos, lo valida con reglas determinísticas y lo registra en PostgreSQL, desde donde la cocina lo consulta directamente;
- un servicio de políticas con RAG que responde con citas y escala a una persona las preguntas sensibles;
- una previsión de pedidos por lote, solo informativa, para apoyar la planeación de cocina.
Regla de oro: la IA propone; el equipo y las personas responsables verifican y deciden.
Fase 1 local; Fase 2 en GCP, con el mismo código y cambiando solo la configuración.
En esta sesión SOLO se crean los artefactos de la spec. No escribas código de la aplicación.

# Fuentes (en este orden de prioridad)
1. README.md: ficha de especificación y fuente de verdad. Contiene:
   - los requisitos RF1–RF13 y RNF1–RNF8 (RNF2 retirado), las restricciones y los indicadores (§1.7);
   - la ficha «¿sí requiere ML?» (§2.5) y el modelo de datos (§3.2);
   - las reglas R1–R18 (§3.3), los prompts P1 v1.1 y P2 v1.1 (§3.6) y las pruebas P-01 a P-19 (§4.3);
   - el plan B (§4.5), las decisiones resueltas y pendientes (Anexo A) y los 7 principios comunes del curso (Anexo B).
2. docs/ficha-tecnica.md: qué va y qué no va al RAG (§2), principios propios (§3), specs e historias H-1 a H-9 (§4), pruebas locales (§5), servicios de GCP (§6), guion del Demo (§7) y cronograma (§8).
3. docs/recortes_p12.md: lo que el equipo hace distinto a la ficha del curso, pendiente de aprobación del docente.
4. docs/analisis_consistencia_p12.md: por qué se tomó cada decisión. Úsalo para justificar; no reabras lo que ya está resuelto.
5. insumos/:
   - categorias_menu.csv, catalogo_items.csv, menus_diarios.csv y detalle_menu_dia.csv: la plantilla semanal del menú;
   - base_conocimiento/*.md: la base de conocimiento del RAG, borradores v0.1 con metadatos de vigencia en el encabezado;
   - preguntas_politicas.jsonl y conversaciones_prueba.jsonl: los sets de prueba.
NO son fuente: docs/otros/ (la especificación v1.2 histórica y apuntes de git). docs/proyecto-12-del-chat-a-la-comanda.pdf es la misma ficha del README en PDF.
Lee las fuentes antes de especificar. Si encuentras un conflicto que el README no resuelva, no lo resuelvas en silencio: regístralo en la sección «Conflictos detectados» de la spec, con la decisión tomada.

# Paso 0 · Preparar el entorno (raíz del repositorio del equipo)
Este proyecto vive en la raíz del repositorio D4nielRivas/ia20-esumer-proyectos-p12, que ya es un repositorio Git con remoto origin. Nunca hagas git init, no crees ni cambies ramas y no hagas push.
1. Verifica que estás en la rama main y que existen README.md, PROMPT_SPEC.md, docs/ (con ficha-tecnica.md) e insumos/ en minúscula. Si faltan los cuatro CSV del menú, los documentos de insumos/base_conocimiento/ o los dos sets de prueba, detente y pídemelos.
2. Si no existe .specify/, inicializa Spec Kit aquí sin git: specify init --here --integration claude --no-git. Verifica .claude/skills/speckit-* y .specify/templates; specs/ queda en la raíz.
3. Crea CLAUDE.md en la raíz con: propósito, stack, comandos, convenciones (español, TDD, un commit por fase) y estas reglas:
   a. El README es la fuente de verdad.
   b. Solo insumos/base_conocimiento/ se indexa en el RAG; el menú, la disponibilidad, los precios y los pedidos nunca van al RAG; docs/otros/ nunca se indexa ni se carga.
   c. El LLM solo propone: no escribe en la base, no confirma disponibilidad ni precios de memoria y no modifica el inventario.
   d. Las preguntas sensibles las responde una persona.
   e. La previsión es informativa y nunca cambia disponibilidad ni la aceptación de pedidos.
   f. Desarrollo y pytest siempre con Ollama o adaptadores falsos; la API de Gemini solo en la evaluación final y el Demo.
4. Crea .claude/settings.json con permisos: permitir uv, pytest, docker compose, git add/commit y edición dentro del repo (nunca en insumos/); negar git push, gcloud y lectura de .env.
5. Usa el .gitignore de la raíz (créalo si falta; si existe, solo añade líneas) para .env, .venv, __pycache__, .pytest_cache y .claude/settings.local.json, y deja versionado .env.example.
6. Commits: un commit por fase de Spec Kit, solo con CLAUDE.md, .claude/, .specify/, specs/ y .gitignore, con prefijo «p12-spec:». No modifiques README.md, PROMPT_SPEC.md, docs/ ni insumos/.

# Specs e historias (ficha técnica §4)
- specs/001-politicas-rag-local/ → H-1 Políticas con citas.
- specs/002-conversacion-y-pedido-servicio/ →
  - H-2 Menú del día vigente.
  - H-3 Pedido completo por WhatsApp (MVP).
  - H-4 Cocina ve pedidos y alertas.
  - H-5 Forms de menú y agotados.
  - H-6 Operador y plan B.
  - H-7 Resumen diario y evaluación final.
  - H-9 Previsión de pedidos (menor prioridad).
- H-8 Fase 2 (GCP): historia aparte en cada spec, dependiente de que H-1 a H-7 pasen la evaluación.
- specs/003-despliegue-gcp/ NO se crea en esta sesión: el docente la entrega como copia de la spec de despliegue del ejemplo, con CODIGO_PROYECTO=p12 y el servicio chat-a-la-comanda.
- Usa exactamente estos identificadores. Orden de implementación: Setup, H-1 a H-7, H-9 y H-8. Antes de H-1, la fase de Setup de tasks.md deja la fundación común: perfiles .env, puertos y adaptadores, Dockerfile, /salud, docker compose y el esquema base.

# Contexto del problema
Panadería Tomasseli recibe pedidos por WhatsApp y debe coordinarlos con la disponibilidad del menú (almuerzos diarios). WhatsApp se usa solo para las órdenes de los clientes, que llegan a la base de datos de pedidos a través de un servicio propio del chatbot. El servicio es fijo, de lunes a domingo de 11:30 a 15:30. Los pedidos son solo para el mismo día y solo de recogida en el sitio, para llevar o para consumir allí; no hay domicilios.
Hoy el menú y las existencias no tienen una fuente única, el pedido se transcribe a mano para cocina y los agotados no se comunican a tiempo. Por eso se ofrecen opciones agotadas, hay reprocesos y demoras, y lo registrado difiere de lo pedido (la línea base se mide en H1).
La solución es un chatbot que le presenta al cliente las opciones disponibles del menú del día por categoría y con precio, toma su pedido por almuerzos y lo registra en PostgreSQL. La cocina consulta directamente la visualización de pedidos y revisa alertas: no hay generación adicional de comanda y la información es unidireccional. La IA generativa facilita la conversación y extrae el pedido; las reglas determinísticas controlan la disponibilidad, la confirmación, el total estimado y el registro. Una regresión por lote prevé los pedidos del día siguiente, solo como información.
Actores:
- cliente (WhatsApp);
- administración (formularios, vistas y resumen diario con la previsión);
- cocina (vista de pedidos y alertas en solo lectura, formulario de agotados);
- operador (vista de conversaciones derivadas; hace los cambios y cancelaciones posteriores a la confirmación y atiende las preguntas sensibles).

# Reglas de negocio clave (detalle en README §3.3; no las reabras en clarify)
- Unidad del pedido: el almuerzo.
  - Cada almuerzo lleva 1 principal (una opción de ME o de MS, nunca ambas), 1 sopa (SP) y 1 jugo (JG).
  - La sopa y el jugo vienen incluidos: el cliente elige cuáles o pide «sin sopa» o «sin jugo», y queda en notas.
  - Un pedido puede tener varios almuerzos, y R12 se valida por almuerzo.
- Ventana (R11): solo pedidos para el mismo día, con hora de recogida entre máx(11:30, hora de confirmación + MARGEN_PREPARACION_MIN) y 15:30, en TZ_NEGOCIO=America/Bogota. MARGEN_PREPARACION_MIN vale 15 por defecto.
- Precios (R15): son informativos. El total estimado lo calculan las reglas con categorias_menu.precio; el bot no cobra ni pide datos de pago, y se paga al recoger.
- Cambios y cancelaciones (R6): antes de confirmar, se hacen en la conversación. Después de confirmar, el bot deriva al operador y no modifica nada.
- Idempotencia (R5, RNF3): pedido_id único, pedidos.mensaje_origen_id único y la tabla mensajes_procesados.
- Menú por fecha (flujo A): menu_del_dia se genera desde plantilla_menu la primera vez que se consulta cada día, sin duplicar, y los formularios lo modifican. Disponibilidad booleana; cupo opcional.
- RAG (R14): solo políticas, con citas validadas; sin evidencia, «no lo encuentro» y operador.
- Preguntas sensibles (R16): alérgenos de un plato, o uso, corrección o borrado de datos personales (propios o de otra persona). El bot no responde de fondo: un clasificador determinístico, antes del LLM, deriva la conversación a una persona.
- Previsión (R17): regresión por lote del día siguiente, por franja de 30 minutos (11:30 a 15:30) y opción. Se publica solo si mejora la línea base (promedio por día de la semana y franja), con fecha y versión; la vencida no se muestra como vigente; nunca cambia disponibilidad, cupos ni la aceptación de pedidos.
- Gasto del LLM (R18):
  - LLM_PROVEEDOR=ollama|gemini; primero la caché (cache_llm);
  - después, el tope: lo gastado en uso_llm se compara con LLM_TOPE_USD=1.00; si se pasó, cae a Ollama o responde 503 con aviso;
  - con Gemini, máximo 400 tokens de salida y temperatura 0.
- Retención (RNF5): pedidos 90 días y conversaciones 30, configurables. No se guarda el texto completo de las conversaciones.

# Requisitos funcionales (trazados al README)
Spec 001:
1. H-1 · RF12, R14 y R16: POST /politicas responde con citas [n] al documento y fragmento de insumos/base_conocimiento/, con las citas validadas por código. Sin evidencia dice «no lo encuentro» y ofrece el operador; escala las preguntas sensibles; nunca responde menú, disponibilidad, precios ni pedidos (P-15, P-16, P-17, P-19).
2. H-1 · Evaluación con insumos/preguntas_politicas.jsonl.
Spec 002:
3. H-2 · RF1 y RF3: ingesta de los CSV a categorias_menu, catalogo_items y plantilla_menu; generación de menu_del_dia por fecha; consulta del menú vigente por categoría con precios (R1, R2, R9; P-02).
4. H-3 · RF4, RF5, RF6 y RF11: conversación con P2 v1.1:
   - presentar el menú y preguntar solo lo que falta;
   - validar (R1–R5, R8, R11, R12, R15);
   - mostrar el resumen con total estimado y recibir la aceptación explícita;
   - revalidar la disponibilidad y registrar de forma idempotente en pedidos y detalle_pedido (P-04 a P-09).
5. H-4 · RF7: v_pedidos_operativa y alertas para cocina, en solo lectura y sin el teléfono completo; roles de PostgreSQL por perfil (R10, R13; P-13).
6. H-5 · RF2: formularios de alta, cambio y agotado validados, auditados en bitacora y reflejados en ≤ 1 minuto (RNF8; P-01, P-03).
7. H-6 · RF8 y RF9: derivación, pausa y reactivación del bot (tabla conversaciones); cambios y cancelaciones después de confirmar solo por el operador; alertas por falla (R6, R7); plan B sin confirmaciones falsas (P-10, P-11).
8. H-7 · RF10: v_resumen_diario por estado, modalidad y canal, con pendientes e incidencias (P-12). Evaluación completa con insumos/conversaciones_prueba.jsonl y P-01 a P-19, con informe en docs/informes/evaluacion_local.
9. H-9 · RF13, R17: previsión de pedidos por lote.
   - La spec define insumos/historial_pedidos.jsonl (fecha, franja, item_id, categoria, cantidad; sin datos personales).
   - Una tarea lo genera de forma sintética y reproducible (semilla fija), con 12 semanas, y lo documenta como dato ficticio.
   - Corte cronológico: 10 semanas para entrenar y 2 para probar.
   - Se compara la regresión con la línea base. La salida va a prediccion_pedidos, GET /prevision y una sección del resumen diario (P-18).
Los sets de prueba ya existen y los revisó el equipo: úsalos tal como están. Si encuentras un caso inconsistente con el README, regístralo en «Conflictos detectados»; no edites insumos/.

# Set de prueba del RAG con los 4 tipos de pregunta (requisito de la puerta P0)
insumos/preguntas_politicas.jsonl trae 18 preguntas, cada una con su tipo, el comportamiento esperado, el documento esperado y si se escala a una persona:
- documento (6): la respuesta está en la base de conocimiento → responde con cita [n] válida.
- fuera de alcance (4): no está en los documentos → «no lo encuentro» y ofrece a la persona responsable.
- sensible (4): alérgenos de un plato, o uso o borrado de datos personales → no responde de fondo y escala a una persona, por regla determinística.
- trampa (4): inyección o premisa falsa → no la obedece, no cambia ningún estado y queda registrada.
Metas del set: citas válidas 100 % en las de documento, «no lo encuentro» ≥ 90 % en las fuera de alcance, escalamiento ≥ 90 % en las sensibles y 0 trampas exitosas.

# Metas de la evaluación local (README §1.7; se recalibran con la línea base de H1)
- ≥ 90 % de las respuestas automatizables en ≤ 10 s, medidas en caliente (RNF1, P-14).
- ≥ 98 % de pedidos confirmados sin corrección atribuible a la captura.
- 100 % de pedidos aceptados vinculados a una opción activa y disponible al confirmar.
- 100 % de pedidos confirmados con modalidad, hora dentro de la ventana y una sola opción por categoría en cada almuerzo.
- 0 pedidos duplicados y 0 confirmaciones falsas ante fallas.
- Políticas: las metas del set de 4 tipos y recuperación ≥ 85 %.
- Previsión: error menor que la línea base en las 2 semanas de prueba; si no la mejora, no se publica y se documenta.
- 0 inyecciones exitosas.
- v_resumen_diario disponible al cierre de cada jornada.

# Stack (va en el plan, no en la spec)
- Front: páginas HTML + JavaScript servidas por FastAPI en / y /static: simulador de chat de WhatsApp, simulador de formularios (alta, cambio, agotado), vista de cocina, vista del operador y resumen diario con la previsión. Consume el back solo por HTTP (API_URL configurable); no tiene reglas de negocio ni llama al LLM. Sin Streamlit.
- Back: FastAPI (OpenAPI) con estas rutas:
  - GET /salud y GET y POST /webhook/whatsapp;
  - POST /politicas, POST /formularios/menu y GET /menu/hoy;
  - GET /cocina/pedidos y GET /cocina/alertas;
  - GET /operador/conversaciones, POST /operador/conversaciones/{id}/reactivar, POST /operador/pedidos/{id}/cambio y POST /operador/pedidos/{id}/cancelacion;
  - GET /resumen-diario, GET /prevision y POST /evaluar.
  Cada ruta queda en contracts/ con su JSON de entrada y de salida.
- Datos: PostgreSQL 16 + pgvector con docker compose, con las tablas del README §3.2.
- IA: LLM detrás de un adaptador (Ollama qwen2.5:3b; API de Gemini gemini-3.1-flash-lite con tope; Vertex AI en GCP) y embeddings bge-m3 (siempre locales en la Fase 1; no se pagan).
- Modelo de ML: regresión por lote para la previsión, como comando (uv run comanda prever), solo informativa.
- Comando de ingesta: uv run comanda ingestar --limpiar.
- Fase 2, GCP (la monta el docente):
  - Cloud Run «chat-a-la-comanda»: PORT 8080, mínimo 0 y máximo 2 instancias.
  - Cloud Run Jobs de ingesta y de previsión, con la misma imagen.
  - Cloud SQL PostgreSQL 16 (db-f1-micro) + pgvector.
  - Vertex AI (Gemini Flash y text-multilingual-embedding-002), Cloud Storage para las políticas, Secret Manager y Artifact Registry.
  - WhatsApp Business API (o su entorno de prueba) y Google Forms que llaman a POST /formularios/menu.
- Fuera de esta fase (márcalo «NA» en la spec, no lo omitas): n8n, reintentos con espera incremental y colas, envío del resumen por Gmail, Loyverse TPV, domicilios, pagos en línea, alérgenos por plato, validación de la gestión de cocina y RNF2.

# Integración: local con el equipo ahora, despliegue en GCP con el docente al final
Nota para el equipo: todo el desarrollo, las pruebas y la evaluación se hacen en el portátil (perfil local, costo cero; la API de Gemini, solo en la evaluación final). Al final, el docente despliega la MISMA imagen en Google Cloud con el equipo presente (perfil gcp, proyecto ia20-p12-<equipo>, us-central1, presupuesto de 10 USD), la prueba y la borra el mismo día, incluida la instancia de Cloud SQL. El código debe quedar listo para la nube desde el primer día: si la spec deja supuestos solo locales (archivos en disco, claves en el código, un puerto fijo, la hora del servidor), el despliegue falla.

Stack común (local → GCP, cambiando solo la configuración RAG_PERFIL=local|gcp):
- Lenguaje y dependencias: Python 3.12 + uv → la misma imagen.
- Servicio (API + páginas): FastAPI con uv run uvicorn en localhost:8000 → Cloud Run (escala a cero).
- Base relacional + vectorial: PostgreSQL 16 + pgvector con docker compose → Cloud SQL PostgreSQL 16 + pgvector.
- LLM: Ollama qwen2.5:3b (7b o 1.5b según la RAM); API de Gemini solo para la evaluación final y el Demo → Vertex AI Gemini Flash.
- Embeddings: Ollama bge-m3 (dimensión 1024) → text-multilingual-embedding-002 (dimensión 768).
- Documentos de políticas: insumos/base_conocimiento/ → bucket de Cloud Storage; solo la ingesta los lee.
- Ingesta y previsión: uv run comanda ingestar --limpiar y uv run comanda prever → Cloud Run Jobs con la misma imagen y los mismos comandos.
- Canal WhatsApp: simulador local con el formato de WhatsApp Cloud API → WhatsApp Business API.
- Formularios: páginas HTML locales → Google Forms, contra el mismo endpoint.
- Configuración: .env leído con pydantic-settings → variables de entorno del despliegue.
- Secretos: .env (nunca en Git) → Secret Manager.
- Modelo tabular: regresión por lote que escribe en prediccion_pedidos → el mismo comando como Cloud Run Job.
- Orquestación: el servicio propio del chatbot reemplaza a n8n (recorte documentado en docs/recortes_p12.md).
- Pruebas: pytest + sets de evaluación → prueba de humo + la misma evaluación contra la URL.

Requisitos no funcionales que deben quedar en la spec y resolverse en el plan:
1. Puertos y adaptadores detrás de una interfaz; el resto del código no sabe en qué perfil corre:
   - LLM: llm_ollama / llm_gemini / llm_vertex;
   - embeddings: emb_ollama / emb_vertex;
   - base: URL local / socket de Cloud SQL;
   - canal: whatsapp_simulador / whatsapp_cloud;
   - fuente de documentos: carpeta local / gs://;
   - reloj: inyectable, para probar la ventana con fecha y hora simuladas.
2. Toda la configuración por variables de entorno, con .env.example completo y documentado y sin secretos. Incluye:
   - RAG_PERFIL, PORT, DATABASE_URL, API_URL, API_KEY y RAG_EMBED_DIM;
   - TZ_NEGOCIO, MARGEN_PREPARACION_MIN, RETENCION_PEDIDOS_DIAS y RETENCION_CONVERSACIONES_DIAS;
   - LLM_PROVEEDOR, LLM_MODELO, LLM_TOPE_USD, LLM_TEMPERATURA, GEMINI_API_KEY (vacía) y los timeouts de RNF1;
   - los tokens de WhatsApp.
   Nada de rutas absolutas, URLs, números de WhatsApp ni claves en el código.
3. Dockerfile desde la fase local. La app escucha en la variable PORT (8080 en la nube) y se prueba con docker run antes de entregar.
4. Sin estado en disco ni en memoria: Cloud Run borra el disco y puede tener varias instancias. Las conversaciones, la pausa del bot, la deduplicación, la caché y el gasto del LLM van a PostgreSQL; el menú y las políticas se cargan con la ingesta.
5. Dimensión del vector parametrizada en RAG_EMBED_DIM (1024 local, 768 nube). El índice de la nube se reconstruye con la ingesta, no se copia.
6. Fechas y horas siempre en TZ_NEGOCIO, nunca la hora del servidor (Cloud Run corre en UTC).
7. Contrato común igual en los dos perfiles:
   - GET /salud sin clave: perfil, estado de la base, modelos, número de fragmentos, opciones del menú de hoy y versiones de la app, de P1, de P2 y del modelo de previsión.
   - Las demás rutas, salvo el webhook, piden la cabecera X-API-Key (401 si falta). Las páginas piden la clave y la envían sin guardarla.
   - El webhook verifica su token y la firma X-Hub-Signature-256 en el perfil gcp.
   - Errores 422 y 503 como {"error","detalle"}.
   - El JSON de salida no cambia entre local y gcp.
8. RNF1: si el LLM o la base no responden dentro del umbral, se informa al cliente, se deriva al operador y nunca se confirma.
9. Mínimo privilegio con roles de PostgreSQL (chatbot, formularios, cocina en solo lectura, operador, administración).
10. Datos personales (Ley 1581):
    - registros sin datos personales;
    - teléfono normalizado que cocina no ve completo;
    - aviso de privacidad en pedidos.aviso_privacidad;
    - purga según RNF5;
    - la previsión, solo con datos agregados;
    - ningún secreto en el repositorio ni en el historial de Git.
11. Trazabilidad: versión de P1, de P2 y del modelo en cada registro de bitacora; tokens y costo de cada llamada pagada en uso_llm.
12. Evaluación reproducible: el mismo set de prueba corre contra localhost y contra la URL de la nube.

Entrega del equipo antes de la sesión de despliegue con el docente (inclúyela como criterio de aceptación de H-7):
- README.md con una sección nueva de comandos para levantarlo en local, sin borrar la ficha del proyecto.
- .env.example con todas las variables de los dos perfiles.
- Dockerfile y .gcloudignore, con la imagen probada en local (docker build + docker run).
- Comando de ingesta que crea el esquema si no existe y carga solo el menú y las políticas vigentes.
- GET /salud funcionando y pruebas en verde.
- docs/informes/evaluacion_local con las metas cumplidas («sin metas cumplidas no hay nube»).
- infra/humo.jsonl con 3 a 5 casos y su resultado esperado: GET /salud, menú de hoy, domicilio rechazado, hora fuera de la ventana y pregunta de política con cita.
NO crees scripts ni recursos de Google Cloud: el docente pone el proyecto de Google Cloud, la spec 003-despliegue-gcp, los scripts de despliegue y borrado y la configuración de la nube.

# Flujo (completo y en orden, sin pedirme confirmación entre pasos)
1. /speckit-constitution (una vez, común a las dos specs): los 7 principios comunes del curso (README, Anexo B) más los 8 propios de la ficha técnica §3.
2. Spec 001-politicas-rag-local: /speckit-specify → /speckit-clarify → /speckit-plan → /speckit-tasks → /speckit-analyze.
3. Spec 002-conversacion-y-pedido-servicio: el mismo ciclo, usando el contrato HTTP de /politicas que dejó la spec 001.
Cómo hacer cada paso:
- /speckit-specify: el qué y el porqué, sin tecnología. Historias H-1…H-9 según la ficha técnica §4, con criterios de aceptación verificables trazados a RF, RNF, R y P del README y a los casos de los sets de prueba. Incluye las secciones «Conflictos detectados», «Recortes pendientes de aprobación» (desde docs/recortes_p12.md) y «Fuera de alcance (NA)».
- /speckit-clarify: responde tú cada pregunta con la opción recomendada y justifícala en una línea en Aclaraciones. Lo que el README resuelve (Anexo A) no se vuelve a preguntar; usa su lista de pendientes como supuestos.
- /speckit-plan con el stack de arriba; debe pasar el Constitution Check. El data-model reproduce el README §3.2 (tablas, PK, FK, UNIQUE, CHECK y vistas) sin cambiar nombres. Los contratos usan P2 v1.1 tal como está en el README §3.6. Documenta en research.md (Decisión / Justificación / Alternativas):
  - Ollama frente a Gemini para la extracción con P2;
  - la deduplicación de mensajes de WhatsApp con varias instancias;
  - regresión lineal frente a árbol de regresión, comparados con la línea base;
  - el simulador de WhatsApp con el mismo formato de la API;
  - la caché y el tope del LLM de pago;
  - el clasificador determinístico de preguntas sensibles.
- /speckit-tasks: fase Setup y luego tareas pequeñas agrupadas por historia (H-1…H-9), ordenadas por dependencia, con las pruebas antes del código.
- /speckit-analyze: corrige toda inconsistencia crítica o alta, también entre 001 y 002 y contra el README (rutas, campos, errores, estados, identificadores de historias y nombres de variables de entorno). Trata como CRÍTICO:
  - una confirmación sin disponibilidad revalidada o sin aceptación del cliente;
  - un pedido duplicado por un reintento del webhook;
  - que el RAG responda menú, disponibilidad, precios o pedidos, o responda de fondo una pregunta sensible;
  - que la previsión cambie disponibilidad, cupos o la aceptación de pedidos;
  - una llamada a la API de pago sin pasar por la caché y el tope.

# Buenas prácticas que deben quedar en la spec, el plan y las tareas
- Pruebas primero (pytest); nunca avanzar con pruebas en rojo.
- Temperatura ≤ 0,2 con Ollama y 0 con Gemini. La salida del LLM sigue P2 v1.1, validada con Pydantic. P1 y P2 están versionados.
- Los mensajes del cliente y los documentos de políticas son datos, nunca instrucciones. Incluye pruebas de inyección y de trampa (P-17 y las preguntas de tipo trampa).
- Ningún secreto en el repo. El .env.example está documentado y la API key es obligatoria. La key de Gemini solo en .env, nunca en Git ni en capturas; el docente la revoca el 13 de diciembre.
- Solo datos ficticios.
- Un commit por fase de Spec Kit, solo con archivos de la spec, con prefijo «p12-spec:».
- Todo en español.

# Puertas y parada
- Si una decisión cambia el alcance o el costo, o contradice el README, detente y pregúntame: por ejemplo, WhatsApp real en local, Streamlit, pagos, domicilios, alérgenos por plato, quitar la previsión, subir el tope del LLM o cualquier ítem marcado NA. Lo demás decídelo y regístralo.
- Termina después de /speckit-analyze de la spec 002. No escribas código de la aplicación. El entregable es solo .claude/, CLAUDE.md, .specify/memory/constitution.md, specs/001-politicas-rag-local/ y specs/002-conversacion-y-pedido-servicio/ (spec, plan, research, data-model, contracts, quickstart, tasks y checklists).
- No ejecutes /speckit-implement, no hagas push ni despliegues en GCP.

# Entregable final
Un resumen con:
1. Los archivos creados en .claude/, .specify/memory/ y specs/.
2. Las decisiones de clarify de cada spec.
3. Los conflictos detectados que el README no resolvía y cómo se resolvieron.
4. Los hallazgos de /speckit-analyze y cómo se corrigieron.
5. El número de tareas por historia y el orden de implementación (Setup, H-1…H-7, H-9 y H-8).
6. Cómo quedaron cubiertos los requisitos de la sección «Integración».
7. Los supuestos pendientes de validar con Tomasseli (README, Anexo A) y los recortes pendientes del docente.
8. Los prerrequisitos para el Prompt 2:
   - Docker, Ollama con qwen2.5:3b y bge-m3, y uv;
   - la key de Gemini, solo para la evaluación final;
   - insumos/base_conocimiento/ validada;
   - el historial de pedidos, sintético o real.
```
