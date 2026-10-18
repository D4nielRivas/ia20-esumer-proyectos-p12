# FICHA DE ESPECIFICACIÓN DEL PROYECTO

# Automatización operativa — Panadería Tomasseli

**Gestión de pedidos, menú, inventario y cocina**
Google Workspace · WhatsApp · Loyverse · n8n · Machine Learning

---

## Ficha técnica

| Campo | Valor |
|---|---|
| Organización | Panadería Tomasseli |
| Alcance | Gestión de pedidos, menú, inventario y cocina, con previsión de pedidos |
| Documento | Especificación funcional y técnica |
| Versión | 1.2 |
| Fecha | 18 de octubre de 2026 |
| Estado | Propuesta para validación operativa |
| IA generativa | LLM para comprensión y redacción; reglas determinísticas para disponibilidad, confirmación y registro |
| Machine Learning | Predicción de las órdenes de los clientes con base en las tendencias de los pedidos (ver 3.4) |
| Conexión modelo–flujo | Lote: el modelo escribe sus resultados en una hoja que el flujo lee |
| Orquestación | n8n, como único orquestador en producción |
| Canales y sistemas | WhatsApp Business API (solo órdenes de clientes) · Loyverse TPV (registro de venta y comanda impresa en cocina) · Google Sheets y Forms · Gmail |

## Contenido

1. **Necesidades:** contexto, problema, actores, requisitos funcionales y no funcionales, restricciones e indicadores de éxito.
2. **Entendimiento:** proceso actual y propuesto, causas raíz, papel de la IA, ficha «¿sí requiere ML?», supuestos y riesgos.
3. **Estructuración:** arquitectura funcional, modelo de datos, reglas de negocio, diseño del modelo de ML, flujo automatizado, prompts y seguridad.
4. **Implementación:** herramientas, plan por hitos, plan de pruebas, contingencias y criterios de salida.
5. **Anexo A:** decisiones pendientes de validación.

> La especificación evita deliberadamente cualquier contenido de carácter económico.

---

## 1. Necesidades

### 1.1 Contexto

Tomasseli coordina pedidos que llegan por WhatsApp con la disponibilidad del menú, la operación de cocina, el inventario y el registro de ventas en Loyverse TPV. WhatsApp se usa únicamente para canalizar las órdenes de los clientes; la comunicación con cocina es directa, mediante comanda impresa desde Loyverse. La solución organiza el dato operativo en Google Sheets y conecta los sistemas mediante automatizaciones en n8n. La IA generativa facilita la conversación, pero las reglas determinísticas controlan la disponibilidad, la confirmación y el registro. Un modelo de Machine Learning predice las órdenes de los clientes a partir de las tendencias de los pedidos, como apoyo informativo a la planeación.

### 1.2 Problema

La actualización manual y la circulación de información por canales separados pueden causar:

| Síntoma | Línea base |
|---|---|
| Respuestas con opciones agotadas | Por medir en H1 |
| Reprocesos al transcribir pedidos | Por medir en H1 |
| Demoras en cocina | Por medir en H1 |
| Diferencias entre lo solicitado, preparado y registrado | Por medir en H1 |
| Ausencia de una estimación de los pedidos esperados para anticipar la preparación | Por medir en H1 |

> La especificación no aporta cifras de línea base; el hito H1 incluye definirla. Las metas de 1.7 se recalibran con esa línea base y el piloto.

### 1.3 Actores y necesidades

| Actor | Necesita | Canal y contexto |
|---|---|---|
| Cliente | Consultar menú y disponibilidad vigente, resolver dudas, especificar pedido, entrega o recogida y recibir confirmación clara. | WhatsApp |
| Administración | Mantener catálogo, horarios, estados, pedidos y cierres; revisar excepciones; tener resumen diario consolidado; consultar la previsión de pedidos. | Google Sheets, Forms y Gmail |
| Cocina | Recibir los pedidos confirmados mediante comanda impresa legible; reportar agotados y cambios; consultar la previsión de pedidos. | Comanda impresa desde Loyverse; Google Forms y vista operativa desde móvil |
| Atención/operador | Consultar historial y hacerse cargo de conversaciones ambiguas, cambios especiales o incidencias. | Vista operativa de pedidos y conversaciones |
| Integraciones | Mantener consistencia entre Sheets, WhatsApp Business API y Loyverse TPV, con trazabilidad y reintentos. | Sin interfaz propia |

### 1.4 Requisitos funcionales

