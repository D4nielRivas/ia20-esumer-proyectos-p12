 # Proyecto 12 · Del chat a la comanda

**IA20 · ESUMER · FICHA DE ESPECIFICACIÓN DEL PROYECTO**

**Panadería Tomasseli · Alimentos y restaurantes**

| Dificultad | Solución | Base de datos | Orquestación |
|---|---|---|---|
| ★★★ | Chatbot de menú y pedidos (LLM + reglas) | PostgreSQL en GCP | n8n, etapas posteriores |

---

## Ficha técnica

| Campo | Detalle |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **Solución** | Chatbot que ofrece al usuario el menú del día disponible, toma el pedido y lo registra en una base de datos de pedidos, desde la cual la cocina lo consulta directamente (la «comanda» se emplea directamente desde `pedidos`, sin generación adicional) |
| **IA** | IA generativa (LLM de un proveedor aprobado) para conversación y extracción del pedido; reglas determinísticas para validar y registrar |
| **Machine Learning** | No aplica en este alcance |
| **Horario de servicio** | Fijo, de lunes a domingo, de 11:30 a 15:30 |
| **Modalidad del pedido** | Solo recogida del pedido en el sitio: para llevar o para consumir en el sitio. No hay domicilios |
| **Selección del menú del día** | Una sola opción por categoría (una categoría puede presentar varias opciones) |
| **Información hacia cocina** | Unidireccional: los reportes quedan en `pedidos` y `alertas`, y es responsabilidad de la cocina revisar estas fuentes |
| **Servicio del chatbot** | Servicio propio en GCP (sin n8n) que recibe los mensajes de WhatsApp Business API, consulta el menú, invoca el LLM, valida y escribe en `pedidos` |
| **Resumen diario** | Se consulta en la vista `v_resumen_diario`; el envío por Gmail queda para una fase posterior |
| **Orquestación** | n8n, como único orquestador en etapas posteriores |
| **Canales y sistemas** | WhatsApp Business API (solo órdenes de clientes) · Servicio propio del chatbot · PostgreSQL en GCP · Forms · Visualización de `pedidos` para cocina |
| **Carpeta de trabajo del equipo** | `ia20-esumer-proyecto-p12` |

> **Origen y alcance.** Esta ficha parte de la especificación funcional y técnica v1.2 de Panadería Tomasseli (18 Oct 2026). A diferencia de las fichas 1 a 11, no trae cifras de línea base: medirlas es una tarea de H1, y las metas de la sección 1.7 se recalibran con esa línea base y el piloto. Por decisión de la especificación, la ficha no incluye contenido económico. El proyecto se concentra en un chatbot que presenta las opciones del menú del día, captura el pedido y lo lleva a una base de datos de pedidos, desde la cual la cocina lo consulta directamente.

### Límites del alcance

- La cocina consulta directamente una visualización de `pedidos` y revisa `alertas`; no hay generación adicional de comanda.
- La información es unidireccional: en `pedidos` y `alertas` quedan los reportes y es responsabilidad de la cocina revisar estas fuentes.
- No se incluye validar la gestión que realiza la cocina del pedido (preparación, avance o entrega).
- El servicio es fijo de lunes a domingo, de 11:30 a 15:30, y solo con recogida en el sitio (para llevar o para consumir en el sitio); no hay domicilios.
- El chatbot opera en WhatsApp mediante un servicio propio (sin n8n); el resumen diario se consulta en `v_resumen_diario` y su envío por Gmail queda para una fase posterior.

## Contenido

1. **Necesidades:** contexto, problema, actores, requisitos funcionales y no funcionales, restricciones e indicadores de éxito.
2. **Entendimiento:** proceso actual y propuesto, causas raíz, papel de la IA, ficha «¿sí requiere ML?», supuestos y riesgos.
3. **Estructuración:** arquitectura funcional, modelo de datos, reglas de negocio, diseño del chatbot, flujo de operación, prompts y seguridad.
4. **Implementación:** herramientas, plan por hitos, plan de pruebas, guion del Demo Day, plan B y criterios de salida.
5. **Anexo A** · Decisiones pendientes de validación.
6. **Anexo B** · Marco común del curso: calendario de hitos, entrega en el repositorio y principios.

---

## 1. Necesidades

### 1.1 Contexto

Panadería Tomasseli recibe pedidos por WhatsApp y debe coordinarlos con la disponibilidad del menú (almuerzos diarios). WhatsApp se usa solo para las órdenes de los clientes, que llegan a la base de datos de pedidos a través de un servicio propio del chatbot. El servicio es fijo, de lunes a domingo de 11:30 a 15:30, y los pedidos son solo de recogida en el sitio, para llevar o para consumir allí; no hay domicilios.

La solución es un chatbot que atiende al cliente, le presenta las opciones disponibles del menú del día, toma su pedido y lo registra en una base de datos de pedidos organizada en PostgreSQL, dentro de GCP como nube. La cocina consulta directamente la visualización de `pedidos` y revisa `alertas`; no hay generación adicional de comanda. La IA generativa facilita la conversación, pero las reglas determinísticas controlan la disponibilidad, la confirmación y el registro.

### 1.2 Problema

La actualización manual y la circulación de la información por canales separados causan:

| Síntoma | Línea base |
|---|---|
| Respuestas al cliente con opciones agotadas | Por medir en H1 |
| Reprocesos al transcribir pedidos | Por medir en H1 |
| Demoras en la información que llega a cocina | Por medir en H1 |
| Diferencias entre lo solicitado y lo registrado | Por medir en H1 |

