# Proyecto 12 · Del chat a la comanda

**Ficha de especificación del proyecto** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📄 [Descargar esta ficha en PDF](proyecto-12-del-chat-a-la-comanda.pdf) · 🧭 [Ficha técnica: RAG, Spec Kit y Google Cloud](ficha-tecnica.md) · 🗂️ [Volver al índice de proyectos](../README.md)

| Ficha técnica | |
|---|---|
| **Organización** | Panadería Tomasseli |
| **Sector** | Alimentos y restaurantes |
| **Dificultad** | ★★★ |
| **Machine Learning** | Regresión sobre datos tabulares (previsión de pedidos); herramienta a confirmar en H4 |
| **Conexión modelo–flujo** | Lote |
| **Orquestación** | n8n, como único orquestador |
| **Canales y sistemas** | WhatsApp Business API (solo órdenes de clientes) · Loyverse TPV (venta y comanda impresa en cocina) · Google Sheets y Forms · Gmail |
| **Carpeta de trabajo del equipo** | `bitacora/proyecto-<nombre-equipo>/` |

> **Origen y alcance.** Esta ficha parte de la especificación funcional y técnica v1.2 de Panadería Tomasseli (18 Oct 2026). A diferencia de las fichas 1 a 11, **no trae cifras de línea base**: medirlas es una tarea de H1, y las metas de la sección 1.7 se recalibran con esa línea base y el piloto. Por decisión de la especificación, la ficha **no incluye contenido económico**.

> **Nota sobre los laboratorios.** Hoy están publicados los laboratorios 1 a 9 y 11 a 13. La ficha «¿sí requiere ML?» (sección 2.5) es el producto del [Laboratorio 9](../../src/modulo_2_construir/laboratorio_9/). La preparación, el entrenamiento y la validación del modelo (H4) siguen los laboratorios [11](../../src/modulo_3_experimentar/laboratorio_11/estudiante/), [12](../../src/modulo_3_experimentar/laboratorio_12/estudiante/) y [13](../../src/modulo_3_experimentar/laboratorio_13/estudiante/), y el ejemplo de [regresión en Python](../../ejemplos/ml/01_regresion/). La fase de automatización (semanas 11 a 14) se basa en el tema y el producto que la hoja **IA** del plan define para cada sesión.

## Contenido