| Código | Requisito |
|---|---|
| RF1 | Publicar una fuente de verdad para menú fijo de desayunos, menú diario/semanal de almuerzos y disponibilidad por producto. |
| RF2 | Permitir a administración/cocina actualizar el menú mediante Google Forms validado, sin editar directamente celdas operativas. |
| RF3 | Consultar menú activo y disponibilidad antes de ofrecer, aceptar o confirmar un producto. |
| RF4 | Atender conversaciones en WhatsApp Business API; comprender intención, resolver consultas y capturar pedido estructurado. WhatsApp solo canaliza las órdenes de los clientes. |
| RF5 | Solicitar datos faltantes (productos, cantidades, nombre, modalidad, dirección cuando aplique, hora y observaciones) antes de confirmar. |
| RF6 | Registrar cada pedido confirmado una sola vez en el consolidado de Google Sheets, con identificador, fecha, canal y estado. |
| RF7 | Comunicar a cocina el pedido confirmado de forma directa mediante comanda impresa desde Loyverse, sin canal de mensajería adicional; los agotados y cambios de menú se reportan por Google Forms. |
| RF8 | Sincronizar pedido/venta con Loyverse TPV mediante integración disponible, con referencia cruzada y manejo de fallas. |
| RF9 | Consolidar diariamente pedidos, ventas, estados, incidencias y diferencias para envío administrativo por Gmail. |
| RF10 | Permitir intervención humana, pausa del bot y seguimiento de conversación sin perder contexto ni duplicar pedidos. |
| RF11 | Mantener bitácora de cambios de menú, transiciones de pedido, llamadas a integraciones y errores. |
| RF12 | Facilitar la conciliación de ventas y pedidos, incluyendo el estado de sincronización con Loyverse. |
| RF13 | Predecir las órdenes de los clientes (cantidad esperada por producto, fecha y franja) con base en las tendencias del historial de pedidos, y ponerla a disposición de administración y cocina como apoyo informativo, incluida en el resumen diario. |

### 1.5 Requisitos no funcionales

| Código | Requisito |
|---|---|
| RNF1 | Respuesta automática objetivo: hasta 10 segundos en condiciones normales; si una dependencia excede el umbral, informar al usuario y pasar a cola/reintento. |
| RNF2 | Disponibilidad operativa objetivo: 99 % mensual del flujo de recepción, excluyendo la indisponibilidad de proveedores externos. |
| RNF3 | Evitar duplicados mediante idempotencia por identificador de mensaje/pedido; reintentos con espera incremental y cola de errores. |
| RNF4 | Acceso de mínimo privilegio, cuentas institucionales, credenciales en gestor seguro y registro de cambios. |
| RNF5 | Proteger datos personales; retener solo la información necesaria para gestionar el pedido y aplicar la política de conservación aprobada por Tomasseli. |
| RNF6 | Trazabilidad de estado: recibido, validado, confirmado, enviado a cocina, en preparación, listo, entregado/cerrado, cancelado o con error. |
| RNF7 | Interfaz de actualización usable desde móvil; comandas de cocina concisas y legibles; pedidos imprimibles desde la vista operativa en caso de contingencia. |
| RNF8 | Los cambios de menú deben reflejarse en la consulta del bot en un máximo objetivo de 1 minuto. |
| RNF9 | Cada previsión de pedidos queda registrada con fecha de generación y versión del modelo; una previsión vencida no se muestra como vigente. El entrenamiento y la previsión usan datos agregados, sin teléfono, nombre ni dirección de clientes. |

### 1.6 Restricciones

Google Sheets es el repositorio operativo acordado; Google Forms, el mecanismo de carga; WhatsApp Business API, el canal conversacional con los clientes y solo para sus órdenes; Gmail, el canal de reporte; y Loyverse TPV se conserva como punto de venta y como origen de la comanda impresa que recibe cocina. La integración efectiva con Loyverse depende de permisos, capacidades de API/conector y validación de los identificadores de producto, y de que el registro del pedido genere la comanda en cocina. n8n es el único orquestador de producción. No se atribuye a Sheets comportamiento de inventario transaccional de alta concurrencia. La previsión de pedidos depende del historial de pedidos disponible y es solo informativa.

### 1.7 Indicadores de éxito

| Indicador | Línea base | Meta | Cómo se mide |
|---|---|---|---|
| Tiempo de respuesta | Por medir | Al menos 90 % de consultas automatizables respondidas en hasta 10 s | Marcas de tiempo en bitácora |
| Exactitud de pedido | Por medir | Al menos 98 % de pedidos confirmados sin corrección manual atribuible a captura | Pedidos corregidos vs. confirmados |
| Disponibilidad de menú | Por medir | 100 % de pedidos aceptados vinculados a una opción activa/disponible al confirmar | `disponibilidad_validada_en` en DetallePedido |
| Integración POS | Por medir | Al menos 98 % de pedidos elegibles sincronizados o señalados en cola de excepción | `pos_status` en Pedidos |
| Comanda de cocina | Por medir | 100 % de pedidos confirmados generan comanda impresa o incidencia visible y recuperable | `pos_status` en Pedidos y hoja Alertas |
| Cierre diario | Por medir | Resumen enviado y cuadre revisable cada jornada operativa | Registro del envío Gmail |
| Previsión de pedidos | Línea base simple: promedio histórico por día de la semana y franja | Error de pronóstico menor que el de la línea base simple; valor objetivo por calibrar en el piloto | Comparación previsión vs. pedidos reales en el periodo de prueba |

> Las metas son criterios iniciales de aceptación; se recalibran con línea base y piloto.

---

## 2. Entendimiento

### 2.1 Proceso actual (AS-IS)