### 1.3 Actores y necesidades

| Actor | Necesita | Canal y contexto |
|---|---|---|
| **Cliente** | Consultar el menú del día y la disponibilidad vigente, resolver dudas, elegir una opción por categoría, indicar si recoge para llevar o para consumir en el sitio y la hora de recogida, y recibir una confirmación clara | WhatsApp |
| **Administración** | Mantener el menú del día, los horarios y la disponibilidad; consultar pedidos, alertas y cierres; revisar excepciones; consultar el resumen diario | Forms y vistas de consulta sobre PostgreSQL |
| **Cocina** | Consultar directamente los pedidos confirmados y las alertas; reportar agotados y cambios de menú | Visualización de `pedidos` y consulta de `alertas`; Forms |
| **Atención / operador** | Consultar el historial y hacerse cargo de conversaciones ambiguas, cambios especiales o incidencias | Vista operativa de pedidos y conversaciones |
| **Integraciones** | Mantener la consistencia entre WhatsApp Business API y la base de datos de pedidos, con trazabilidad | Sin interfaz propia |

### 1.4 Requisitos funcionales

| Código | Requisito |
|---|---|
| **RF1** | Publicar una fuente de verdad para el menú del día (almuerzos), organizado por categorías con una o varias opciones cada una, y la disponibilidad por opción. |
| **RF2** | Permitir que administración y cocina actualicen el menú y la disponibilidad con un Google Form validado, sin editar directamente las tablas operativas. |
| **RF3** | Consultar el menú activo y la disponibilidad antes de ofrecer, aceptar o confirmar una opción. |
| **RF4** | Atender conversaciones en WhatsApp Business API: presentar las opciones disponibles del menú del día por categoría, comprender la intención, resolver consultas y capturar el pedido de forma estructurada. WhatsApp solo canaliza las órdenes de los clientes. |
| **RF5** | Pedir los datos faltantes (opciones del menú —una por categoría—, cantidades, nombre, modalidad de recogida, hora de recogida y observaciones) antes de confirmar. |
| **RF6** | Registrar cada pedido confirmado una sola vez en la base de datos de pedidos, con identificador, fecha, canal y estado. |
| **RF7** | Poner a disposición de cocina los pedidos confirmados mediante una visualización directa de `pedidos`, sin generar una comanda adicional ni usar un canal de mensajería. Los agotados y cambios de menú se reportan por Google Forms. La información es unidireccional: cocina consulta `pedidos` y `alertas` y es responsable de revisarlos. |
| **RF8** | Permitir la intervención humana, la pausa del bot y el seguimiento de la conversación sin perder contexto ni duplicar pedidos. |
| **RF9** | Mantener una bitácora de cambios de menú, transiciones de pedido y errores. |
| **RF10** | Consolidar cada día pedidos, estados e incidencias en un resumen diario que administración consulta en la vista `v_resumen_diario`. El envío por Gmail queda para una fase posterior. |
| **RF11** | Validar con el cliente, antes de confirmar: que el pedido es de recogida en el sitio (no hay domicilios); si es para llevar o para consumir en el sitio; que la hora de recogida está dentro del horario fijo (lunes a domingo, de 11:30 a 15:30); y que solo se selecciona una opción por categoría del menú del día. |

### 1.5 Requisitos no funcionales

| Código | Requisito |
|---|---|
| **RNF1** | Respuesta automática en 10 segundos o menos en condiciones normales; si el LLM o la base de datos no responden dentro del umbral, se informa al usuario y se deriva a atención humana. |
| **RNF2** | Disponibilidad objetivo del 99 % mensual del servicio propio del chatbot y de la base de datos en GCP, sin contar la indisponibilidad de proveedores externos (WhatsApp Business API y LLM); ante una caída aplica el plan B (atención humana y formulario alterno). |
| **RNF3** | Sin duplicados: identificador único por pedido garantizado por PostgreSQL (R5); un pedido repetido no genera doble registro. Los reintentos automáticos con espera incremental y la cola de errores quedan para la etapa con n8n. |
| **RNF4** | Mínimo privilegio, cuentas institucionales, credenciales en un gestor seguro y registro de cambios. |
| **RNF5** | Proteger los datos personales (Ley 1581): guardar solo lo necesario para gestionar el pedido y aplicar la política de conservación aprobada. |
| **RNF6** | Trazabilidad del estado del pedido en el registro: recibido, validado, confirmado, cancelado o con error. El avance posterior en cocina no se registra ni se valida en este alcance. |
| **RNF7** | Formularios usables desde el móvil, computador o tablet. |
| **RNF8** | Los cambios de menú se reflejan en las respuestas del bot en 1 minuto o menos. |

### 1.6 Restricciones

- PostgreSQL es el repositorio operativo; Google Forms, el mecanismo de carga; el resumen diario se consulta en `v_resumen_diario` y su envío por Gmail queda para una fase posterior.
- WhatsApp Business API es el canal con los clientes, solo para sus órdenes; no se usa para hablar con cocina.
- El chatbot atiende WhatsApp mediante un servicio propio en GCP, sin n8n; los reintentos y las colas automáticas quedan para una etapa posterior.
- La cocina consulta directamente la visualización de `pedidos` y revisa `alertas`; no hay comanda adicional, y la información es unidireccional. La gestión que realiza la cocina del pedido no se valida en este alcance.
- El servicio es fijo, de lunes a domingo de 11:30 a 15:30. Solo hay recogida del pedido en el sitio (para llevar o para consumir en el sitio); no hay domicilios.
- Loyverse TPV no se integra en esta fase del proyecto: la integración depende de permisos y de la capacidad de su API, y no es necesaria para que cocina consulte `pedidos`.
- n8n sería el único orquestador, para una etapa posterior.