1. [Necesidades](#1-necesidades): contexto, problema, actores, requisitos funcionales y no funcionales, restricciones e indicadores de éxito.
2. [Entendimiento](#2-entendimiento): proceso actual y propuesto, causas raíz, papel de la IA, ficha «¿sí requiere ML?», supuestos y riesgos.
3. [Estructuración](#3-estructuración): arquitectura funcional, modelo de datos, reglas de negocio, diseño del modelo de ML, flujo automatizado, prompts y seguridad.
4. [Implementación](#4-implementación): herramientas, plan por hitos, plan de pruebas, guion del Demo Day, plan B y criterios de salida.
5. [Fuentes de datos](#5-fuentes-de-datos): datasets recomendados, fuentes de Colombia, portales para buscar más y lista de verificación para elegir los datos.
6. [Anexo A · Decisiones pendientes de validación](#anexo-a--decisiones-pendientes-de-validación).
7. [Anexo B · Marco común del curso](#anexo-b--marco-común-del-curso): calendario de hitos, entrega en el repositorio, conexión modelo–flujo y principios.

---

## 1. Necesidades

### 1.1 Contexto

Panadería Tomasseli recibe pedidos por **WhatsApp** y debe coordinarlos con la disponibilidad del menú (desayunos fijos y almuerzos diarios o semanales), la operación de cocina, el inventario y el registro de ventas en **Loyverse TPV**. WhatsApp se usa **solo para las órdenes de los clientes**; la comunicación con cocina es directa, mediante la **comanda impresa desde Loyverse**.

La solución organiza el dato operativo en **Google Sheets** y conecta los sistemas con automatizaciones en **n8n**. La IA generativa facilita la conversación, pero las **reglas determinísticas** controlan la disponibilidad, la confirmación y el registro. Un modelo de **Machine Learning** predice las órdenes de los clientes a partir de las tendencias de los pedidos, como apoyo informativo a la planeación.

### 1.2 Problema

La actualización manual y la circulación de la información por canales separados causan:

| Síntoma | Línea base |
|---|---|
| Respuestas al cliente con opciones agotadas | Por medir en H1 |
| Reprocesos al transcribir pedidos | Por medir en H1 |
| Demoras en cocina | Por medir en H1 |
| Diferencias entre lo solicitado, lo preparado y lo registrado | Por medir en H1 |
| Ninguna estimación de los pedidos esperados para anticipar la preparación | Por medir en H1 |

### 1.3 Actores y necesidades

| Actor | Necesita | Canal y contexto |
|---|---|---|
| Cliente | Consultar el menú y la disponibilidad vigente, resolver dudas, especificar el pedido, la entrega o recogida, y recibir una confirmación clara | WhatsApp |
| Administración | Mantener catálogo, horarios, estados, pedidos y cierres; revisar excepciones; recibir un resumen diario; consultar la previsión de pedidos | Google Sheets, Forms y Gmail |
| Cocina | Recibir los pedidos confirmados en una comanda impresa legible; reportar agotados y cambios; consultar la previsión de pedidos | Comanda impresa desde Loyverse; Google Forms y vista operativa desde el móvil |
| Atención / operador | Consultar el historial y hacerse cargo de conversaciones ambiguas, cambios especiales o incidencias | Vista operativa de pedidos y conversaciones |
| Integraciones | Mantener la consistencia entre Sheets, WhatsApp Business API y Loyverse, con trazabilidad y reintentos | Sin interfaz propia |

### 1.4 Requisitos funcionales

| Código | Requisito |
|---|---|
| RF1 | Publicar una fuente de verdad para el menú fijo de desayunos, el menú diario o semanal de almuerzos y la disponibilidad por producto. |
| RF2 | Permitir que administración y cocina actualicen el menú con un Google Form validado, sin editar directamente las celdas operativas. |
| RF3 | Consultar el menú activo y la disponibilidad antes de ofrecer, aceptar o confirmar un producto. |
| RF4 | Atender conversaciones en WhatsApp Business API: comprender la intención, resolver consultas y capturar el pedido de forma estructurada. WhatsApp solo canaliza las órdenes de los clientes. |
| RF5 | Pedir los datos faltantes (productos, cantidades, nombre, modalidad, dirección cuando aplique, hora y observaciones) antes de confirmar. |
| RF6 | Registrar cada pedido confirmado **una sola vez** en el consolidado de Sheets, con identificador, fecha, canal y estado. |
| RF7 | Comunicar a cocina el pedido confirmado mediante la comanda impresa desde Loyverse, sin un canal de mensajería adicional; los agotados y cambios de menú se reportan por Google Forms. |
| RF8 | Sincronizar el pedido o la venta con Loyverse TPV, con referencia cruzada y manejo de fallas. |
| RF9 | Consolidar cada día pedidos, ventas, estados, incidencias y diferencias, y enviar el resumen a administración por Gmail. |
| RF10 | Permitir la intervención humana, la pausa del bot y el seguimiento de la conversación sin perder contexto ni duplicar pedidos. |
| RF11 | Mantener una bitácora de cambios de menú, transiciones de pedido, llamadas a integraciones y errores. |
| RF12 | Facilitar la conciliación de ventas y pedidos, incluido el estado de sincronización con Loyverse. |
| RF13 | Predecir las órdenes de los clientes (cantidad esperada por producto, fecha y franja) a partir de las tendencias del historial, y ponerla a disposición de administración y cocina como apoyo informativo, incluida en el resumen diario. |

### 1.5 Requisitos no funcionales

| Código | Requisito |
|---|---|
| RNF1 | Respuesta automática en **10 segundos o menos** en condiciones normales; si una dependencia excede el umbral, se informa al usuario y el mensaje pasa a cola con reintento. |
| RNF2 | Disponibilidad objetivo del 99 % mensual del flujo de recepción, sin contar la indisponibilidad de proveedores externos. |
| RNF3 | Sin duplicados: idempotencia por identificador de mensaje o pedido, reintentos con espera incremental y cola de errores. |
| RNF4 | Mínimo privilegio, cuentas institucionales, credenciales en un gestor seguro y registro de cambios. |
| RNF5 | Proteger los datos personales (Ley 1581): guardar solo lo necesario para gestionar el pedido y aplicar la política de conservación aprobada. |
| RNF6 | Trazabilidad del estado: recibido, validado, confirmado, enviado a cocina, en preparación, listo, entregado/cerrado, cancelado o con error. |
| RNF7 | Formularios usables desde el móvil; comandas concisas y legibles; pedidos imprimibles desde la vista operativa en caso de contingencia. |
| RNF8 | Los cambios de menú se reflejan en las respuestas del bot en **1 minuto o menos**. |
| RNF9 | Cada previsión queda registrada con fecha de generación y versión del modelo; una previsión vencida no se muestra como vigente. El entrenamiento y la previsión usan datos agregados, **sin teléfono, nombre ni dirección** de clientes. |

### 1.6 Restricciones

- Google Sheets es el repositorio operativo; Google Forms, el mecanismo de carga; Gmail, el canal de reporte.
- WhatsApp Business API es el canal con los clientes, **solo para sus órdenes**; no se usa para hablar con cocina.
- Loyverse TPV se conserva como punto de venta y como origen de la comanda impresa. La integración depende de permisos, de la capacidad de la API y de que el registro del pedido genere la comanda en cocina.
- n8n es el único orquestador.
- Sheets no se trata como un inventario transaccional de alta concurrencia.
- La previsión de pedidos depende del historial disponible y es **solo informativa**.

### 1.7 Indicadores de éxito

| Indicador | Línea base | Meta | Cómo se mide |
|---|---|---|---|
| Tiempo de respuesta | Por medir | ≥ 90 % de las consultas automatizables respondidas en ≤ 10 s | Marcas de tiempo en Bitacora |
| Exactitud del pedido | Por medir | ≥ 98 % de los pedidos confirmados sin corrección manual atribuible a la captura | Pedidos corregidos frente a confirmados |
| Disponibilidad del menú | Por medir | 100 % de los pedidos aceptados vinculados a una opción activa y disponible al confirmar | `disponibilidad_validada_en` en DetallePedido |
| Integración con Loyverse | Por medir | ≥ 98 % de los pedidos elegibles sincronizados o señalados en la cola de excepción | `pos_status` en Pedidos |
| Comanda de cocina | Por medir | 100 % de los pedidos confirmados generan comanda impresa o una incidencia visible y recuperable | `pos_status` en Pedidos y hoja Alertas |
| Cierre diario | Por medir | Resumen enviado y cuadre revisable en cada jornada | Registro del envío en Gmail |
| Previsión de pedidos | Promedio histórico por día de la semana y franja | Error de pronóstico menor que el de la línea base; valor objetivo por calibrar en el piloto | Previsión frente a pedidos reales en el periodo de prueba |

> Las metas son criterios iniciales de aceptación y se recalibran con la línea base de H1 y el piloto.

## 2. Entendimiento

### 2.1 AS-IS

1. El cliente pregunta por WhatsApp o pide un producto.
2. El equipo consulta el menú y la disponibilidad en información dispersa o de memoria. ❌ *Aquí se ofrecen opciones agotadas.*
3. El pedido se interpreta y se transcribe a mano para cocina y para el TPV. ❌ *Aquí nacen los reprocesos y las diferencias.*
4. Cocina prepara; los cambios y agotados no siempre se comunican a tiempo. ❌ *Aquí se generan las demoras.*
5. La venta, la entrega y el cierre se registran en sistemas separados y se concilian al final del día.

### 2.2 Causas raíz

| Causa raíz | Cómo se aborda |
|---|---|
| Menú y existencias sin una fuente única | Se centralizan menú y disponibilidad, con un responsable de actualización |
| Transcripción manual entre conversación, cocina y TPV | Una entidad Pedido con estados y referencia cruzada; la comanda sale de Loyverse sin retranscribir |
| Lenguaje libre y variable del cliente | Extracción asistida por LLM, seguida de validación estructurada |
| Cambios que no se comunican en tiempo real | Un evento de cambio actualiza al bot y alerta a operación |
| Falta de conciliación diaria | Reporte consolidado y cola de excepciones |
| Falta de anticipación de los pedidos esperados | Modelo de ML que predice las órdenes a partir de las tendencias históricas |

### 2.3 TO-BE

Administración publica el menú en Sheets y cocina lo actualiza por Form → el cliente escribe por WhatsApp → n8n recupera el menú vigente y el LLM clasifica la intención y extrae el pedido → reglas validan datos y disponibilidad → el cliente acepta el resumen → el pedido se registra una sola vez como «confirmado» → n8n lo sincroniza con Loyverse, que imprime la comanda en cocina → cocina u operador actualizan el estado → Gmail envía el cierre diario con la previsión. Aparte, por lote, el modelo de ML escribe la previsión en la hoja PrediccionPedidos.

### 2.4 ¿Dónde aporta la IA?

| Tarea | Quién | Por qué / límite |
|---|---|---|
| Clasificar el mensaje (consulta, pedido, cambio, cancelación, solicitud humana) y extraer productos, cantidades y notas | IA generativa (LLM) | El lenguaje del cliente es libre. Salida en JSON validado |
| Redactar la respuesta natural | IA generativa (LLM) | Solo con datos del menú activo, reglas aprobadas y disponibilidad consultada |
| Detectar campos ausentes o ambiguos y preguntar | IA generativa (LLM) | Sin inferir direcciones, cantidades ni sustituciones |
| Presentar el resumen del pedido para confirmar | IA generativa (LLM) | Sobre datos ya validados por reglas |
| Predecir las órdenes según las tendencias de los pedidos | Modelo de ML | Salida informativa: no confirma ni limita pedidos |
| Validar disponibilidad, esquema, SKU, cantidades y estado | Reglas (sin IA) | Son controles exactos que hace n8n |
| Registrar, sincronizar con Loyverse, conciliar y cerrar | Reglas y n8n | Ejecución determinística con idempotencia |
| Atender casos ambiguos, cambios especiales e incidencias | **Operador** | La IA deriva cuando falta información o hay ambigüedad |
| Decidir cuánto preparar | **Administración y cocina** | El modelo solo orienta |

**Límite de autoridad.** El LLM no modifica el inventario, no crea ventas en el TPV, no confirma disponibilidad «de memoria» ni ejecuta acciones fuera de las herramientas autorizadas. El modelo de ML no modifica inventario, cupos ni disponibilidad, no acepta ni rechaza pedidos y no dispara acciones sobre clientes.

### 2.5 Ficha "¿sí requiere ML?"

| Pregunta | Respuesta |
|---|---|
| ¿Qué se predice? | La cantidad esperada de pedidos por producto (SKU), fecha y franja |
| ¿Con qué datos? | Historial de Pedidos y DetallePedido: fecha, franja, SKU, cantidad, modalidad, canal y estado; cantidades de periodos previos como medida de tendencia |
| ¿Criterio de éxito? | Que el error de pronóstico (previsión frente a pedidos reales) sea menor que el de la línea base; el valor objetivo se calibra en el piloto |
| ¿Alternativa? | Sí: el promedio histórico por día de la semana y franja. Si el modelo no lo mejora, se recomienda no usarlo |
| Conclusión | Se usa ML para la previsión, de forma informativa. La recomendación de uso o no uso es un entregable de H4 |

### 2.6 Supuestos y riesgos

**Supuestos por validar en H1:** catálogo con SKU; horarios, zonas de entrega, reglas de domicilios, medios de pago, política de cancelación y responsables de cada bandeja; correspondencia entre el menú y los productos de Loyverse; que el registro del pedido en Loyverse genere la comanda impresa; volumen simultáneo; cuentas y accesos de API; historial de pedidos suficiente para entrenar la previsión.

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Menú desactualizado | Se promete un producto agotado | Form con vigencia, responsable, expiración automática y recarga antes de confirmar |
| Falla de una API o proveedor | Pedido sin comanda o sin registro en el TPV | Cola, reintento, alerta, consola de excepciones y pedido imprimible desde la vista operativa |
| Webhook repetido o reintento | Doble preparación o doble venta | Idempotencia e identificador único antes de repetir una escritura |
| El LLM inventa o malinterpreta | Pedido incorrecto | Contexto acotado, esquema validado, confirmación explícita y derivación a humano |
| Permisos y datos personales | Exposición o cambio no autorizado | Mínimo privilegio, acceso por rol, retención definida y bitácora (Ley 1581) |
| Caída de Sheets o límites de cuota | El bot no puede verificar disponibilidad | Caché de lectura con marca de tiempo; no confirmar con caché vencida; contingencia manual |
| Comanda no generada o no impresa | Cocina no ve el pedido | `pos_status`, tablero de pendientes, alerta al responsable y copia impresa |
| Historial insuficiente o previsión errónea | Preparación mal dimensionada | Uso solo informativo, comparación obligatoria con la línea base, fecha y versión, y decisión humana |

> **Fuga de información en el modelo.** Las variables que solo se conocen después del día objetivo (por ejemplo, el estado final del pedido o las cantidades del mismo día) no pueden entrar como variables de entrada. La separación entre entrenamiento y prueba debe ser **cronológica**, nunca aleatoria.

## 3. Estructuración

### 3.1 Arquitectura funcional

| Componente | En este proyecto |
|---|---|
| **Datos** | Sheets: MenuDesayunos, MenuAlmuerzos, Productos, Pedidos, DetallePedido, Alertas, Bitacora y PrediccionPedidos |
| **Interfaz** | Chat de WhatsApp para el cliente; Google Forms de alta, cambio y agotado para administración y cocina; vista operativa de pedidos (imprimible) para operador y cocina; comanda impresa desde Loyverse |
| **Reglas** | R1 a R12: vigencia y disponibilidad, datos mínimos, idempotencia, separación de estados y previsión solo informativa |
| **Automatizaciones** | n8n: A (actualización de menú), B (conversación y pedido con LLM), C (cocina y Loyverse), D (cierre diario por Gmail), E (previsión por lote) |

```text
Cliente WhatsApp (solo órdenes)
  -> WhatsApp Business API / webhook
  -> n8n: normalización, idempotencia, reglas y bitácora
       -> menú y disponibilidad en Google Sheets
       -> LLM con contexto acotado y salida JSON
       -> validación determinística y confirmación
       -> Pedido consolidado en Sheets
       -> Loyverse TPV -> comanda impresa en cocina
       -> Gmail: resumen diario (incluye la previsión)

Administración / Cocina -> Google Forms -> validación -> Sheets -> bot actualizado

Historial de Pedidos (Sheets) -> modelo de ML (lote) -> PrediccionPedidos -> vistas y Gmail
```

### 3.2 Modelo de datos

| Hoja | Campos principales |
|---|---|
| MenuDesayunos | `menu_id`, `sku`, `nombre`, `descripcion`, `categoria`, `disponible`, `cupo`, `alergenos_declarados`, `vigencia_desde`, `vigencia_hasta`, `actualizado_por`, `actualizado_en` |
| MenuAlmuerzos | `menu_id`, `fecha`, `sku`, `nombre`, `componentes`, `descripcion`, `cupo`, `disponible`, `hora_corte`, `alergenos_declarados`, `responsable`, `vigencia` (una fila por producto y fecha) |
| Productos | `sku`, `nombre_loyverse`, `loyverse_item_id`, `unidad`, `activo`, `politica_stock`, `actualizado_en` |
| Pedidos | `pedido_id`, `mensaje_origen_id`, `fecha_hora`, `telefono_normalizado`, `nombre`, `canal`, `modalidad`, `direccion`, `franja_solicitada`, `estado`, `notas`, `aviso_privacidad`, `pos_status`, `loyverse_sale_id`, `ultima_actualizacion` |
| DetallePedido | `pedido_id`, `linea`, `sku`, `nombre_snapshot`, `cantidad`, `notas_linea`, `disponibilidad_validada_en` |
| Alertas | `alerta_id`, `tipo`, `severidad`, `pedido_id`, `origen`, `mensaje`, `creada_en`, `estado`, `responsable`, `resuelta_en` |
| Bitacora | `evento_id`, `entidad`, `entidad_id`, `accion`, `actor_sistema`, `timestamp`, `resultado`, `correlation_id`, `detalle_tecnico` (sin secretos) |
| PrediccionPedidos | `prediccion_id`, `fecha_objetivo`, `franja`, `sku`, `cantidad_prevista`, `generado_en`, `version_modelo`, `vigente` (solo datos agregados) |

Se protegen los rangos de catálogo y las fórmulas, se validan enumeraciones, fechas y cantidades, y se usan identificadores estables. Si la concurrencia o el volumen superan el umbral acordado, el registro de pedidos se migra a una base de datos y Sheets queda como vista administrativa.

### 3.3 Reglas de negocio

| Código | Regla | Dónde se implementa |
|---|---|---|
| R1 | Solo se ofrecen productos activos y vigentes para la fecha y franja; la disponibilidad se verifica al iniciar y al confirmar | n8n, consulta a los menús |
| R2 | Un producto con disponibilidad desconocida no es confirmable: se pregunta al operador | n8n y derivación a humano |
| R3 | El pedido pasa a «confirmado» solo con datos mínimos, disponibilidad validada y resumen aceptado por el cliente | Validación determinística |
| R4 | Cantidades positivas; opciones, sustituciones, horarios y zonas se rigen por el catálogo | Validación de esquema |
| R5 | Clave idempotente = canal + identificador del mensaje o evento + operación; un pedido repetido no genera doble comanda ni doble venta | n8n (deduplicación) |
| R6 | Cancelaciones y cambios conservan el historial; si ya hubo sincronización, se comunican a cocina por la comanda de Loyverse | Bitacora y Loyverse |
| R7 | Toda operación fallida queda en Alertas con responsable y acción pendiente | Hoja Alertas |
| R8 | El estado del TPV (`pos_status`) se separa del estado de cocina (`estado`) | Hoja Pedidos |
| R9 | Los menús con vigencia vencida dejan de ser elegibles; el menú de desayunos conserva el catálogo y actualiza su disponibilidad diaria | Vigencias y expiración |
| R10 | La previsión es informativa: no modifica disponibilidad, cupos ni inventario, ni interviene en aceptar o rechazar pedidos | Separación de PrediccionPedidos |
| R11 | La previsión se publica solo si el modelo mejora la línea base; lleva fecha y versión, y la vencida no se muestra como vigente | Escenario E y campo `vigente` |
| R12 | WhatsApp solo canaliza las órdenes de los clientes; cocina se comunica solo por la comanda de Loyverse | Diseño de integración |

### 3.4 Diseño del modelo de ML

| Elemento | Decisión |
|---|---|
| Objetivo | Predecir la cantidad pedida por SKU, fecha y franja a partir de las tendencias de los pedidos |
| Dataset | Historial de Pedidos y DetallePedido de Tomasseli, agregado por fecha, franja y SKU, sin pedidos cancelados ni con error. Si en H1 el historial no alcanza, se practica con un dataset público de ventas de panadería (por ejemplo, *French Bakery Daily Sales* en Kaggle, verificando licencia y columnas) y el modelo se reentrena con los datos propios cuando existan |
| Variable objetivo | `cantidad_pedida` por SKU, fecha y franja |
| Variables de entrada | Día de la semana, franja, SKU, categoría, modalidad, canal y cantidades de periodos previos (tendencia) |
| Preparación | Revisar nulos y duplicados; agregar el detalle; separar entrenamiento y prueba **en orden cronológico** (por ejemplo, 70/30); excluir variables conocidas solo después del hecho y todo dato personal |
| Algoritmos | Regresión lineal y árbol de regresión (Orange o cuaderno de Python, a confirmar en H4) |
| Métrica principal | Error de pronóstico, por ejemplo el error absoluto medio (MAE) por SKU y franja |
| Comparación obligatoria | Modelo frente a la línea base: promedio histórico por día de la semana y franja |
| Puntuación por lote | Se puntúan las fechas objetivo con la frecuencia acordada y el resultado se escribe en PrediccionPedidos |
| Uso de la salida | Vistas de administración y cocina, y sección de previsión en el resumen diario |
| Recomendación | Si el modelo no mejora la línea base o el historial no alcanza, no se publica y se documenta como hallazgo |

**Motor LLM (comprensión y atención).** LLM de un proveedor aprobado, invocado desde n8n; no se entrena un modelo propio. El contexto se recupera de Sheets con campos mínimos y marca de tiempo. El LLM solo **propone** un JSON; n8n valida tipos, SKU elegibles, cantidades, privacidad y estado. Se registra la versión del prompt, el modelo y el `correlation_id`, y se minimiza la conservación del texto conversacional. Si el LLM o n8n fallan, la alternativa es atención humana con un formulario alterno de captura.

### 3.5 Diseño del flujo automatizado

- **A · Actualización de menú.** *Trigger:* envío del Google Form de alta, cambio o agotado → validar campos, fecha, SKU y responsable → actualizar las filas vigentes → registrar en Bitacora → refrescar la caché de lectura (≤ 1 minuto, RNF8) → confirmar la publicación o alertar el error.
- **B · Conversación y pedido.** *Trigger:* webhook de WhatsApp → deduplicar el mensaje (R5) → recuperar menú y disponibilidad → **paso de IA** (P1 + P2): clasificar la intención y extraer el pedido en JSON → validar esquema y reglas → si faltan datos, preguntarlos; si hay ambigüedad o solicitud humana, **derivar al operador** → al confirmar, revalidar disponibilidad y mostrar el resumen → tras la aceptación explícita, escribir Pedido y DetallePedido → responder la confirmación.
- **C · Cocina y Loyverse.** *Trigger:* pedido confirmado o cambiado → mapear SKU a `loyverse_item_id` → registrar la transacción en Loyverse, que imprime la comanda (ID, hora, modalidad, líneas y notas) → guardar `loyverse_sale_id` y `pos_status` → registrar los estados de preparación y entrega que reporta cocina u operador → avisar al cliente si corresponde.
- **D · Cierre diario.** *Trigger:* programado → agrupar pedidos por estado, modalidad y canal → comparar con las ventas de Loyverse → leer la previsión vigente → enviar por Gmail el resumen con diferencias, fallos, previsión y enlaces a las vistas.
- **E · Previsión por lote.** *Trigger:* programado con la frecuencia acordada → preparar el historial agregado sin datos personales → puntuar con el modelo → verificar que mejora la línea base (R11) → escribir PrediccionPedidos con `generado_en` y `version_modelo` y marcar las anteriores como no vigentes → registrar en Bitacora.
- **Errores.** Falla de Loyverse → reintento idempotente; si persiste, `pos_status` queda «pendiente», se crea una alerta con responsable y el pedido queda imprimible en la vista operativa. Falla del cierre → reporte y alerta en cola, reenvío sin duplicar. Falla de la previsión → se conserva la última con su fecha y se registra en Alertas.
- **Punto de control humano.** El operador atiende toda derivación del escenario B; administración y cocina deciden cuánto preparar con la previsión.

### 3.6 Prompts clave

#### P1 · Instrucción de sistema

```text
Eres el asistente de pedidos de Panadería Tomasseli. Responde en español, con tono
cordial y conciso. Usa únicamente el menú, disponibilidad, horarios y reglas recibidos
por herramientas en esta conversación. No inventes productos, existencias, tiempos ni
condiciones. No confirmes una orden hasta que la validación determinística indique
disponible y el cliente acepte el resumen. Si la información falta, está vencida o es
ambigua, pregunta o deriva a una persona. No solicites datos que no sean necesarios
para gestionar el pedido.
```

#### P2 · Salida estructurada (el LLM propone; n8n valida)

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

El LLM no genera ni modifica la previsión de pedidos: esta proviene solo del modelo de ML.

### 3.7 Seguridad, privacidad y operación

- Cuentas de servicio con propietario organizacional, MFA, permisos por rol y acceso restringido a las hojas.
- Tokens y llaves de API en el almacén de credenciales de n8n; nunca en celdas, prompts ni mensajes de WhatsApp.
- Datos del cliente limitados a lo necesario; el teléfono completo no aparece en la comanda salvo necesidad aprobada.
- El entrenamiento y la previsión usan datos agregados, sin datos personales.
- Aviso de privacidad, finalidad, retención y atención de solicitudes definidos con un responsable de Tomasseli antes del piloto (Ley 1581).
- Registro de accesos y cambios, y rotación de credenciales.

## 4. Implementación

### 4.1 Herramientas

LLM; Gamma o Canva y v0.dev para la presentación y el prototipo; Google Sheets, Forms y Gmail; WhatsApp Business API (o su entorno de prueba); Loyverse TPV con su API y la impresora de comandas; n8n como único orquestador; Orange o cuaderno de Python para el modelo de previsión; repositorio con prompts, configuración y registro de cambios.

### 4.2 Plan por hitos

| Hito | Tareas | Entregable |
|---|---|---|
| H1 | AS-IS y TO-BE validados con Tomasseli; reglas de domicilios, horarios y cortes; catálogo y responsables; **medición de la línea base**; inventario de accesos; verificación del historial de pedidos; P1 v1 | Documento de descubrimiento y biblioteca de prompts |
| H2 | Diccionario de datos y reglas R1–R12 trazables a los requisitos; esquema P2 probado con 10 mensajes reales o simulados, verificando cada producto contra el menú | Documento base + tabla de verificación |
| H3 | Presentación ejecutiva; prototipo de la vista operativa; **MVP sin código**: libro de Sheets con validaciones y protecciones, y Forms de desayunos, almuerzos y agotados | PDF, `index.html`, libro de Sheets y capturas |
| H4 | Preparación del historial agregado, separación cronológica, regresión y árbol de regresión, comparación con la línea base y hoja PrediccionPedidos | Dataset, modelo, registro de cambios y recomendación de uso o no uso |
| H5 | Escenarios A–E en n8n: webhook de WhatsApp, paso de IA, Loyverse con comanda impresa, idempotencia, reintentos, alertas y cierre por Gmail | Flujos exportados de n8n, diagrama y pruebas P-01 a P-16 |
| H6 | Piloto, capacitación por rol, manual operativo y guion | Demo y acta de habilitación |

### 4.3 Plan de pruebas

| # | Caso | Resultado esperado |
|---|---|---|
| P-01 | Alta o edición de menú por Form | Campos validados, cambio auditado y visible al bot en ≤ 1 minuto |
| P-02 | Consulta de producto activo y agotado | El bot muestra solo datos vigentes; el agotado no se confirma y se ofrecen alternativas autorizadas |
| P-03 | Pedido completo y claro | Resumen, aceptación, un Pedido, comanda impresa desde Loyverse, ningún mensaje a cocina por WhatsApp y respuesta dentro del objetivo |
| P-04 | Pedido incompleto o ambiguo | Pregunta solo los campos faltantes; no confirma antes de la aceptación |
| P-05 | Webhook repetido | Como máximo un pedido, una comanda y una venta; el duplicado queda reconocido |
| P-06 | Error de WhatsApp, Sheets o LLM | Mensaje de espera o derivación, error trazado y reintento; nunca una confirmación falsa |
| P-07 | Loyverse no genera o no imprime la comanda | Pedido con `pos_status` pendiente, alerta escalada, copia imprimible y reintento sin duplicar |
| P-08 | Integración con Loyverse | SKU correcto, referencia cruzada, estado registrado y comanda generada |
| P-09 | Cambio o cancelación después de confirmar | Historial conservado y comanda actualizada según la capacidad validada |
| P-10 | Cierre diario | El correo trae totales por estado y canal, pendientes, diferencias con Loyverse, incidencias y previsión |
| P-11 | Permisos y seguridad | Roles no autorizados no cambian el catálogo; los secretos no aparecen en logs ni mensajes |
| P-12 | Carga y tiempo | Objetivo de 10 s medido con tráfico piloto; la saturación genera cola, no pérdida silenciosa |
| P-13 | Previsión con historial suficiente | PrediccionPedidos se llena por fecha, franja y SKU, con fecha y versión, sin datos personales |
| P-14 | Modelo frente a línea base | Comparación documentada; si no mejora, no se publica |
| P-15 | Previsión vencida o historial insuficiente | No se muestra como vigente y queda una alerta |
| P-16 | Independencia de la previsión | No cambia disponibilidad, cupos ni la aceptación de pedidos |

### 4.4 Guion del Demo Day

1. El problema: opciones agotadas, transcripciones y diferencias, con la línea base medida en H1.
2. En vivo: cocina marca un agotado por Form → el bot deja de ofrecerlo en menos de un minuto.
3. En vivo: un pedido por WhatsApp con un dato faltante → pregunta → resumen → confirmación → comanda impresa desde Loyverse.
4. El mismo webhook enviado dos veces → un solo pedido; una falla simulada de Loyverse → alerta y pedido imprimible.
5. El modelo: previsión frente a línea base, y la recomendación de uso o no uso.
6. El cierre diario en Gmail y los límites de la IA: qué propone, qué valida n8n y qué decide la persona.

### 4.5 Plan B

| Evento | Acción |
|---|---|
| WhatsApp o su API fuera de servicio | Canal alterno aprobado (teléfono o atención directa); pedidos manuales con ID único, comanda desde Loyverse y carga a Sheets al restablecer |
| Sheets inaccesible o datos vencidos | Pausar confirmaciones automáticas; consultar la última copia sincronizada; validar existencias a mano |
| n8n o el LLM caídos | Atención humana y formulario alterno de captura; reanudar desde la cola y conciliar antes de reenviar |
| Loyverse no sincroniza | Pedido confirmado y marcado «POS pendiente»; copia impresa para cocina; registro manual y conciliación de IDs sin doble venta |
| Comanda sincronizada pero no impresa | Reimprimir desde Loyverse o desde la vista operativa y registrar la incidencia |
| Falla el cierre por Gmail | Reporte y alerta en cola; cuadre manual; reenvío sin duplicar |
| La API de Loyverse no está disponible a tiempo para el Demo Day | Se demuestra con una hoja que simula el TPV y la comanda en PDF, y se documenta la integración pendiente |
| El modelo no mejora la línea base o falla | No se publica la previsión; se planifica con el promedio histórico por día y franja, y se muestra esa evidencia |

### 4.6 Criterios de salida y operación

La salida a producción requiere: catálogo y mapeo de SKU aprobados; horarios y reglas aprobados; cada integración probada, incluida la comanda impresa; responsables de excepciones; textos de privacidad; acceso protegido; procedimiento manual; recomendación de uso o no uso del modelo; y aceptación del piloto. En operación, las excepciones y el cuadre se revisan a diario; la exactitud, los tiempos, la disponibilidad del menú, las causas de derivación y el error de la previsión frente a la línea base, cada semana. Todo cambio de reglas, prompts, mapeos o versión del modelo se registra, se valida y tiene reversión documentada.

---

## 5. Fuentes de datos

Enlaces para conseguir datos mientras el historial propio de Tomasseli no alcanza (sección 3.4). El modelo de previsión necesita **ventas por producto, fecha y franja**; el motor LLM necesita **mensajes de pedido** para probar la extracción. Cuando existan los datos de Loyverse y de las hojas Pedidos y DetallePedido, esos son la fuente principal y estos datasets quedan como práctica.

### 5.1 Datasets recomendados para la previsión de pedidos

| | Dataset | Qué trae | Uso en el proyecto | Enlace |
|---|---|---|---|---|
| ⭐ | **French Bakery Daily Sales** · Kaggle | ~234.000 transacciones de una panadería francesa (ene 2021 – sep 2022): fecha, **hora**, ticket, artículo, cantidad y precio unitario | Dataset de práctica sugerido en la sección 3.4. La hora permite construir la **franja** (desayuno, almuerzo, tarde) y el artículo hace de SKU. Agregue por fecha, franja y producto | [kaggle.com/datasets/matthieugimbert/french-bakery-daily-sales](https://www.kaggle.com/datasets/matthieugimbert/french-bakery-daily-sales) |
| | **Bakery (The Bread Basket)** · Kaggle | ~20.500 líneas de una panadería de Edimburgo: transacción, artículo, fecha y hora, franja del día | Alternativa más pequeña. Ya trae la franja (*morning*, *afternoon*…), útil para probar el modelo rápido en Orange | [kaggle.com/datasets/akashdeepkuila/bakery](https://www.kaggle.com/datasets/akashdeepkuila/bakery) |
| | **Store Sales – Time Series Forecasting** (Corporación Favorita) · Kaggle | Ventas diarias de supermercados de **Ecuador** por familia de producto (incluye `BREAD/BAKERY`), con festivos y promociones | Ejemplo latinoamericano para estudiar el efecto de festivos y días de la semana. Filtre la familia `BREAD/BAKERY` y una tienda | [kaggle.com/competitions/store-sales-time-series-forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) |

### 5.2 Datos para el motor LLM (conversación de pedidos)

| Fuente | Qué trae | Uso en el proyecto | Enlace |
|---|---|---|---|
| **MASSIVE** (Amazon) · configuración `es-ES` | ~16.500 frases en español etiquetadas con 60 intenciones, entre ellas `takeaway_order` y `takeaway_query` | Inspirar y probar mensajes de pedido y de consulta para el prompt P2 (salida estructurada). Filtre las intenciones `takeaway_*` | [huggingface.co/datasets/AmazonScience/massive](https://huggingface.co/datasets/AmazonScience/massive) |
| Mensajes sintéticos propios | Pedidos generados con un LLM a partir del menú real, con casos límite (agotados, cambios, ambigüedades) | Plan de pruebas (sección 4.3). Documente el prompt y revise a mano una muestra, como en el proyecto 3 | — |

### 5.3 Variables externas y datos propios

| Fuente | Qué ofrece | Para qué sirve | Enlace |
|---|---|---|---|
| Loyverse · API y reportes | Exportación de ventas por artículo y recibos | Fuente real del historial cuando se active la integración (H1–H4) | [developer.loyverse.com/docs](https://developer.loyverse.com/docs/) |
| Nager.Date · festivos de Colombia | API gratuita con los festivos por año | Variable «es festivo» o «puente» para el modelo | [date.nager.at](https://date.nager.at/api/v3/PublicHolidays/2026/CO) |
| Open-Meteo · clima histórico | Lluvia y temperatura por día y hora, sin clave de API | Variable opcional (la lluvia cambia los pedidos a domicilio) | [open-meteo.com](https://open-meteo.com/en/docs/historical-weather-api) |
| Ley 1581 de 2012 | Protección de datos personales | La tabla PrediccionPedidos solo guarda datos agregados | [Función Pública](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981) |

### 5.4 Dónde buscar más

| Portal | Búsqueda sugerida |
|---|---|
| [Kaggle Datasets](https://www.kaggle.com/datasets) | `bakery sales`, `restaurant orders`, `coffee shop sales`, `food demand forecasting` |
| [Hugging Face Datasets](https://huggingface.co/datasets?language=language:es) | `food order`, `restaurant`, filtro de idioma español |
| [Google Dataset Search](https://datasetsearch.research.google.com/) | `bakery daily sales`, `restaurant demand` |
| [datos.gov.co](https://www.datos.gov.co/) | `ventas`, `restaurantes`, `consumo de alimentos` |

### 5.5 Cómo elegir el dataset

> [!TIP]
> Antes de entrenar, transforme el dataset al **mismo formato** que tendrá PrediccionPedidos: una fila por `fecha`, `franja` y `sku`, con `cantidad_pedida`. Así el flujo de n8n no cambia cuando se reemplacen los datos de práctica por los de Tomasseli.

- [ ] Tiene fecha **y hora** (o franja) y una columna de producto que pueda hacer de SKU.
- [ ] Cubre al menos varias semanas seguidas para medir la tendencia y el efecto del día de la semana.
- [ ] La separación entrenamiento/prueba es **cronológica** (nunca aleatoria).
- [ ] Se calculó la línea base (promedio histórico por día de la semana y franja) con los mismos datos.
- [ ] Se revisó la licencia en la página del dataset y se citó la fuente en `h4_modelo/`.

---

## Anexo A · Decisiones pendientes de validación

Hasta validarlas, los componentes descritos son diseño objetivo y toda integración externa queda sujeta a prueba técnica.

- Si Loyverse admite crear y consultar ventas por API en la cuenta, y si el pedido así registrado genera la comanda en la impresora de cocina.
- Contenido de la comanda (notas, modalidad, hora, alérgenos declarados) y cómo se refleja en ella un cambio o una cancelación.
- Si cada plato tiene SKU o item ID.
- Método de registro de domicilios.
- Si las existencias se controlan por ingrediente, por plato o por conteo manual.
- Campos obligatorios de entrega.
- Horarios de desayuno y almuerzo, y hora límite.
- Protocolo con el que cocina reporta los estados de preparación (en preparación, listo) sin canal de mensajería.
- Destinatarios del correo de cierre.
- Política de cancelación.
- Conservación y acceso a los datos personales.
- Modalidad de despliegue y administración de n8n.
- Historial mínimo de pedidos para entrenar el modelo.
- Granularidad de la previsión (producto, fecha, franja), frecuencia de actualización y destinatarios.
- Herramienta de ML y método de publicación en PrediccionPedidos.

## Anexo B · Marco común del curso

Estas reglas aplican a todos los proyectos del curso. Se incluyen aquí para que la ficha se pueda leer sola.

### Calendario común de hitos

Este calendario aplica a **todos** los proyectos. La sección [4.2 Plan por hitos](#42-plan-por-hitos) detalla qué significa cada hito en este proyecto.

| Hito | Semanas | Sesiones del plan (fecha) | Producto del plan que se aplica al proyecto |
|---|---|---|---|
| **H1 · Planteamiento** | 2–3 | MasterClass de nivelación (12 Sep) · Fundamentos de prompting (13 Sep) · Prompting avanzado (19 Sep) | Problema, usuario, tarea y resultado esperado · Biblioteca de prompts · Secuencia de prompts documentada |
| **H2 · Documento base** | 3–4 | Documentos, datos y contexto (20 Sep) · Generación estructurada (26 Sep) · MasterClass (27 Sep) | Resumen ejecutivo trazable · Reporte profesional y plantilla de prompt reutilizable |
| **H3 · Presentación, prototipo y MVP** | 5–8 | Presentaciones (3 Oct) · Prototipado (4 Oct) · Co-creación de código (10 Oct) · No-Code (11 Oct) · MasterClass (18 Oct) · **Bootcamp (24–25 Oct)** | Presentación ejecutiva · Prototipo web · Interacción funcional · Arquitectura funcional y MVP sin código |
| **H4 · Modelo de ML** | 7–10 | ML sin código (17 Oct) · Preparación de datos (31 Oct) · Entrenamiento (1 Nov) · Validación (7 Nov) · MasterClass (8 Nov) | Ficha ¿sí requiere ML? · Dataset preparado · Modelo entrenado con registro de cambios · Validación y recomendación de uso o no uso |
| **H5 · Flujo con IA** | 11–14 | Triggers y actions (14 Nov) · Integración y mapeo (15 Nov) · APIs y webhooks (21 Nov) · IA en un workflow (22 Nov) · Diseño robusto (28 Nov) · MasterClass (29 Nov) · **Bootcamp (5–6 Dic)** | Proceso mapeado · Workflow formulario → app · Llamada a servicio o webhook · Paso de IA con acción posterior · Controles, validaciones y ruta humana |
| **H6 · Demo Day** | 15 | Semana de la Innovación (7–13 Dic) | Presentación final con demo en vivo |

### Entrega en el repositorio

Cada equipo trabaja en `bitacora/proyecto-<nombre-equipo>/` con esta estructura:

```text
bitacora/proyecto-<nombre-equipo>/
├── README.md                 # Ficha del proyecto (este formato) + estado de cada hito
├── h1_planteamiento/         # Documento de descubrimiento, línea base y biblioteca de prompts
├── h2_documento_base/        # Diccionario de datos, reglas, prompts usados y registro de verificación
├── h3_mvp/                   # Presentación (PDF), prototipo (HTML), libro de Sheets y capturas del MVP
├── h4_modelo/                # Dataset preparado, modelo, comparación con la línea base, recomendación
├── h5_flujo/                 # Diagrama, flujos exportados de n8n (sin credenciales), casos de prueba
└── h6_demo/                  # Guion, presentación final y video de respaldo
```

**Regla de oro (la misma de los laboratorios):** *la IA propone, el equipo verifica y decide.* Cada hito debe dejar registrado qué hizo la IA, qué revisó el equipo y qué se corrigió.

### Conexión entre el modelo de ML y el flujo

En este proyecto: **lote**. El modelo (en Orange o en un cuaderno de Python) no se conecta directamente con n8n: con la frecuencia acordada, se puntúan las fechas, franjas y SKU objetivo, y el resultado se escribe en la hoja PrediccionPedidos, que los escenarios D y E de n8n leen.

| Forma | Cómo funciona | Cuándo conviene |
|---|---|---|
| **Regla** | El árbol de decisión se lee y se traduce en una fórmula de Google Sheets. El flujo lee esa columna. | Cuando 2 o 3 variables explican casi todo el resultado |
| **Lote** | Se puntúan los casos nuevos con el modelo y el resultado se escribe en una hoja que el flujo lee. | Cuando el modelo usa muchas variables |
| **Registro** | Una persona usa el modelo y anota el resultado en un formulario, que es el trigger del flujo. | Modelos de imagen o sonido |

### Principios comunes

| Principio | Cómo aparece en este proyecto |
|---|---|
| Primero el problema, después la herramienta | La ficha empieza por necesidades; la línea base se mide antes de construir |
| La IA propone, la persona decide | El LLM propone un JSON que n8n valida; el operador atiende las derivaciones; cocina decide cuánto preparar |
| Verificar lo que produce la IA | Disponibilidad revalidada al confirmar y salidas en JSON con esquema |
| Un modelo puede no servir, y eso también es un resultado | Si la previsión no mejora la línea base, no se publica |
| Diseñar para el fallo | Idempotencia, reintentos, Alertas y plan B por cada sistema |
| Cuidar el dato | Ley 1581, mínimo de datos y un modelo entrenado sin datos personales |