1. El cliente pregunta por WhatsApp o solicita un producto.
2. El equipo consulta menú/disponibilidad desde información dispersa o conocimiento del turno. ❌ *Aquí se ofrecen opciones agotadas.*
3. El pedido se interpreta y transcribe manualmente para cocina y/o TPV. ❌ *Aquí nacen los reprocesos y diferencias.*
4. Cocina prepara; cambios y agotados se comunican de manera no siempre sincronizada. ❌ *Aquí se generan demoras.*
5. Venta, entrega y cierre se registran en sistemas separados y se concilian al final del día.

### 2.2 Causas raíz

| Causa raíz | Cómo se aborda |
|---|---|
| Menú y stock sin fuente operativa única | Se centraliza menú/disponibilidad y se define responsable de actualización. |
| Transcripción manual entre conversación, cocina y TPV | Se captura una entidad Pedido con estados y referencia cruzada; la comanda de cocina se emite desde Loyverse sin retranscribir. |
| Variación del lenguaje del cliente | Extracción asistida por LLM, seguida de validación estructurada. |
| Cambios no comunicados en tiempo real | Un evento de cambio distribuye la actualización al bot y alerta a operación. |
| Falta de conciliación diaria | Reporte consolidado y cola de excepciones para revisión. |
| Falta de anticipación de los pedidos esperados | Modelo de ML que predice las órdenes a partir de las tendencias históricas de pedidos. |

### 2.3 Proceso propuesto (TO-BE)

1. Administración publica menú fijo y menú diario/semanal en Sheets; cocina actualiza por Form. La automatización valida campos, fecha y estado.
2. El cliente inicia chat por WhatsApp. El bot obtiene menú activo y disponibilidad, responde con contenido vigente y clasifica la intención.
3. El bot captura el pedido en borrador y verifica datos requeridos y disponibilidad nuevamente al confirmar.
4. El servicio registra el pedido con clave idempotente y estado «confirmado»; devuelve la confirmación al cliente.
5. n8n sincroniza el pedido con Loyverse, que emite la comanda impresa en cocina; registra el resultado y reintenta o deriva excepciones.
6. Los cambios de preparación/entrega actualizan el consolidado; Gmail envía el resumen operativo diario para el cuadre administrativo.
7. De forma periódica, el modelo de ML predice las órdenes esperadas a partir de las tendencias del historial de pedidos; la previsión queda disponible en Sheets para administración y cocina, y se incluye en el resumen diario.

### 2.4 ¿Dónde aporta la IA?

| Tarea | Quién la hace | Por qué / límite |
|---|---|---|
| Comprensión de mensajes: clasificar consulta, pedido, cambio, cancelación o solicitud humana; extraer productos, cantidades y notas | LLM | El lenguaje del cliente es libre y variable. Salida en JSON validado. |
| Atención contextual: redactar respuesta natural | LLM | Solo con datos recuperados del menú activo, reglas aprobadas y disponibilidad consultada. |
| Aclaración: detectar campos ausentes o ambiguos y preguntar brevemente | LLM | Sin inferir direcciones, cantidades ni sustituciones. |
| Resumen de pedido: presentar al cliente el resumen de confirmación | LLM | Sobre datos ya validados por reglas. |
| Predecir las órdenes de los clientes según las tendencias de los pedidos | Modelo de ML | Es un patrón en datos históricos de pedidos. Salida informativa: no confirma ni limita pedidos. |
| Validar disponibilidad, esquema, SKU, cantidades y estado | Reglas (sin IA) | Son controles exactos; el orquestador valida. |
| Registrar pedido, sincronizar Loyverse (comanda de cocina), conciliar y cerrar | Reglas y orquestador | Ejecución determinística con idempotencia. |
| Atender casos ambiguos, cambios especiales e incidencias | Persona (operador) | La IA deriva cuando falta información o hay ambigüedad. |
| Decidir cuánto preparar a partir de la previsión | Persona (administración y cocina) | El modelo solo orienta. |

**Límite de autoridad:** el LLM no modifica inventario, no crea ventas en TPV, no confirma disponibilidad por memoria ni ejecuta acciones fuera de herramientas autorizadas. El modelo de ML no modifica inventario, cupos ni disponibilidad, no acepta ni rechaza pedidos y no dispara acciones sobre clientes; su salida es una previsión consultiva.

### 2.5 Ficha «¿sí requiere ML?»

| Pregunta | Respuesta |
|---|---|
| ¿Qué se quiere predecir? | Las órdenes de los clientes: cantidad esperada de pedidos por producto (SKU), fecha y franja, con base en las tendencias de los pedidos. |
| ¿Con qué datos? | Historial de Pedidos y DetallePedido: fecha, franja, SKU, cantidad, modalidad, canal y estado; cantidades de periodos previos como medida de tendencia. |
| ¿Cómo sabremos que funciona? | El error de pronóstico (previsión vs. pedidos reales) debe ser menor que el de la línea base simple (promedio histórico por día de la semana y franja). El valor objetivo se calibra en el piloto. |
| ¿Hay una alternativa sin ML? | Sí: el promedio histórico por día de la semana y franja. El modelo debe mejorar sobre esa línea base; si no lo hace, se recomienda no usarlo. |
| Conclusión | Se usa ML para la previsión de pedidos, de forma informativa. La recomendación de uso o no uso es un entregable del hito H5. |