### 1.7 Indicadores de éxito

| Indicador | Línea base | Meta | Cómo se mide |
|---|---|---|---|
| **Tiempo de respuesta** | Por medir | ≥ 90 % de las consultas automatizables respondidas en ≤ 10 s | Marcas de tiempo en `bitacora` |
| **Exactitud del pedido** | Por medir | ≥ 98 % de los pedidos confirmados sin corrección manual atribuible a la captura | Pedidos corregidos frente a confirmados |
| **Disponibilidad del menú** | Por medir | 100 % de los pedidos aceptados vinculados a una opción activa y disponible al confirmar | `disponibilidad_validada_en` en `detalle_pedido` |
| **Validaciones con el cliente** | Por medir | 100 % de los pedidos confirmados con modalidad de recogida, hora dentro del horario (11:30 a 15:30) y una sola opción por categoría | `modalidad`, `hora_recogida` en `pedidos` y `categoria` en `detalle_pedido` |
| **Registro en la base de datos** | Por medir | 100 % de los pedidos confirmados registrados una sola vez (sin duplicados) | `pedido_id` único en `pedidos` |
| **Cierre diario** | Por medir | Resumen diario de pedidos disponible para administración en cada jornada | Consulta de `v_resumen_diario` al cierre de la jornada |

> Las metas son criterios iniciales de aceptación y se recalibran con la línea base de H1 y el piloto.

---

## 2. Entendimiento

### 2.1 AS-IS

1. El cliente pregunta por WhatsApp o pide un producto.
2. El equipo consulta el menú y la disponibilidad en información dispersa o de memoria. ❌ *Aquí se ofrecen opciones agotadas.*
3. El pedido se interpreta y se transcribe a mano para cocina. ❌ *Aquí nacen los reprocesos y las diferencias.*
4. Cocina prepara; los cambios y agotados no siempre se comunican a tiempo. ❌ *Aquí se generan las demoras.*
5. La venta, la entrega y el cierre se registran en sistemas separados y se concilian al final del día.

### 2.2 Causas raíz

| Causa raíz | Cómo se aborda |
|---|---|
| Menú y existencias sin una fuente única | Se centralizan menú y disponibilidad, con un responsable de actualización |
| Transcripción manual entre conversación y cocina | Una entidad Pedido en la base de datos; cocina la consulta directamente en `pedidos`, sin retranscribir |
| Lenguaje libre y variable del cliente | Extracción asistida por LLM, seguida de validación estructurada |
| Cambios que no se comunican en tiempo real | El Form de cambio actualiza el menú y el bot responde con la versión vigente; los cambios y cancelaciones de pedidos quedan en `pedidos` y `alertas` |
| Falta de conciliación diaria | Reporte consolidado y alertas |

### 2.3 TO-BE

Administración publica el menú del día, y cocina reporta la disponibilidad y los agotados, ambos mediante Forms que actualizan PostgreSQL → el cliente escribe por WhatsApp → el servicio propio del chatbot consulta el menú vigente, presenta las opciones por categoría y el LLM clasifica la intención y extrae el pedido → la validación contrasta datos, opciones, disponibilidad, una opción por categoría, modalidad de recogida (para llevar o consumo en el sitio) y hora de recogida dentro del horario → el cliente acepta el resumen → el pedido se registra una sola vez como «confirmado» en la base de datos de pedidos → cocina consulta directamente la visualización de `pedidos` y revisa `alertas`, que son sus únicas fuentes de información → administración consulta el resumen diario en `v_resumen_diario`.

### 2.4 ¿Dónde aporta la IA?

| Tarea | Quién | Por qué / límite |
|---|---|---|
| Clasificar el mensaje (consulta, pedido, cambio, cancelación, solicitud humana) y extraer opciones, cantidades y notas | IA generativa (LLM) | El lenguaje del cliente es libre. Salida en JSON validado |
| Presentar las opciones del menú del día por categoría y redactar la respuesta natural | IA generativa (LLM) | Solo con datos del menú activo, reglas aprobadas y disponibilidad consultada |
| Detectar campos ausentes o ambiguos y preguntar (incluida la modalidad y la hora de recogida) | IA generativa (LLM) | Sin inferir cantidades, modalidad, hora ni sustituciones |
| Presentar el resumen del pedido para confirmar | IA generativa (LLM) | Sobre datos ya validados |
| Validar disponibilidad, esquema, opciones, una opción por categoría, modalidad, horario, cantidades y estado | Reglas (sin IA) | Controles exactos: consultas al catálogo y restricciones de PostgreSQL |
| Registrar el pedido y consolidar el resumen diario | Servicio propio del chatbot, reglas y PostgreSQL | Identificador único para evitar duplicados; el resumen se consulta en una vista de la base de datos |
| Consultar los pedidos confirmados y las alertas | Cocina | Información unidireccional; la revisión es responsabilidad de cocina y su gestión no se valida en este alcance |
| Atender casos ambiguos, cambios especiales e incidencias | Operador | La IA deriva cuando falta información o hay ambigüedad |

> **Límite de autoridad.** El LLM no modifica el inventario, no escribe en la base de datos por su cuenta, no confirma disponibilidad «de memoria» ni ejecuta acciones fuera del contexto autorizado. Solo propone; la validación y el registro los controlan las reglas y el operador.

