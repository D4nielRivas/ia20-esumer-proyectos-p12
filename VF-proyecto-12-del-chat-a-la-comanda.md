# Proyecto 12 · Del chat a la comanda

**IA20 · ESUMER · FICHA DE ESPECIFICACIÓN DEL PROYECTO**

**Panadería Tomasseli · Alimentos y restaurantes**

| Dificultad | Solución | Conexión modelo–flujo | Orquestación |
|---|---|---|---|
| ★★★ | Chatbot de menú y pedidos (LLM + reglas | Regla | n8n, etapas posteriores|

---

## Ficha técnica

| Campo | Detalle |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **Solución** | 	Chatbot que ofrece al usuario el menú del día disponible, toma el pedido y lo registra en una base de datos de pedidos, desde la cual se envía a la comanda de la panadería|
| **Conexión modelo–flujo** | Regla |
|**IA**|IA generativa (LLM de un proveedor aprobado) para conversación y extracción del pedido; reglas determinísticas para validar y registrar|
| **Orquestación** | n8n, como único orquestador en etapas posteriores |
| **Canales y sistemas** | WhatsApp Business API (solo órdenes de clientes) · Google Sheets y Forms · Gmail · Comanda de la panadería|
| **Carpeta de trabajo del equipo** | `ia20-esumer-proyecto-p12` |

> **Origen y alcance.** Esta ficha parte de la especificación funcional y técnica v1.2 de Panadería Tomasseli (18 Oct 2026). A diferencia de las fichas 1 a 11, no trae cifras de línea base: medirlas es una tarea de H1, y las metas de la sección 1.7 se recalibran con esa línea base y el piloto. Por decisión de la especificación, la ficha no incluye contenido económico. el proyecto se concentra en un chatbot que presenta opciones de menú y productos, captura el pedido y lo lleva a una base de datos de pedidos para su envío a la comanda.


## Contenido

1. **Necesidades:** contexto, problema, actores, requisitos funcionales y no funcionales, restricciones e indicadores de éxito.
2. **Entendimiento:** proceso actual y propuesto, causas raíz, papel de la IA, ficha «¿sí requiere ML?», supuestos y riesgos.
3. **Estructuración:** arquitectura funcional, modelo de datos, reglas de negocio, diseño del modelo de ML, flujo automatizado, prompts y seguridad.
4. **Implementación:** herramientas, plan por hitos, plan de pruebas, guion del Demo Day, plan B y criterios de salida.
5. **Anexo A** · Decisiones pendientes de validación.
6. **Anexo B** · Marco común del curso: calendario de hitos, entrega en el repositorio, conexión modelo–flujo y principios.

---

## 1. Necesidades

### 1.1 Contexto

Panadería Tomasseli recibe pedidos por WhatsApp y debe coordinarlos con la disponibilidad del menú (almuerzos diarios). WhatsApp se usa solo para las órdenes de los clientes que viajan directamente a la BD pedidos.

La solución es un chatbot que atiende al cliente, le presenta las opciones disponibles del menú del día, toma su pedido y lo registra en una base de datos de pedidos organizada en postgresql como base de datos y dentro de GCP como nube. La IA generativa facilita la conversación, pero las reglas determinísticas controlan la disponibilidad, la confirmación y el registro.

### 1.2 Problema

La actualización manual y la circulación de la información por canales separados causan:

| Síntoma | Línea base |
|---|---|
| Respuestas al cliente con opciones agotadas | Por medir en H1 |
| Reprocesos al transcribir pedidos | Por medir en H1 |
| Demoras en cocina | Por medir en H1 |
| Diferencias entre lo solicitado, lo preparado y lo registrado | Por medir en H1 |

### 1.3 Actores y necesidades

| Actor | Necesita | Canal y contexto |
|---|---|---|
| **Cliente** | Consultar el menú y la disponibilidad vigente, resolver dudas, especificar el pedido, la entrega o recogida, y recibir una confirmación clara | WhatsApp |
| **Administración** | Mantener catálogo, horarios, estados, pedidos y cierres; revisar excepciones; recibir un resumen diario; consultar la previsión de pedidos | Formulario de forms|
| **Atención / operador** | Consultar el historial y hacerse cargo de conversaciones ambiguas, cambios especiales o incidencias | Vista operativa de pedidos y conversaciones |
| **Integraciones** | Mantener la consistencia entre WhatsApp Business API y la base de datos de pedidos, con trazabilidad y reintentos|

### 1.4 Requisitos funcionales


| Código | Requisito |
|---|---|
| **RF1** | Publicar una fuente de verdad para el menú fijo de almuerzos y la disponibilidad por producto. |
| **RF2** | Permitir que administración y cocina actualicen el menú con un Google Form validado, sin editar directamente las celdas operativas. |
| **RF3** | Consultar el menú activo y la disponibilidad antes de ofrecer, aceptar o confirmar un producto. |
| **RF4** | Atender conversaciones en WhatsApp Business API: presentar las opciones disponibles del menú del día, comprender la intención, resolver consultas y capturar el pedido de forma estructurada. WhatsApp solo canaliza las órdenes de los clientes. |
| **RF5** | Pedir los datos faltantes (productos, cantidades, nombre, modalidad, dirección cuando aplique, hora y observaciones) antes de confirmar. |
| **RF6** | Registrar cada pedido confirmado una sola vez en la base de datos de pedidos, con identificador, fecha, canal y estado. |
| **RF7** | Enviar a la comanda de la panadería el pedido confirmado desde la base de datos de pedidos, sin un canal de mensajería adicional; los agotados y cambios de menú se reportan por Google Forms. |
| **RF8** | 	Permitir la intervención humana, la pausa del bot y el seguimiento de la conversación sin perder contexto ni duplicar pedidos. |
| **RF9** | Mantener una bitácora de cambios de menú, transiciones de pedido, envíos a la comanda y errores. |
| **RF10** | 	Consolidar cada día pedidos, estados e incidencias, y enviar el resumen a administración por Gmail. |


### 1.5 Requisitos no funcionales

| Código | Requisito |
|---|---|
| **RNF1** | Respuesta automática en 10 segundos o menos en condiciones normales; si una dependencia excede el umbral, se informa al usuario y el mensaje pasa a cola con reintento. |
| **RNF2** | Disponibilidad objetivo del 99 % mensual del flujo de recepción, sin contar la indisponibilidad de proveedores externos. |
| **RNF3** | Sin duplicados: idempotencia por identificador de mensaje o pedido, reintentos con espera incremental y cola de errores. |
| **RNF4** | Mínimo privilegio, cuentas institucionales, credenciales en un gestor seguro y registro de cambios. |
| **RNF5** | Proteger los datos personales (Ley 1581): guardar solo lo necesario para gestionar el pedido y aplicar la política de conservación aprobada. |
| **RNF6** | Trazabilidad del estado: recibido, validado, confirmado, enviado a cocina, en preparación, listo, entregado/cerrado, cancelado o con error. |
| **RNF7** | Formularios usables desde el móvil, computador o tablet |
| **RNF8** | Los cambios de menú se reflejan en las respuestas del bot en 1 minuto o menos. |


### 1.6 Restricciones

- postgresql es el repositorio operativo; Google Forms, el mecanismo de carga; Gmail, el canal de reporte.
- WhatsApp Business API es el canal con los clientes, solo para sus órdenes; no se usa para hablar con cocina.
- Loyverse TPV se conserva como punto de venta y como origen de la comanda impresa. La integración depende de permisos, de la capacidad de la API y de que el registro del pedido genere la comanda en cocina por lo cual no se incluirá en esta fase del proyecto.
- n8n sería el único orquestador, para una etapa posterior.


### 1.7 Indicadores de éxito

| Indicador | Línea base | Meta | Cómo se mide |
|---|---|---|---|
| **Tiempo de respuesta** | Por medir | ≥ 90 % de las consultas automatizables respondidas en ≤ 10 s | Marcas de tiempo en `Bitacora` |
| **Exactitud del pedido** | Por medir | ≥ 98 % de los pedidos confirmados sin corrección manual atribuible a la captura | Pedidos corregidos frente a confirmados |
| **Disponibilidad del menú** | Por medir | 100 % de los pedidos aceptados vinculados a una opción activa y disponible al confirmar | `disponibilidad_validada_en` en `DetallePedido` |
| **Registro en la base de datos** | Por medir | 100 % de los pedidos confirmados registrados una sola vez (sin duplicados) | `pedido_id` y `mensaje_origen_id únicos` en Pedidos |
| **Cierre diario** | Por medir | Resumen enviado de pedidos en cada jornada | Registro del envío en Gmail |


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
| Transcripción manual entre conversación y cocina | Una entidad Pedido con estados en la base de datos; la comanda se genera desde ella sin retranscribir |
| Lenguaje libre y variable del cliente | Extracción asistida por LLM, seguida de validación estructurada |
| Cambios que no se comunican en tiempo real | Un evento de cambio actualiza al bot y alerta a operación |
| Falta de conciliación diaria | Reporte consolidado y cola de excepciones |


### 2.3 TO-BE

Administración publica el menú del día y el catálogo, y cocina reporta la disponibilidad y los agotados, ambos mediante Forms que actualizan PostgreSQL → el cliente escribe al chatbot → el chatbot consulta el menú vigente, presenta las opciones y el LLM clasifica la intención y extrae el pedido → la validación contrasta datos, SKU y disponibilidad → el cliente acepta el resumen → el pedido se registra una sola vez como «confirmado» en la base de datos de pedidos → la comanda se genera desde la base de datos y llega a cocina → cocina u operador actualizan el estado mediante Form → administración revisa el resumen diario.

### 2.4 ¿Dónde aporta la IA?

| Tarea | Quién | Por qué / límite |
|---|---|---|
| Clasificar el mensaje (consulta, pedido, cambio, cancelación, solicitud humana) y extraer productos, cantidades y notas | IA generativa (LLM) | El lenguaje del cliente es libre. Salida en JSON validado |
| Presentar las opciones del menú del día y de otros productos de panadería, y redactar la respuesta natural | IA generativa (LLM) | Solo con datos del menú activo, reglas aprobadas y disponibilidad consultada |
| Detectar campos ausentes o ambiguos y preguntar | IA generativa (LLM) | Sin inferir direcciones, cantidades ni sustituciones |
| Presentar el resumen del pedido para confirmar | IA generativa (LLM) | Sobre datos ya validados |
| Validar disponibilidad, esquema, SKU, cantidades y estado | Reglas (sin IA) | Controles exactos: consultas al catálogo y restricciones de PostgreSQL |
| Registrar el pedido, generar la comanda y revisar el resumen diario | Reglas, PostgreSQL y operador | Identificador único para evitar duplicados; vistas sobre la base de datos |
| Atender casos ambiguos, cambios especiales e incidencias | Operador | La IA deriva cuando falta información o hay ambigüedad |

> **Límite de autoridad.** El LLM no modifica el inventario, no escribe en la base de datos por su cuenta, no confirma disponibilidad «de memoria» ni ejecuta acciones fuera del contexto autorizado. Solo propone; la validación y el registro los controlan las reglas y el operador.

### 2.5 Ficha «¿sí requiere ML?»

Se define que no se utiliza ML en esta etapa del proyecto.

### 2.6 Supuestos y riesgos

**Supuestos por validar en H1:** catálogo con ID; horarios estáticos siempre, zonas de entrega, reglas de domicilios, medios de pago, política de cancelación y responsables de cada bandeja; alojamiento y administración de PostgreSQL; mecanismo con el que los Forms actualizan la base de datos; mecanismo de escritura del pedido; mecanismo de entrega de la comanda (impresión o vista operativa); volumen simultáneo; cuentas y accesos.

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Menú desactualizado | Se promete un producto agotado | Form con vigencia y responsable, expiración y consulta del menú antes de confirmar |
| Escritura del pedido con errores u omisiones | Pedido sin registro o mal transcrito | Resumen aceptado por el cliente como fuente, revisión del operador y restricciones en PostgreSQL |
| Pedido registrado dos veces | Doble comanda o doble preparación | Clave primaria y restricción de unicidad por `pedido_id`; verificación antes de registrar |
| El LLM inventa o malinterpreta | Pedido incorrecto | Contexto acotado, esquema validado, confirmación explícita y derivación a humano |
| Permisos y datos personales | Exposición o cambio no autorizado | Roles de PostgreSQL con mínimo privilegio, retención definida y bitácora (Ley 1581) |
| Caída del servidor PostgreSQL | El bot no puede verificar disponibilidad ni registrar pedidos | Respaldos, no confirmar sin consulta vigente y contingencia manual |
| Forms mal diligenciados o sin acceso | Menú o estados desactualizados | Campos obligatorios y validados, responsable por Form y revisión diaria |
| Comanda no generada o no vista | Cocina no ve el pedido | Se consulta directamente `pedido_id` los que están confirmados, no hay otra fuente|

---
### 3.1 Arquitectura funcional

| Componente | En este proyecto |
|---|---|
| **Datos** | PostgreSQL: `menu_del_dia`, `productos`, `pedidos`, `detalle_pedido`, `alertas` y `bitacora` |
| **Vistas** | `v_comanda` (comanda), `v_pedidos_operativa` (vista operativa imprimible) y `v_resumen_diario` (resumen diario) |
| **Interfaz** | Chatbot para el cliente; Forms de alta, cambio, agotado y estado de preparación para administración y cocina; vista operativa para operador y cocina; comanda |
| **Reglas** | R1 a R10: vigencia y disponibilidad, datos mínimos, identificador único y separación de estados |
| **Orquestación** | No se aborda en esta fase (n8n queda para una fase posterior) |

```text
Cliente -> Chatbot (interfaz de conversación)
 -> consulta de menú del día, catálogo y disponibilidad (PostgreSQL)
 -> LLM con contexto acotado y salida JSON
 -> validación contra catálogo y confirmación del cliente
 -> Base de datos de pedidos (pedidos + detalle_pedido en PostgreSQL)
 -> Comanda generada desde la base de datos (v_comanda) -> cocina
 -> Resumen diario (v_resumen_diario)

Administración / Cocina -> Forms -> validación -> PostgreSQL -> menú y estados vigentes para el bot
```

### 3.2 Modelo de datos

| Tabla | Campos principales |
|---|---|
| `menu_del_dia` | `menu_id`, `fecha`, `sku`, `nombre`, `componentes`, `descripcion`, `cupo`, `disponible`, `hora_corte`, `alergenos_declarados`, `responsable`, `vigencia` (una fila por producto y fecha) |
| `productos` | `sku`, `nombre`, `descripcion`, `categoria` (desayuno, panadería u otra), `disponible`, `cupo`, `alergenos_declarados`, `vigencia_desde`, `vigencia_hasta`, `activo`, `actualizado_por`, `actualizado_en` |
| `pedidos` | `pedido_id`, `fecha_hora`, `telefono_normalizado`, `nombre`, `canal`, `modalidad`, `direccion`, `franja_solicitada`, `estado`, `notas`, `aviso_privacidad`, `comanda_status`, `comanda_enviada_en`, `ultima_actualizacion` |
| `detalle_pedido` | `pedido_id`, `linea`, `sku`, `nombre_snapshot`, `cantidad`, `notas_linea`, `disponibilidad_validada_en` |
| `alertas` | `alerta_id`, `tipo`, `severidad`, `pedido_id`, `origen`, `mensaje`, `creada_en`, `estado`, `responsable`, `resuelta_en` |
| `bitacora` | `evento_id`, `entidad`, `entidad_id`, `accion`, `actor`, `timestamp`, `resultado`, `detalle` (sin secretos) |

**Restricciones e integridad (propuesta a validar en H2):**

| Tipo | Aplicación |
|---|---|
| **Claves primarias** | `menu_id`, `sku`, `pedido_id`, (`pedido_id`, `linea`), `alerta_id`, `evento_id` |
| **Claves foráneas** | `detalle_pedido.pedido_id` → `pedidos`; `detalle_pedido.sku` y `menu_del_dia.sku` → `productos`; `alertas.pedido_id` → `pedidos` |
| **Unicidad** | `pedido_id` en `pedidos`; combinación `fecha` + `sku` en `menu_del_dia` |
| **Validaciones (CHECK)** | `cantidad > 0`; `cupo >= 0`; `modalidad` limitada a entrega o recogida; `dirección` obligatoria cuando la modalidad es entrega, según los campos definidos en H1 |
| **Dominios de estado** | `estado` con los valores de RNF5; `comanda_status` con valores como pendiente, enviada o error |

Los roles de PostgreSQL separan los permisos por perfil (chatbot, formularios, operador y administración), y las credenciales se guardan fuera de la base de datos. Si la concurrencia o el volumen aumentan, se revisa el dimensionamiento del servidor y de las conexiones.

### 3.3 Reglas de negocio

| Código | Regla | Dónde se implementa |
|---|---|---|
| **R1** | Solo se ofrecen productos activos y vigentes para la fecha y franja; la disponibilidad se verifica al iniciar y al confirmar | Consulta del bot a `menu_del_dia` y `productos` |
| **R2** | Un producto con disponibilidad desconocida no es confirmable: se pregunta al operador | Derivación a humano |
| **R3** | El pedido pasa a «confirmado» solo con datos mínimos, disponibilidad validada y resumen aceptado por el cliente | Validación contra catálogo y esquema |
| **R4** | Cantidades positivas; opciones, sustituciones, horarios y zonas se rigen por el catálogo | Restricciones CHECK y claves foráneas en PostgreSQL |
| **R5** | Cada pedido lleva un identificador único; un pedido repetido no genera doble registro ni doble comanda | Clave primaria y unicidad de `pedido_id` |
| **R6** | Cancelaciones y cambios conservan el historial; si el pedido ya está en la comanda, se comunica la actualización a cocina por la comanda y se crea una alerta | `bitacora`, `alertas` y comanda |
| **R7** | Toda operación fallida queda en `alertas` con responsable y acción pendiente | Tabla `alertas` |
| **R8** | El estado de la comanda (`comanda_status`) se separa del estado de preparación del pedido (`estado`) | Tabla `pedidos` |
| **R9** | Los menús y productos con vigencia vencida dejan de ser elegibles; el menú de desayunos conserva el catálogo y actualiza su disponibilidad diaria | Vigencias y expiración en las consultas |
| **R10** | El chatbot solo canaliza las órdenes de los clientes; cocina recibe los pedidos solo por la comanda | Diseño del flujo |

### 3.4 Diseño del chatbot

| Elemento | Decisión |
|---|---|
| **Objetivo** | Ofrecer opciones del menú del día disponible y de otros productos de panadería, tomar el pedido de forma estructurada y registrarlo en la base de datos de pedidos para generar la comanda |
| **Motor** | LLM de un proveedor aprobado; no se entrena un modelo propio |
| **Canal** | Interfaz de conversación del prototipo; WhatsApp queda para una fase posterior |
| **Contexto** | Menú del día, catálogo, disponibilidad, horarios y reglas, consultados en PostgreSQL con campos mínimos y marca de tiempo |
| **Salida** | El LLM solo propone un JSON (P2); se validan tipos, SKU elegibles, cantidades, privacidad y estado |
| **Confirmación** | El cliente acepta explícitamente el resumen; solo entonces se registra el pedido |
| **Trazabilidad** | Se registra la versión del prompt y del modelo, y se minimiza la conservación del texto conversacional |
| **Alternativa ante fallas** | Si el LLM falla, atención humana con un formulario alterno de captura |

### 3.5 Flujo de operación de esta fase

Sin orquestador, el flujo se ejecuta con PostgreSQL, los Forms y el apoyo del operador:

**A · Actualización de menú y estados.** Administración o cocina envían el Form de alta, cambio, agotado o estado de preparación → validación de campos, fecha, SKU y responsable → actualización de las filas vigentes de `menu_del_dia`, `productos` o `pedidos` → registro en `bitacora` → el bot responde con la versión vigente (≤ 1 minuto, RNF7).

**B · Conversación y pedido.** El cliente escribe al chatbot → el bot consulta menú del día, catálogo y disponibilidad en PostgreSQL → paso de IA (P1 + P2): clasifica la intención, presenta las opciones y extrae el pedido en JSON → validación de esquema, SKU y disponibilidad → si faltan datos, el bot los pregunta; si hay ambigüedad o solicitud humana, se deriva al operador → al confirmar, se revalida la disponibilidad y se muestra el resumen → tras la aceptación explícita del cliente, el pedido se registra en `pedidos` y `detalle_pedido` con `pedido_id` único.

**C · Comanda.** Pedido confirmado o cambiado → la comanda se genera desde `v_comanda` (ID, hora, modalidad, líneas y notas) en una vista legible e imprimible → se actualiza `comanda_status` y `comanda_enviada_en` → cocina registra los estados de preparación y entrega mediante Form.

**D · Resumen diario.** Al cierre de la jornada, administración revisa `v_resumen_diario`: pedidos por estado, modalidad y canal, con pendientes, fallos de comanda e incidencias.

**Errores.** Si la comanda no se genera o no se imprime, `comanda_status` queda «pendiente», se crea una alerta con responsable y el pedido queda imprimible en la vista operativa.

**Punto de control humano.** El operador atiende toda derivación del flujo B y revisa el registro de pedidos.

### 3.6 Prompts clave

#### P1 · Instrucción de sistema

```text
Eres el asistente de pedidos de Panadería Tomasseli. Responde en español, con tono
cordial y conciso. Presenta al cliente las opciones del menú del día y de los demás
productos de panadería que estén disponibles. Usa únicamente el menú, disponibilidad,
horarios y reglas recibidos como contexto en esta conversación. No inventes
productos, existencias, tiempos ni condiciones. No confirmes una orden hasta que la
validación indique disponible y el cliente acepte el resumen. Si la información
falta, está vencida o es ambigua, pregunta o deriva a una persona. No solicites datos
que no sean necesarios para gestionar el pedido.
```

#### P2 · Salida estructurada (el LLM propone; la validación decide)

```json
{
  "intent": "consulta | pedido | cambio | cancelacion | solicitud_humana",
  "items": [
    { "sku": "string", "quantity": "integer > 0", "notes": "string" }
  ],
  "customer_name": "string",
  "fulfillment": "string (entrega o recogida)",
  "address": "string (solo cuando aplique)",
  "requested_time": "string",
  "missing_fields": ["string"],
  "needs_human": "boolean",
  "response": "string"
}
```

### 3.7 Seguridad, privacidad y operación

- Roles de PostgreSQL por perfil con mínimo privilegio: el chatbot solo lee menús y productos y escribe pedidos; los Forms solo modifican los datos que les corresponden; administración y operador consultan por vistas.
- Cuentas institucionales con propietario organizacional y acceso restringido a la base de datos.
- Llaves de API y credenciales fuera de tablas, prompts y conversaciones.
- Datos del cliente limitados a lo necesario; el teléfono completo no aparece en la comanda salvo necesidad aprobada.
- Aviso de privacidad, finalidad, retención y atención de solicitudes definidos con un responsable de Tomasseli antes del piloto (Ley 1581).
- Registro de accesos y cambios, y copias de respaldo de la base de datos.

---

## 4. Implementación

### 4.1 Herramientas

LLM; Gamma o Canva y v0.dev para la presentación y el prototipo; PostgreSQL como base de datos; Forms para las actualizaciones de administración y cocina; impresora o vista operativa para la comanda; repositorio con prompts, scripts SQL, configuración y registro de cambios.

### 4.2 Plan por hitos

| Hito | Tareas | Entregable |
|---|---|---|
| **H1** | AS-IS y TO-BE validados con Tomasseli; reglas de domicilios, horarios y cortes; catálogo (menú del día y otros productos) y responsables; medición de la línea base; inventario de accesos; definición del alojamiento de PostgreSQL, del mecanismo con que los Forms actualizan la base de datos, de la escritura del pedido y de la entrega de la comanda; P1 v1 | Documento de descubrimiento y biblioteca de prompts |
| **H2** | Diccionario de datos y esquema de PostgreSQL (tablas, restricciones y vistas); reglas R1–R10 trazables a los requisitos; esquema P2 probado con 10 mensajes reales o simulados, verificando cada producto contra el menú | Documento base + tabla de verificación |
| **H3** | Presentación ejecutiva; prototipo del chatbot, de la vista operativa y de la comanda; MVP: base de datos PostgreSQL con restricciones y vistas, y Forms de menú del día, productos, agotados y estados; pruebas P-01 a P-12 | PDF, `index.html`, script SQL del esquema, capturas y registro de pruebas |
| **H4** | *No aplica en este alcance (sin modelo de ML).* | — |
| **H5** | *No se aborda en esta fase (flujo automatizado con n8n e integración con Loyverse TPV).* | — |
| **H6** | Piloto del MVP, capacitación por rol, manual operativo y guion | Demo y acta de habilitación |

### 4.3 Plan de pruebas

| # | Caso | Resultado esperado |
|---|---|---|
| **P-01** | Alta o edición de menú por Form | Campos validados, cambio auditado en `bitacora` y visible al bot en ≤ 1 minuto |
| **P-02** | Consulta del menú del día y de otros productos de panadería | El bot muestra solo opciones vigentes y disponibles |
| **P-03** | Producto agotado reportado por Form de cocina | El agotado no se confirma y se ofrecen alternativas autorizadas |
| **P-04** | Pedido completo y claro | Resumen, aceptación, un registro en `pedidos` y `detalle_pedido`, pedido en la comanda, ningún mensaje a cocina por el chatbot y respuesta dentro del objetivo |
| **P-05** | Pedido incompleto o ambiguo | Pregunta solo los campos faltantes; no confirma antes de la aceptación |
| **P-06** | Pedido repetido (mismo identificador) | La restricción de unicidad impide el duplicado; queda un registro y una comanda, y el intento queda reconocido |
| **P-07** | Falla del LLM, del chatbot o de la base de datos | Mensaje de espera o derivación al operador y formulario alterno; nunca una confirmación falsa |
| **P-08** | La comanda no se genera o no se imprime | Pedido con `comanda_status` pendiente, alerta, copia imprimible y regeneración sin duplicar |
| **P-09** | Cambio o cancelación después de confirmar | Historial conservado y comanda actualizada, con alerta a cocina |
| **P-10** | Resumen diario | `v_resumen_diario` trae totales por estado y canal, pendientes, fallos de comanda e incidencias |
| **P-11** | Permisos y seguridad | Roles no autorizados no cambian el catálogo; los secretos no aparecen en tablas, prompts ni conversaciones |
| **P-12** | Tiempo de respuesta | Objetivo de 10 s medido en las pruebas del piloto |

### 4.4 Guion del Demo Day

1. El problema: opciones agotadas, transcripciones y diferencias, con la línea base medida en H1.
2. En vivo: cocina marca un agotado por Form → el bot deja de ofrecerlo en menos de un minuto.
3. En vivo: el cliente pide al chatbot; el bot presenta el menú del día y otros productos; el pedido tiene un dato faltante → pregunta → resumen → confirmación → registro en PostgreSQL → comanda.
4. Un pedido repetido → un solo registro; una comanda no generada → alerta y pedido imprimible.
5. El resumen diario desde la base de datos.
6. Los límites de la IA: qué propone, qué valida el catálogo y qué decide la persona.

### 4.5 Plan B

| Evento | Acción |
|---|---|
| Chatbot o LLM fuera de servicio | Atención humana y formulario alterno de captura con ID único; registro en PostgreSQL al restablecer |
| PostgreSQL inaccesible o datos vencidos | Pausar confirmaciones automáticas; restaurar o consultar el último respaldo; validar existencias a mano |
| Un Form no actualiza la base de datos | Registro manual del cambio por el responsable y revisión de `bitacora`; avisar al operador para que el bot ofrezca la versión correcta |
| La comanda no se genera o no se imprime | Reimprimir desde la vista operativa y registrar la incidencia; pedido marcado «comanda pendiente» |
| Falla el registro del pedido | Registro manual por el operador con ID único y conciliación antes de generar la comanda |

### 4.6 Criterios de salida y operación

La salida a piloto requiere: catálogo y SKU aprobados; horarios y reglas aprobados; esquema de PostgreSQL con restricciones y respaldos operativos; Forms de actualización probados; flujo de la base de datos de pedidos a la comanda probado; responsables de excepciones; textos de privacidad; acceso protegido; procedimiento manual; y aceptación del piloto.

En operación, las excepciones y las comandas pendientes se revisan a diario; la exactitud, los tiempos, la disponibilidad del menú y las causas de derivación, cada semana. Todo cambio de reglas, prompts, catálogo o esquema se registra, se valida y tiene reversión documentada.

### 4.7 Evolución prevista (fuera de esta fase)

Para fases posteriores quedan: automatización del flujo con n8n (recepción por WhatsApp Business API, idempotencia, reintentos, alertas y resumen por Gmail) y la integración con Loyverse TPV. El esquema de PostgreSQL y las reglas de esta ficha se mantienen para facilitar esa evolución.

---

## Anexo A · Decisiones pendientes de validación

Hasta validarlas, los componentes descritos son diseño objetivo y toda herramienta externa queda sujeta a prueba técnica.

- Alojamiento y administración de PostgreSQL (servidor, versión, acceso, respaldos y retención).
- Mecanismo con el que cada Form (de administración y de cocina) escribe en PostgreSQL y herramienta de Forms a usar.
- Mecanismo de escritura del pedido confirmado en la base de datos (carga asistida por el operador o servicio propio del chatbot) y quién lo ejecuta.
- Plataforma o interfaz del chatbot para el prototipo y forma en que consulta el menú y la disponibilidad en PostgreSQL.
- Mecanismo de entrega de la comanda: impresión desde la vista operativa u otro medio.
- Contenido de la comanda (notas, modalidad, hora, alérgenos declarados) y cómo se refleja en ella un cambio o una cancelación.
- Si cada producto y plato tiene SKU.
- Qué productos de panadería, además del menú del día, se ofrecen en el chatbot.
- Método de registro de domicilios.
- Si las existencias se controlan por ingrediente, por producto o por conteo manual.
- Campos obligatorios de entrega.
- Horarios de desayuno y almuerzo, y hora límite.
- Estados de preparación que cocina reporta por Form (en preparación, listo) y quién puede diligenciarlos.
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