### 2.6 Supuestos y riesgos

**Supuestos por validar:** catálogo/SKU disponible; horarios, zonas de entrega, reglas de domicilios, medios de pago, política de cancelación y responsables de cada bandeja; correspondencia entre menú y productos Loyverse; que el registro del pedido en Loyverse genere la comanda impresa en cocina; volumen simultáneo; disponibilidad de cuentas y accesos de API; existencia de un historial de pedidos suficiente para entrenar la previsión.

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Menú desactualizado | Promesa de producto agotado | Formulario con vigencia, revisión por responsable, expiración automática y recarga previa a confirmar. |
| Falla de API/proveedor | Pedido sin comanda en cocina o sin registro en POS | Cola durable, reintento, alerta de error, consola de excepciones, y procedimiento manual con pedido imprimible desde la vista operativa. |
| Duplicados/reintento | Doble preparación/venta | Idempotencia, identificador único y reconciliación de eventos antes de repetir escritura. |
| El LLM inventa o malinterpreta | Pedido incorrecto | Contexto acotado (RAG), esquema validado, confirmación explícita y derivación a humano. |
| Permisos/datos personales | Exposición o cambio no autorizado | Mínimo privilegio, acceso por rol, retención definida y bitácora. |
| Caída de Sheets/límites | Bot sin disponibilidad verificable | Caché de lectura con marca de tiempo; no confirmar con caché vencida; contingencia manual. |
| Comanda no generada o no impresa en cocina | Cocina no ve el pedido | Estado `pos_status` y tablero de pedidos pendientes, alerta al responsable y copia impresa desde la vista operativa. |
| Historial insuficiente o previsión errónea | Preparación mal dimensionada | Uso solo informativo; comparación obligatoria con la línea base; marca de fecha y versión; no publicar si no mejora la línea base; decisión final humana. |

---

## 3. Estructuración

### 3.1 Arquitectura funcional

```text
Cliente WhatsApp (solo órdenes de clientes)
  -> WhatsApp Business API / Webhook
  -> Orquestador n8n
       -> normalización, idempotencia, reglas y bitácora
       -> consulta menú/disponibilidad en Google Sheets
       -> Motor LLM con contexto acotado y salida estructurada
       -> validación determinística y confirmación
       -> Pedido consolidado en Sheets
       -> Loyverse TPV (adaptador/API; reconciliación)
            -> comanda impresa en cocina
       -> Gmail resumen diario (incluye previsión de pedidos)

Administración / Cocina
  -> Google Forms -> validación -> Sheets -> actualización bot

Historial de Pedidos y DetallePedido (Sheets)
  -> modelo de ML (previsión de órdenes por tendencias)
  -> hoja PrediccionPedidos (lote) -> vistas de administración y cocina / Gmail
```

| Componente | Qué es en este proyecto |
|---|---|
| Google Sheets | Fuente operativa: MenuDesayunos, MenuAlmuerzos, Productos, Pedidos, DetallePedido, Alertas, Bitacora y PrediccionPedidos. Se separan hojas de captura, catálogos y vistas de reporte. |
| Google Forms | Captura guiada de alta/cambio/agotado de menú, con fecha efectiva, responsable y aprobación cuando aplique. |
| WhatsApp Business API | Recepción de webhooks y envío de respuestas a clientes; plantillas aplicables y control de ventana/sesión según la configuración vigente del canal. No se usa para comunicación con cocina. |
| Orquestador (n8n) | Recibe el evento, valida, coordina APIs, reintenta, registra errores y evita duplicados. Mantiene los secretos fuera de las hojas. |
| Motor de IA (LLM) | LLM invocado desde n8n: extracción estructurada, preguntas aclaratorias y redacción basada en contexto. |
| Modelo de ML | Predicción de las órdenes de los clientes a partir de las tendencias de los pedidos. Se ejecuta por lote y escribe en PrediccionPedidos; la herramienta de ML se define en H5. |
| Loyverse TPV | Registro/consulta de venta, conciliación por SKU/ID externo y emisión de la comanda impresa para cocina, sujeto a validación de API y permisos disponibles. |
| Gmail | Envío automático del cierre diario a destinatarios autorizados con totales, estados, errores, diferencias y previsión de pedidos. |

**Recomendación de control:** implementar n8n como única capa de integración, con adaptadores lógicos por proveedor. La modalidad de despliegue y administración de n8n, sus límites, el registro de ejecuciones y la política de credenciales se validan en el diseño detallado.

### 3.2 Modelo de datos