### 2.5 Ficha «¿sí requiere ML?»

Se define que no se utiliza ML en esta etapa del proyecto.

### 2.6 Supuestos y riesgos

**Supuestos por validar en H1:** catálogo del menú del día con ID y categorías; horario fijo de lunes a domingo de 11:30 a 15:30; recogida solo en el sitio (sin domicilios); medios de pago, política de cancelación y responsables de cada bandeja; alojamiento y administración de PostgreSQL en GCP; mecanismo con el que los Forms actualizan la base de datos; servicio propio del chatbot (alojamiento en GCP y acceso a WhatsApp Business API); forma de la visualización de `pedidos` para cocina (vista, panel o consulta); volumen simultáneo; cuentas y accesos.

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Menú desactualizado | Se promete un producto agotado | Form con vigencia y responsable, expiración y consulta del menú antes de confirmar |
| Escritura del pedido con errores u omisiones | Pedido sin registro o mal transcrito | Resumen aceptado por el cliente como fuente, revisión del operador y restricciones en PostgreSQL |
| Pedido registrado dos veces | Doble registro o doble preparación | Clave primaria y restricción de unicidad por `pedido_id`; verificación antes de registrar |
| Pedido con más de una opción por categoría, sin modalidad o fuera del horario | Pedido inconsistente | Validaciones del bot y del registro antes de confirmar (R8, R11 y R12) |
| El LLM inventa o malinterpreta | Pedido incorrecto | Contexto acotado, esquema validado, confirmación explícita y derivación a humano |
| Permisos y datos personales | Exposición o cambio no autorizado | Roles de PostgreSQL con mínimo privilegio, retención definida y bitácora (Ley 1581) |
| Caída del servidor PostgreSQL | El bot no puede verificar disponibilidad ni registrar pedidos | Respaldos, no confirmar sin consulta vigente y contingencia manual |
| WhatsApp Business API o servicio propio del chatbot no disponibles | Pedidos no recibidos | Canal alterno aprobado (teléfono o atención directa), atención humana y formulario alterno de captura |
| Forms mal diligenciados o sin acceso | Menú desactualizado | Campos obligatorios y validados, responsable por Form y revisión diaria |
| Cocina no consulta `pedidos` ni `alertas` | Pedido sin preparar | Es responsabilidad de cocina revisar estas fuentes; no hay otro canal y la gestión de cocina no se valida en este alcance; se deja constancia en el manual operativo |

---

## 3. Estructuración

### 3.1 Arquitectura funcional

| Componente | En este proyecto |
|---|---|
| **Datos** | PostgreSQL: `menu_del_dia`, `pedidos`, `detalle_pedido`, `alertas` y `bitacora` |
| **Servicio del chatbot** | Servicio propio en GCP, sin n8n: recibe los mensajes de WhatsApp Business API, consulta el menú, invoca el LLM, valida y escribe en `pedidos` y `detalle_pedido` |
| **Vistas** | `v_pedidos_operativa` (visualización de `pedidos` para cocina y operador, empleada directamente, sin comanda adicional) y `v_resumen_diario` (resumen diario) |
| **Interfaz** | Chatbot en WhatsApp para el cliente; Forms de alta, cambio y agotado para administración y cocina; visualización de `pedidos` y consulta de `alertas` para cocina y operador; consulta de `v_resumen_diario` para administración |
| **Reglas** | R1 a R13: vigencia y disponibilidad, datos mínimos, identificador único, recogida en el sitio, horario fijo, una opción por categoría e información unidireccional |
| **Orquestación** | No se aborda en esta fase (n8n queda para una fase posterior) |

```text
Cliente -> WhatsApp Business API
 -> Servicio propio del chatbot (GCP)
 -> consulta de menú del día y disponibilidad (PostgreSQL)
 -> LLM con contexto acotado y salida JSON
 -> validación contra catálogo y confirmación del cliente
 -> Base de datos de pedidos (pedidos + detalle_pedido en PostgreSQL)
 -> Resumen diario (v_resumen_diario)

Cocina -> consulta directa de la visualización de pedidos (v_pedidos_operativa) y de alertas (unidireccional)

Administración -> consulta de v_resumen_diario (el envío por Gmail queda para una fase posterior)

Administración / Cocina -> Forms -> validación -> PostgreSQL -> menú y disponibilidad vigentes para el bot
```

### 3.2 Modelo de datos

| Tabla | Campos principales |
|---|---|
| `menu_del_dia` | `menu_id`, `fecha`, `categoria`, `nombre`, `componentes`, `descripcion`, `cupo`, `disponible`, `hora_corte`, `alergenos_declarados`, `responsable`, `vigencia` (una fila por opción y fecha; una categoría puede tener varias opciones) |
| `pedidos` | `pedido_id`, `fecha_hora`, `telefono_normalizado`, `nombre`, `canal`, `modalidad` (para llevar o consumo en el sitio), `hora_recogida`, `estado`, `notas`, `aviso_privacidad`, `ultima_actualizacion` |
| `detalle_pedido` | `pedido_id`, `linea`, `menu_id`, `categoria`, `nombre_snapshot`, `cantidad`, `notas_linea`, `disponibilidad_validada_en` |
| `alertas` | `alerta_id`, `tipo`, `severidad`, `pedido_id`, `origen`, `mensaje`, `creada_en`, `estado`, `responsable`, `resuelta_en` |
| `bitacora` | `evento_id`, `entidad`, `entidad_id`, `accion`, `actor`, `timestamp`, `resultado`, `detalle` (sin secretos) |