| Hoja | Campos principales |
|---|---|
| MenuDesayunos | `menu_id`, `sku`, `nombre`, `descripcion`, `categoria`, `disponible`, `cupo`, `alergenos_declarados`, `vigencia_desde/hasta`, `actualizado_por`, `actualizado_en`. Catálogo fijo con disponibilidad diaria. |
| MenuAlmuerzos | `menu_id`, `fecha`, `sku`, `nombre`, `componentes`, `descripcion`, `cupo`, `disponible`, `hora_corte`, `alergenos_declarados`, `responsable`, `vigencia`. Una fila por producto y fecha. |
| Productos | `sku`, `nombre_Loyverse`, `loyverse_item_id`, `unidad`, `activo`, `politica_stock`, `actualizado_en`. No se infieren equivalencias por texto cuando existe SKU. |
| Pedidos | `pedido_id`, `mensaje_origen_id`, `fecha_hora`, `telefono_normalizado`, `nombre`, `canal`, `modalidad`, `direccion`, `franja_solicitada`, `estado`, `subtotal`, `notas`, `consentimiento/aviso_aplicable`, `pos_status`, `loyverse_sale_id`, `ultima_actualizacion`. |
| DetallePedido | `pedido_id`, `linea`, `sku`, `nombre_snapshot`, `cantidad`, `notas_linea`, `disponibilidad_validada_en`. Captura el dato vigente al confirmar. |
| Alertas | `alerta_id`, `tipo`, `severidad`, `pedido_id`, `origen`, `mensaje`, `creada_en`, `estado`, `responsable`, `resuelta_en`. |
| Bitacora | `evento_id`, `entidad`, `entidad_id`, `accion`, `actor/sistema`, `timestamp`, `resultado`, `correlation_id`, `detalle_tecnico` (sin secretos). |
| PrediccionPedidos | `prediccion_id`, `fecha_objetivo`, `franja`, `sku`, `cantidad_prevista`, `generado_en`, `version_modelo`, `vigente`. Solo datos agregados, sin datos personales de clientes. |

Las hojas deben proteger rangos de catálogo y fórmulas, validar enumeraciones/fechas/cantidades y usar identificadores estables. Sheets es un repositorio de operación ligera: si la concurrencia, el volumen o la consistencia exceden el umbral acordado, se migra el registro transaccional a una base de datos y se conserva Sheets como vista administrativa.

### 3.3 Reglas de negocio

| Código | Regla | Dónde se implementa |
|---|---|---|
| R1 | Solo ofrecer productos activos y vigentes para la fecha y franja actuales; verificar disponibilidad al iniciar y al confirmar. | n8n, consulta a MenuDesayunos/MenuAlmuerzos |
| R2 | Un producto con disponibilidad desconocida se trata como no confirmable: preguntar a operador, no asumir existencia. | n8n y derivación a humano |
| R3 | El pedido solo pasa a «confirmado» tras obtener datos mínimos, validar disponibilidad y mostrar un resumen aceptado por el cliente. | Validación determinística |
| R4 | Las cantidades deben ser positivas; opciones, sustituciones, horarios y zonas se rigen por catálogo/reglas aprobadas. | Validación de esquema |
| R5 | La clave idempotente combina canal, identificador de mensaje/evento y operación; pedidos repetidos no generan doble comanda ni doble venta. | n8n (deduplicación) |
| R6 | Cancelaciones/cambios conservan historial; se comunican a cocina mediante la comanda desde Loyverse, según la capacidad validada, si ya hubo sincronización. | Bitácora, Loyverse |
| R7 | Toda operación fallida queda en Alertas/cola de error con responsable y acción pendiente. | Hoja Alertas |
| R8 | El estado POS se separa del estado de cocina para distinguir pedido aceptado, preparado y registrado en venta. | Campos `estado` y `pos_status` |
| R9 | Los menús con vigencia expirada dejan de ser elegibles; el menú fijo de desayunos conserva el catálogo, pero su disponibilidad diaria se actualiza. | Vigencias y expiración automática |
| R10 | La previsión de pedidos es informativa: no modifica disponibilidad, cupos ni inventario, y nunca interviene en aceptar, confirmar o rechazar un pedido. | Separación entre PrediccionPedidos y las hojas de menú/pedidos |
| R11 | Una previsión se publica solo si el modelo mejora la línea base simple; cada previsión lleva fecha de generación y versión, y una previsión vencida no se muestra como vigente. | Escenario E y campo `vigente` |
| R12 | WhatsApp solo canaliza las órdenes de los clientes; la comunicación con cocina se hace exclusivamente mediante la comanda impresa desde Loyverse. | Diseño de integración |

### 3.4 Diseño del modelo de ML