**Restricciones e integridad (propuesta a validar en H2):**

| Tipo | Aplicación |
|---|---|
| **Claves primarias** | `menu_id`, `pedido_id`, (`pedido_id`, `linea`), `alerta_id`, `evento_id` |
| **Claves foráneas** | `detalle_pedido.pedido_id` → `pedidos`; `detalle_pedido.menu_id` → `menu_del_dia`; `alertas.pedido_id` → `pedidos` |
| **Unicidad** | `pedido_id` en `pedidos`; combinación `fecha` + `categoria` + `nombre` en `menu_del_dia` |
| **Validaciones (CHECK)** | `cantidad > 0`; `cupo >= 0`; `modalidad` limitada a para llevar o consumo en el sitio; `hora_recogida` entre 11:30 y 15:30 |
| **Dominios de estado** | `estado` con los valores de RNF6 (recibido, validado, confirmado, cancelado o con error) |

La regla de una sola opción por categoría se valida antes de registrar el pedido (R12), con base en `categoria` en `detalle_pedido`.

Los roles de PostgreSQL separan los permisos por perfil (chatbot, formularios, cocina en solo lectura, operador y administración), y las credenciales se guardan fuera de la base de datos. Si la concurrencia o el volumen aumentan, se revisa el dimensionamiento del servidor y de las conexiones.

### 3.3 Reglas de negocio

| Código | Regla | Dónde se implementa |
|---|---|---|
| **R1** | Solo se ofrecen opciones activas, vigentes y disponibles del menú del día para la fecha; la disponibilidad se verifica al iniciar y al confirmar | Consulta del bot a `menu_del_dia` |
| **R2** | Una opción con disponibilidad desconocida no es confirmable: se pregunta al operador | Derivación a humano |
| **R3** | El pedido pasa a «confirmado» solo con datos mínimos (opciones, cantidades, nombre, modalidad y hora de recogida), disponibilidad validada y resumen aceptado por el cliente | Validación contra catálogo y esquema |
| **R4** | Cantidades positivas; opciones, sustituciones y horarios se rigen por el catálogo y son fijos | Restricciones CHECK y claves foráneas en PostgreSQL |
| **R5** | Cada pedido lleva un identificador único; un pedido repetido no genera doble registro | Clave primaria y unicidad de `pedido_id` |
| **R6** | Cancelaciones y cambios conservan el historial; la actualización queda reflejada en `pedidos` y se crea una alerta en `alertas`, que cocina revisa | `bitacora`, `pedidos` y `alertas` |
| **R7** | Toda operación fallida queda en `alertas` con responsable y acción pendiente | Tabla `alertas` |
| **R8** | Todo pedido es de recogida en el sitio; no hay domicilios. El chatbot pregunta y valida con el cliente si es para llevar o para consumir en el sitio antes de confirmar | Validación de esquema y CHECK de `modalidad` |
| **R9** | Los menús con vigencia vencida dejan de ser elegibles | Vigencias y expiración en las consultas |
| **R10** | El chatbot solo canaliza las órdenes de los clientes; cocina consulta los pedidos directamente desde `pedidos` | Diseño del flujo |
| **R11** | El servicio es fijo, de lunes a domingo de 11:30 a 15:30; la hora de recogida solicitada debe estar dentro de ese horario | Validación de esquema y CHECK de `hora_recogida` |
| **R12** | En el menú del día solo se puede seleccionar una opción por categoría; una categoría puede presentar varias opciones | Validación del bot y verificación antes de registrar el pedido |
| **R13** | La información hacia cocina es unidireccional: los reportes quedan en `pedidos` y `alertas`; cocina es responsable de revisarlos y su gestión del pedido no se valida en este alcance | Diseño del flujo |

### 3.4 Diseño del chatbot

| Elemento | Decisión |
|---|---|
| **Objetivo** | Ofrecer opciones del menú del día disponible, tomar el pedido de forma estructurada (una opción por categoría, modalidad de recogida y hora) y registrarlo en `pedidos`, desde donde cocina lo consulta directamente |
| **Motor** | LLM de un proveedor aprobado; no se entrena un modelo propio |
| **Canal** | WhatsApp Business API (solo órdenes de clientes), atendido por un servicio propio del chatbot en GCP, sin n8n |
| **Contexto** | Menú del día por categoría, disponibilidad, horario fijo y reglas, consultados en PostgreSQL con campos mínimos y marca de tiempo |
| **Salida** | El LLM solo propone un JSON (P2); se validan tipos, opciones elegibles, cantidades, una opción por categoría, modalidad, hora de recogida, privacidad y estado |
| **Confirmación** | El cliente acepta explícitamente el resumen, que incluye la modalidad (para llevar o consumo en el sitio) y la hora de recogida; solo entonces se registra el pedido |
| **Trazabilidad** | Se registra la versión del prompt y del modelo, y se minimiza la conservación del texto conversacional |
| **Alternativa ante fallas** | Si el LLM falla, atención humana con un formulario alterno de captura |

### 3.5 Flujo de operación de esta fase

Sin orquestador, el flujo se ejecuta con el servicio propio del chatbot, PostgreSQL, los Forms y el apoyo del operador:

**A · Actualización de menú y disponibilidad.** Administración o cocina envían el Form de alta, cambio o agotado → validación de campos, fecha, ID y responsable → actualización de las filas vigentes de `menu_del_dia` → registro en `bitacora` → el bot responde con la versión vigente (≤ 1 minuto, RNF8).