| Elemento | Decisión |
|---|---|
| Objetivo | Predecir las órdenes de los clientes con base en las tendencias de los pedidos. |
| Dataset | Historial de Pedidos y DetallePedido, agregado por fecha, franja y SKU. Se excluyen pedidos cancelados o con error. |
| Variable objetivo | `cantidad_pedida` por SKU, fecha y franja. |
| Variables de entrada | Día de la semana, franja, SKU, categoría, modalidad, canal y cantidades de periodos previos (tendencia). |
| Preparación | Revisar nulos y duplicados; agregar el detalle por fecha, franja y SKU; separar entrenamiento y prueba de forma cronológica (por ejemplo, 70/30). No usar variables conocidas solo después del hecho: fuga de información. Excluir datos personales (teléfono, nombre, dirección). |
| Algoritmos | Candidatos: modelo de regresión y árbol de regresión, a definir en H5 junto con la herramienta de ML. |
| Métrica principal | Error de pronóstico entre la previsión y los pedidos reales; objetivo por calibrar en el piloto. |
| Comparación obligatoria | Modelo frente a la línea base simple: promedio histórico por día de la semana y franja. |
| Conexión modelo–flujo | Lote: se puntúan las fechas objetivo con la frecuencia definida y el resultado se escribe en PrediccionPedidos; el flujo lee esa hoja. |
| Uso de la salida | Vistas de administración y cocina, y sección de previsión en el resumen diario de Gmail. |
| Criterio de uso | Si el modelo no mejora la línea base o el historial es insuficiente, no se publica y se documenta como hallazgo. |
| Límite | La previsión es consultiva (R10); no automatiza decisiones sobre pedidos, inventario ni clientes. |

**Motor LLM (comprensión y atención)**

| Elemento | Decisión |
|---|---|
| Modelo | LLM de proveedor aprobado, invocado desde n8n. No se entrena ni se ajusta un modelo propio. |
| Contexto | Recuperación desde Sheets con campos mínimos y marca de tiempo (contexto acotado). |
| Salida | JSON estructurado; el LLM solo propone. |
| Validación | n8n valida tipos, SKU elegibles, cantidades, privacidad y estado. |
| Trazabilidad | Se guarda versión del prompt, modelo, `correlation_id` y resultado técnico; se minimiza la conservación de texto conversacional. |
| Alternativa sin IA | Atención humana y formulario alterno de captura si el LLM o n8n caen. |

### 3.5 Diseño del flujo automatizado

**Escenario A · Actualización de menú**

| Paso | Qué pasa |
|---|---|
| Trigger | Envío del Google Form de alta/cambio/agotado. |
| Acción 1 | Validar campos, fecha, SKU y responsable. |
| Acción 2 | Actualizar filas vigentes. |
| Acción 3 | Registrar en Bitácora. |
| Acción 4 | Actualizar caché de lectura (objetivo ≤ 1 minuto, RNF8). |
| Resultado | Confirmar publicación o alertar el error. |

**Escenario B · Conversación y pedido (WhatsApp)**

| Paso | Qué pasa |
|---|---|
| Trigger | Webhook de WhatsApp. |
| Acción 1 | Deduplicar el mensaje (clave idempotente). |
| Acción 2 | Recuperar menú y disponibilidad. |
| Paso de IA | El LLM clasifica la intención y extrae el pedido en JSON. |
| Validación | Validar esquema y reglas. |
| Decisión | Si faltan datos, pedir faltantes; si hay ambigüedad o solicitud humana, derivar. |
| Acción 3 | Validar stock y datos al confirmar y mostrar el resumen al cliente. |
| Acción 4 | Tras la aceptación explícita, escribir Pedido y DetallePedido. |
| Resultado | Responder la confirmación al cliente. |

**Escenario C · Cocina y POS (Loyverse)**

| Paso | Qué pasa |
|---|---|
| Trigger | Evento de pedido confirmado o de cambio. |
| Acción 1 | Mapear SKU a `loyverse_item_id`. |
| Acción 2 | Crear/registrar la transacción en Loyverse según la API disponible; Loyverse emite la comanda impresa en cocina (ID, hora, modalidad, líneas y notas). |
| Acción 3 | Guardar `loyverse_sale_id` y `pos_status`. |
| Acción 4 | Registrar el estado de preparación/entrega que reporta cocina u operador en la vista operativa y actualizar el consolidado. |
| Resultado | Confirmación al cliente por WhatsApp si corresponde. |
| Error | Reintentar con idempotencia; si persiste, `pos_status` queda pendiente, se crea una alerta con responsable y el pedido queda disponible e imprimible en la vista operativa para conciliación manual. |

**Escenario D · Cierre diario**

| Paso | Qué pasa |
|---|---|
| Trigger | Programador diario. |
| Acción 1 | Agrupar pedidos por estado, modalidad y canal. |
| Acción 2 | Comparar pedidos elegibles con ventas de Loyverse. |
| Acción 3 | Leer la previsión vigente de PrediccionPedidos. |
| Acción 4 | Generar el Gmail con resumen, previsión de pedidos, diferencias, fallos y enlaces a vistas. |
| Error | Guardar reporte y alerta en cola; reenvío controlado sin duplicar. |

**Escenario E · Previsión de pedidos (lote)**

| Paso | Qué pasa |
|---|---|
| Trigger | Programación con la frecuencia definida en H5. |
| Acción 1 | Preparar el historial agregado de Pedidos y DetallePedido (sin datos personales). |
| Acción 2 | Puntuar con el modelo las fechas, franjas y SKU objetivo. |
| Validación | Verificar que el modelo mantiene mejora sobre la línea base simple (R11); si no, no se publica. |
| Acción 3 | Escribir PrediccionPedidos con `generado_en` y `version_modelo`, y marcar como no vigentes las previsiones anteriores. |
| Acción 4 | Registrar en Bitácora. |
| Error | Si falla, se conserva la última previsión con su fecha, marcada según vigencia, y se registra en Alertas. |