**B · Conversación y pedido.** El cliente escribe por WhatsApp → el servicio propio del chatbot recibe el mensaje y consulta el menú del día y la disponibilidad en PostgreSQL → paso de IA (P1 + P2): clasifica la intención, presenta las opciones por categoría y extrae el pedido en JSON → validación de esquema, opciones, disponibilidad, una opción por categoría y horario (11:30 a 15:30) → si faltan datos (incluidas la modalidad, para llevar o consumo en el sitio, y la hora de recogida), el bot los pregunta; si el cliente pide domicilio, el bot informa que solo hay recogida en el sitio; si hay ambigüedad o solicitud humana, se deriva al operador → al confirmar, se revalida la disponibilidad y se muestra el resumen → tras la aceptación explícita del cliente, el pedido se registra en `pedidos` y `detalle_pedido` con `pedido_id` único.

**C · Consulta de cocina.** Pedido confirmado o cambiado → queda en `pedidos` (ID, hora de recogida, modalidad, líneas y notas) → cocina lo consulta directamente en la visualización de `pedidos` (`v_pedidos_operativa`) y revisa `alertas`. No se genera una comanda adicional y no se valida la gestión que cocina realice del pedido.

**D · Resumen diario.** Al cierre de la jornada, administración revisa `v_resumen_diario`: pedidos por estado, modalidad y canal, con pendientes e incidencias. El envío por Gmail queda para una fase posterior.

**Punto de control humano.** El operador atiende toda derivación del flujo B y revisa el registro de pedidos.

### 3.6 Prompts clave

#### P1 · Instrucción de sistema

```text
Eres el asistente de pedidos de Panadería Tomasseli. Responde en español, con tono
cordial y conciso. Presenta al cliente las opciones del menú del día que estén
disponibles, organizadas por categoría, y recuérdale que solo puede elegir una opción
por categoría. El servicio es de lunes a domingo, de 11:30 a 15:30, y solo con
recogida en el sitio: no hay domicilios. Pregunta siempre si el pedido es para llevar
o para consumir en el sitio, y la hora de recogida dentro del horario. Usa únicamente
el menú, disponibilidad, horarios y reglas recibidos como contexto en esta
conversación. No inventes productos, existencias, tiempos ni condiciones. No confirmes
una orden hasta que la validación indique disponible y el cliente acepte el resumen.
Si la información falta, está vencida o es ambigua, pregunta o deriva a una persona.
No solicites datos que no sean necesarios para gestionar el pedido.
```

#### P2 · Salida estructurada (el LLM propone; la validación decide)

```json
{
  "intent": "consulta | pedido | cambio | cancelacion | solicitud_humana",
  "items": [
    { "menu_id": "string", "category": "string", "quantity": "integer > 0", "notes": "string" }
  ],
  "customer_name": "string",
  "service_mode": "para_llevar | consumo_en_sitio",
  "requested_time": "string (hora de recogida entre 11:30 y 15:30)",
  "missing_fields": ["string"],
  "needs_human": "boolean",
  "response": "string"
}
```

### 3.7 Seguridad, privacidad y operación

- Roles de PostgreSQL por perfil con mínimo privilegio: el chatbot solo lee el menú del día y escribe pedidos; los Forms solo modifican los datos que les corresponden; cocina, administración y operador consultan por vistas (cocina en solo lectura).
- Cuentas institucionales con propietario organizacional y acceso restringido a la base de datos.
- Llaves de API, tokens de WhatsApp Business API y credenciales fuera de tablas, prompts y conversaciones.
- Datos del cliente limitados a lo necesario; el teléfono completo no aparece en la visualización de `pedidos` para cocina salvo necesidad aprobada.
- Aviso de privacidad, finalidad, retención y atención de solicitudes definidos con un responsable de Tomasseli antes del piloto (Ley 1581).
- Registro de accesos y cambios, y copias de respaldo de la base de datos.

---

## 4. Implementación

### 4.1 Herramientas

LLM; Gamma o Canva y v0.dev para la presentación y el prototipo; WhatsApp Business API (o su entorno de prueba); servicio propio del chatbot en GCP; PostgreSQL como base de datos; Forms para las actualizaciones de administración y cocina; visualización de `pedidos` para cocina; repositorio con prompts, scripts SQL, configuración y registro de cambios.

### 4.2 Plan por hitos

| Hito | Tareas | Entregable |
|---|---|---|
| **H1** | AS-IS y TO-BE validados con Tomasseli; horario fijo (lunes a domingo, 11:30 a 15:30), recogida en el sitio (para llevar o consumo en el sitio) y cortes; menú del día por categorías y responsables; medición de la línea base; inventario de accesos; definición del alojamiento de PostgreSQL, del mecanismo con que los Forms actualizan la base de datos, del servicio propio del chatbot y de la visualización de `pedidos` para cocina; P1 v1 | Documento de descubrimiento y biblioteca de prompts |
| **H2** | Diccionario de datos y esquema de PostgreSQL (tablas, restricciones y vistas); reglas R1–R13 trazables a los requisitos; esquema P2 probado con 10 mensajes reales o simulados, verificando cada opción contra el menú | Documento base + tabla de verificación |
| **H3** | Presentación ejecutiva; prototipo del chatbot en WhatsApp (o su entorno de prueba) y de la visualización de `pedidos` para cocina; MVP: base de datos PostgreSQL con restricciones y vistas, y Forms de menú del día y agotados; pruebas P-01 a P-14 | PDF, `index.html`, script SQL del esquema, capturas y registro de pruebas |
| **H4** | *No aplica en este alcance (sin modelo de ML).* | — |
| **H5** | *No se aborda en esta fase (flujo automatizado con n8n e integración con Loyverse TPV).* | — |
| **H6** | Piloto del MVP, capacitación por rol, manual operativo y guion | Demo y acta de habilitación |

### 4.3 Plan de pruebas

| # | Caso | Resultado esperado |
|---|---|---|
| **P-01** | Alta o edición de menú por Form | Campos validados, cambio auditado en `bitacora` y visible al bot en ≤ 1 minuto |
| **P-02** | Consulta del menú del día | El bot muestra solo opciones vigentes y disponibles, organizadas por categoría |
| **P-03** | Opción agotada reportada por Form de cocina | El agotado no se confirma y se ofrecen alternativas de la misma categoría |
| **P-04** | Pedido completo y claro | Resumen con modalidad y hora de recogida, aceptación, un registro en `pedidos` y `detalle_pedido`, pedido visible para cocina directamente en `pedidos`, ningún mensaje a cocina por el chatbot y respuesta dentro del objetivo |
| **P-05** | Pedido incompleto o ambiguo | Pregunta solo los campos faltantes; no confirma antes de la aceptación |
| **P-06** | El cliente elige dos opciones de una misma categoría | El bot pide elegir una sola opción por categoría; no confirma con más de una |
| **P-07** | Pedido sin modalidad o con solicitud de domicilio | El bot pregunta si es para llevar o para consumir en el sitio; ante un domicilio, informa que solo hay recogida en el sitio |
| **P-08** | Hora de recogida fuera de 11:30 a 15:30 | No se acepta la hora; el bot propone una dentro del horario |
| **P-09** | Pedido repetido (mismo identificador) | La restricción de unicidad impide el duplicado; queda un registro y el intento queda reconocido |
| **P-10** | Falla de WhatsApp, del servicio del chatbot, del LLM o de la base de datos | Mensaje de espera o derivación al operador y formulario alterno; nunca una confirmación falsa |
| **P-11** | Cambio o cancelación después de confirmar | Historial conservado, `pedidos` actualizado y alerta en `alertas` visible para cocina |
| **P-12** | Resumen diario | `v_resumen_diario` trae totales por estado y canal, pendientes e incidencias |
| **P-13** | Permisos y seguridad | Roles no autorizados no cambian el menú; cocina solo lee `pedidos` y `alertas`; los secretos no aparecen en tablas, prompts ni conversaciones |
| **P-14** | Tiempo de respuesta | Objetivo de 10 s medido en las pruebas del piloto |

### 4.4 Guion del Demo Day

1. El problema: opciones agotadas, transcripciones y diferencias, con la línea base medida en H1.
2. En vivo: cocina marca un agotado por Form → el bot deja de ofrecerlo en menos de un minuto.
3. En vivo: el cliente pide por WhatsApp; el bot presenta el menú del día por categorías; el cliente intenta elegir dos opciones de una misma categoría → el bot pide elegir una; falta la modalidad → pregunta si es para llevar o para consumir en el sitio → resumen → confirmación → registro en PostgreSQL → cocina lo ve directamente en `pedidos`.
4. Un pedido repetido → un solo registro; una solicitud de domicilio → el bot informa que solo hay recogida en el sitio.
5. El resumen diario desde la base de datos.
6. Los límites de la IA: qué propone, qué valida el catálogo y qué decide la persona.

### 4.5 Plan B

| Evento | Acción |
|---|---|
| WhatsApp o su API fuera de servicio | Canal alterno aprobado (teléfono o atención directa); pedidos manuales con ID único y carga a PostgreSQL al restablecer |
| Servicio del chatbot o LLM fuera de servicio | Atención humana y formulario alterno de captura con ID único; registro en PostgreSQL al restablecer |
| PostgreSQL inaccesible o datos vencidos | Pausar confirmaciones automáticas; restaurar o consultar el último respaldo; validar existencias a mano |
| Un Form no actualiza la base de datos | Registro manual del cambio por el responsable y revisión de `bitacora`; avisar al operador para que el bot ofrezca la versión correcta |
| La visualización de `pedidos` no está disponible | Restablecer la visualización o consultar `pedidos` con el rol de solo lectura; registrar la incidencia en `alertas` |
| Falla el registro del pedido | Registro manual por el operador con ID único y verificación de que el pedido aparezca en `pedidos` |

### 4.6 Criterios de salida y operación

La salida a piloto requiere: menú del día con ID y categorías aprobados; horario y reglas aprobados; esquema de PostgreSQL con restricciones y respaldos operativos; Forms de actualización probados; visualización de `pedidos` para cocina probada; responsabilidad de cocina de revisar `pedidos` y `alertas` comunicada y aceptada; responsables de excepciones; textos de privacidad; acceso protegido; procedimiento manual; y aceptación del piloto.

En operación, las alertas y los pedidos registrados se revisan a diario; la exactitud, los tiempos, la disponibilidad del menú y las causas de derivación, cada semana. Todo cambio de reglas, prompts, menú o esquema se registra, se valida y tiene reversión documentada.

### 4.7 Evolución prevista (fuera de esta fase)

Para fases posteriores quedan: automatización del flujo con n8n (reintentos con espera incremental, colas de errores, alertas automáticas y envío del resumen diario por Gmail) y la integración con Loyverse TPV. El esquema de PostgreSQL y las reglas de esta ficha se mantienen para facilitar esa evolución.