### 3.6 Prompts clave

**P1 · Instrucción de sistema (base)**

```text
Eres el asistente de pedidos de Panadería Tomasseli. Responde en español, con tono
cordial y conciso. Usa únicamente el menú, disponibilidad, horarios y reglas recibidos
por herramientas en esta conversación. No inventes productos, existencias, tiempos ni
condiciones. No confirmes una orden hasta que la validación determinística indique
disponible y el cliente acepte el resumen. Si la información falta, está vencida o es
ambigua, pregunta o deriva a una persona. No solicites datos que no sean necesarios
para gestionar el pedido.
```

**P2 · Salida estructurada esperada** (el LLM solo propone; n8n valida)

```json
{
  "intent": "consulta | pedido | cambio | cancelacion | solicitud_humana",
  "items": [
    { "sku": "string", "quantity": "integer > 0", "notes": "string" }
  ],
  "customer_name": "string",
  "fulfillment": "string (modalidad de entrega o recogida)",
  "address": "string (solo cuando aplique)",
  "requested_time": "string",
  "missing_fields": ["string"],
  "needs_human": "boolean",
  "response": "string"
}
```

Reglas de uso: para consultas se usa recuperación de Sheets con campos mínimos y marca de tiempo; n8n valida tipos, SKU elegibles, cantidades, privacidad y estado antes de escribir o responder. El LLM no genera ni modifica la previsión de pedidos: esta proviene solo del modelo de ML.

### 3.7 Seguridad, privacidad y operación

- Cuentas de servicio/propietario organizacional, MFA, permisos por rol y restricción de acceso a las hojas.
- Tokens/API keys en el almacén de credenciales de n8n o en propiedades protegidas con acceso restringido; nunca en celdas, prompts ni mensajes de WhatsApp.
- Limitar los datos de cliente a lo necesario; no incluir el teléfono completo en la comanda de cocina salvo necesidad aprobada.
- El entrenamiento y la previsión del modelo de ML usan datos agregados, sin datos personales de clientes.
- Definir aviso de privacidad, finalidad, retención y atención de solicitudes, con responsable de Tomasseli, antes del piloto.
- Registrar accesos y cambios, y rotar credenciales.

---

## 4. Implementación

### 4.1 Herramientas y cuentas

Google Sheets, Google Forms y Gmail; WhatsApp Business API; Loyverse TPV y API/conector disponible, con impresora de comandas en cocina; n8n como único motor de orquestación; proveedor LLM aprobado; herramienta de ML por definir en H5; repositorio controlado de prompts/configuración y tablero de alertas. Las versiones, permisos, endpoints, límites y mapeos deben quedar documentados en la configuración técnica del entorno.

### 4.2 Plan por hitos

| Hito | Tareas | Entregable verificable |
|---|---|---|
| H1 — Descubrimiento | Mapa validado AS-IS/TO-BE; reglas de domicilios, horarios/cortes, catálogo, responsables, línea base e inventario de accesos; verificación del historial de pedidos disponible. | Documento de descubrimiento validado. |
| H2 — Datos y menú | Libro Sheets con tablas, validaciones, protecciones, vistas y formularios para desayunos/almuerzos. | Libro Sheets y diccionario de datos. |
| H3 — Conversación IA | Webhook WhatsApp, prompt/versionado, recuperación de menú, esquema de extracción, confirmaciones y derivación humana. | Flujo conversacional probado. |
| H4 — Operación integrada | Automatizaciones de pedido en n8n, integración con Loyverse y comanda impresa en cocina, estados, bitácora, idempotencia, reintentos y alertas. | Escenarios B y C operativos. |
| H5 — Reportes y previsión | Cierre Gmail, cuadre pedido/TPV, vistas de excepción y rutina de contingencia; preparación de datos, entrenamiento y validación del modelo de previsión; comparación con la línea base; hoja PrediccionPedidos. | Escenarios D y E, rutina de contingencia, registro de cambios del modelo y recomendación de uso o no uso. |
| H6 — Piloto y salida | Pruebas aceptadas, capacitación por rol, manual operativo, monitoreo y acta de habilitación. | Acta de habilitación. |

### 4.3 Plan de pruebas