---

## Anexo A · Decisiones pendientes de validación

Hasta validarlas, los componentes descritos son diseño objetivo y toda herramienta externa queda sujeta a prueba técnica.

- Alojamiento y administración de PostgreSQL en GCP (servidor, versión, acceso, respaldos y retención).
- Mecanismo con el que cada Form (de administración y de cocina) escribe en PostgreSQL y herramienta de Forms a usar.
- Servicio propio del chatbot: tecnología y alojamiento en GCP, recepción de los mensajes de WhatsApp Business API, llamada al LLM, escritura del pedido en PostgreSQL y consulta del menú y la disponibilidad; responsable de operarlo. La carga manual por el operador queda solo como contingencia (plan B).
- Cuenta y acceso a WhatsApp Business API (o su entorno de prueba).
- Forma de la visualización de `pedidos` para cocina (vista, panel o consulta) y campos que muestra (ID, hora de recogida, modalidad, líneas, notas y alérgenos declarados).
- Categorías del menú del día y número de opciones por categoría; cómo se aplica la regla de una opción por categoría cuando un pedido incluye más de un menú.
- Si cada opción del menú del día tiene ID.
- Si las existencias se controlan por ingrediente, por opción o por conteo manual.
- Campos obligatorios del pedido (opciones, cantidades, nombre, modalidad y hora de recogida).
- Hora límite para tomar pedidos dentro del horario fijo (11:30 a 15:30), si aplica.
- Responsables y frecuencia de revisión del resumen diario.
- Política de cancelación.
- Conservación y acceso a los datos personales.

---

## Anexo B · Marco común del curso

Estas reglas aplican a todos los proyectos del curso. Se incluyen aquí para que la ficha se pueda leer sola.

### Calendario común de hitos

Este calendario aplica a todos los proyectos. La sección 4.2 *Plan por hitos* detalla qué significa cada hito en este proyecto. En esta fase, el hito H4 (Modelo de ML) no aplica y el hito H5 (Flujo con IA, con n8n) no se aborda.

| Hito | Semanas | Sesiones del plan (fecha) | Producto del plan que se aplica al proyecto |
|---|---|---|---|
| **H1 · Planteamiento** | 2–3 | MasterClass de nivelación (12 Sep) · Fundamentos de prompting (13 Sep) · Prompting avanzado (19 Sep) | Problema, usuario, tarea y resultado esperado · Biblioteca de prompts · Secuencia de prompts documentada |
| **H2 · Documento base** | 3–4 | Documentos, datos y contexto (20 Sep) · Generación estructurada (26 Sep) · MasterClass (27 Sep) | Resumen ejecutivo trazable · Reporte profesional y plantilla de prompt reutilizable |
| **H3 · Presentación, prototipo y MVP** | 5–8 | Presentaciones (3 Oct) · Prototipado (4 Oct) · Co-creación de código (10 Oct) · No-Code (11 Oct) · MasterClass (18 Oct) · Bootcamp (24–25 Oct) | Presentación ejecutiva · Prototipo web · Interacción funcional · Arquitectura funcional y MVP sin código |
| **H4 · Modelo de ML** | 7–10 | ML sin código (17 Oct) · Preparación de datos (31 Oct) · Entrenamiento (1 Nov) · Validación (7 Nov) · MasterClass (8 Nov) | *No aplica en este alcance* |
| **H5 · Flujo con IA** | 11–14 | Triggers y actions (14 Nov) · Integración y mapeo (15 Nov) · APIs y webhooks (21 Nov) · IA en un workflow (22 Nov) · Diseño robusto (28 Nov) · MasterClass (29 Nov) · Bootcamp (5–6 Dic) | *No se aborda en esta fase* |
| **H6 · Demo Day** | 15 | Semana de la Innovación (7–13 Dic) | Presentación final con demo en vivo |

### Entrega en el repositorio

Cada equipo trabaja en `bitacora/proyecto-<nombre-equipo>/` con esta estructura:

```text
bitacora/proyecto-<nombre-equipo>/
├── README.md              # Ficha del proyecto (este formato) + estado de cada hito
├── h1_planteamiento/      # Documento de descubrimiento, línea base y biblioteca de prompts
├── h2_documento_base/     # Diccionario de datos, esquema SQL, reglas, prompts usados y registro de verificación
├── h3_mvp/                # Presentación (PDF), prototipo (HTML), script SQL de PostgreSQL, capturas y pruebas del MVP
├── h4_modelo/             # No aplica en este alcance
├── h5_flujo/              # No se aborda en esta fase
└── h6_demo/               # Guion, presentación final y video de respaldo
```

> **Regla de oro** (la misma de los laboratorios): la IA propone, el equipo verifica y decide. Cada hito debe dejar registrado qué hizo la IA, qué revisó el equipo y qué se corrigió.

### Principios comunes

| Principio | Cómo aparece en este proyecto |
|---|---|
| **Primero el problema, después la herramienta** | La ficha empieza por necesidades; la línea base se mide antes de construir |
| **La IA propone, la persona decide** | El LLM propone un JSON que se valida contra el catálogo; el operador atiende las derivaciones |
| **Verificar lo que produce la IA** | Disponibilidad revalidada al confirmar y salidas en JSON con esquema |
| **Diseñar para el fallo** | Identificador único, alertas, respaldos, contingencia manual y plan B por cada componente |
| **Cuidar el dato** | Ley 1581, roles con mínimo privilegio y mínimo de datos personales |