| # | Caso | Resultado esperado |
|---|---|---|
| P-01 | Alta/edición de menú por Form | Las reglas validan campos; el cambio queda auditado y visible al bot dentro del objetivo de actualización. |
| P-02 | Consulta de producto activo/agotado | El bot muestra solo datos vigentes; un agotado no se confirma y se ofrecen alternativas autorizadas. |
| P-03 | Pedido completo y claro | Resumen, aceptación explícita, un Pedido, comanda impresa desde Loyverse en cocina, sin mensajes a cocina por WhatsApp, y respuesta al cliente dentro del objetivo. |
| P-04 | Pedido incompleto/ambiguo | Pregunta solo los campos faltantes; no crea pedido confirmado antes de la aceptación. |
| P-05 | Repetición de webhook | Un pedido/comanda/venta como máximo; el evento duplicado queda reconocido. |
| P-06 | Error de WhatsApp/Sheets/LLM | Mensaje de espera o derivación, error trazado, reintento controlado; no se confirma falsamente. |
| P-07 | Falla de la comanda de cocina (Loyverse no la genera o no se imprime) | El pedido persiste con `pos_status` pendiente; alerta escalada, copia imprimible en la vista operativa y reintento sin duplicidad. |
| P-08 | Integración Loyverse | SKU correcto, referencia cruzada, estado POS registrado y comanda generada; las fallas van a conciliación. |
| P-09 | Cambio/cancelación después de confirmar | Historial y comanda de cocina actualizada según la capacidad validada; actualización POS conforme a la política. |
| P-10 | Cierre diario | El Gmail contiene totales por estado/canal, pedidos pendientes, diferencias frente a Loyverse, incidencias y previsión de pedidos. |
| P-11 | Permisos/seguridad | Los roles no autorizados no modifican el catálogo; los secretos no aparecen en logs ni mensajes. |
| P-12 | Carga/tiempo | Medición con tráfico piloto; objetivo de 10 s evaluado y la saturación genera cola, no pérdida silenciosa. |
| P-13 | Generación de la previsión con historial suficiente | PrediccionPedidos se llena por fecha, franja y SKU, con fecha de generación y versión del modelo, sin datos personales. |
| P-14 | Modelo vs. línea base simple | Se documenta la comparación; si el modelo no mejora la línea base, no se publica la previsión. |
| P-15 | Previsión vencida o historial insuficiente | No se muestra como vigente; queda registrada una alerta. |
| P-16 | Independencia de la previsión | La previsión no cambia disponibilidad, cupos ni la aceptación o confirmación de pedidos. |

### 4.4 Contingencias y continuidad (Plan B)

| Evento | Acción operativa |
|---|---|
| WhatsApp/API fuera de servicio | Activar canal alterno aprobado (teléfono/atención directa), registrar pedidos manuales con ID único, generar su comanda desde Loyverse y cargarlos a Sheets al restablecer; anunciar la demora. |
| Sheets inaccesible o datos vencidos | Pausar confirmaciones automáticas; usar copia/vista controlada con última sincronización solo para consulta; validar stock manualmente y regularizar cambios. |
| n8n o LLM caído | Pasar a atención humana; capturar el pedido con formulario alterno; reanudar eventos desde cola y conciliar antes de enviar. |
| Loyverse no sincroniza | Mantener el pedido confirmado y marcado «POS pendiente»; entregar a cocina una copia imprimible desde la vista operativa; registrar manualmente según procedimiento; conciliar IDs evitando doble registro. |
| Comanda sincronizada pero no impresa en cocina | Reimprimir desde Loyverse o imprimir el pedido desde la vista operativa; contactar al responsable y registrar la incidencia sin duplicar la venta. |
| Cierre Gmail falla | Guardar reporte y alerta en cola; revisión manual del cuadre; reenvío controlado sin duplicar notificación. |
| El modelo de ML no mejora la línea base o falla | No se publica la previsión o se conserva la última vigente con su fecha; administración y cocina planifican con el promedio histórico por día y franja. |

### 4.5 Criterios de salida y operación

La salida a producción requiere aprobación de catálogo/mapeo SKU, horarios y reglas; prueba de cada integración, incluida la emisión de la comanda impresa en cocina; responsables de excepciones; textos de privacidad; acceso protegido; procedimiento manual; recomendación de uso o no uso del modelo de previsión; y aceptación del piloto. Durante la operación se revisan diariamente excepciones y cuadre; semanalmente se evalúan exactitud, tiempos, disponibilidad de menú, causas de derivación y error de la previsión frente a la línea base. Toda modificación de reglas, prompts, mapeos o versión del modelo pasa por registro, validación y reversión documentada.

---

## Anexo A. Decisiones pendientes de validación

Confirmar:

- Si Loyverse admite crear/consultar ventas por API en el contexto de la cuenta, y si el pedido así registrado genera la comanda en la impresora de cocina.
- Contenido de la comanda (notas, modalidad, hora, alérgenos declarados) y cómo se refleja un cambio o cancelación en ella.
- Si cada plato tiene SKU/item ID.
- Método de descuento/registro de domicilios.
- Si el stock se controla por ingrediente, plato o conteo manual.
- Campos obligatorios de entrega.
- Horarios de desayuno/almuerzo y hora límite.
- Protocolo con el que cocina reporta los estados de preparación (en preparación, listo) sin canal de mensajería.
- Destinatarios del correo.
- Política de cancelación.
- Conservación y acceso a datos personales.
- Modalidad de despliegue y administración de n8n.
- Historial mínimo de pedidos disponible para entrenar el modelo de previsión.
- Granularidad de la previsión (producto, fecha, franja), frecuencia de actualización y destinatarios.
- Herramienta de ML y método de publicación en PrediccionPedidos.

Hasta esa validación, los componentes descritos son diseño objetivo y cualquier integración externa queda sujeta a prueba técnica.
