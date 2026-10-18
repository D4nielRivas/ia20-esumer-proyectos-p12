# Automatización operativa — Panadería Tomasseli

Gestión de pedidos, menú, inventario y cocina mediante **WhatsApp · Google Workspace · Loyverse · n8n · Machine Learning**.

| | |
|---|---|
| **Estado** | Propuesta para validación operativa |
| **Versión de la especificación** | 1.2 (18 de octubre de 2026) |
| **Orquestador** | n8n (único en producción) |
| **Especificación completa** | [`docs/Ficha_Especificacion_Panaderia_Tomasseli.md`](docs/Ficha_Especificacion_Panaderia_Tomasseli.md) |

---

## Descripción

Tomasseli recibe pedidos por WhatsApp y debe coordinarlos con la disponibilidad del menú, la operación de cocina, el inventario y el registro de ventas en Loyverse TPV. Hoy esa coordinación depende de información dispersa y transcripción manual, lo que puede causar respuestas con opciones agotadas, reprocesos, demoras en cocina y diferencias entre lo solicitado, preparado y registrado.

Este proyecto organiza el dato operativo en **Google Sheets** y conecta los sistemas con automatizaciones en **n8n**. Un asistente conversacional con IA atiende a los clientes por WhatsApp, pero **las reglas determinísticas controlan la disponibilidad, la confirmación y el registro**: el LLM propone y el orquestador valida.

## Qué resuelve

- **Una sola fuente de verdad** para el menú fijo de desayunos, el menú diario/semanal de almuerzos y la disponibilidad por producto.
- **Pedidos sin retranscripción:** el bot captura el pedido estructurado, lo valida y lo registra una sola vez.
- **Cocina directa:** la comanda se imprime desde Loyverse; WhatsApp solo canaliza las órdenes de los clientes.
- **Conciliación diaria** entre pedidos y ventas, con resumen por Gmail y cola de excepciones.
- **Previsión de pedidos:** un modelo de ML predice las órdenes de los clientes a partir de las tendencias del historial, como apoyo informativo a la planeación.

## Cómo funciona

```text
Cliente WhatsApp (solo órdenes de clientes)
  -> WhatsApp Business API / Webhook
  -> n8n
       -> normalización, idempotencia, reglas y bitácora
       -> consulta menú/disponibilidad en Google Sheets
       -> LLM con contexto acotado y salida estructurada
       -> validación determinística y confirmación
       -> Pedido consolidado en Sheets
       -> Loyverse TPV -> comanda impresa en cocina
       -> Gmail: resumen diario (incluye previsión de pedidos)

Administración / Cocina -> Google Forms -> validación -> Sheets -> actualización del bot
Historial de pedidos -> modelo de ML -> hoja PrediccionPedidos -> vistas y Gmail
```

### Escenarios de automatización

| Escenario | Descripción |
|---|---|
| A · Actualización de menú | Un Google Form valida y publica cambios de menú y agotados; el bot los refleja en ≤ 1 minuto. |
| B · Conversación y pedido | Webhook de WhatsApp, deduplicación, recuperación de menú, extracción con LLM, validación y confirmación. |
| C · Cocina y POS | Registro del pedido en Loyverse, emisión de la comanda impresa y seguimiento de estados. |
| D · Cierre diario | Consolidado de pedidos, cuadre frente a Loyverse e informe por Gmail. |
| E · Previsión de pedidos | Cálculo por lote de la cantidad esperada por producto, fecha y franja. |

### Principios de diseño

- **El LLM no decide:** no modifica inventario, no crea ventas en TPV, no confirma disponibilidad por memoria.
- **El ML es consultivo:** la previsión nunca interviene en aceptar, confirmar o rechazar un pedido, y solo se publica si mejora una línea base simple (promedio histórico por día de la semana y franja).
- **Idempotencia:** un pedido, una comanda y una venta como máximo, aunque se repitan los eventos.
- **Diseñado para el fallo:** colas, reintentos, alertas y procedimientos manuales para cada dependencia.
- **Mínimo de datos personales:** el modelo de ML usa datos agregados y la comanda no incluye el teléfono completo salvo necesidad aprobada.

## Alcance y estado

La especificación es un **diseño objetivo**. Cualquier integración externa queda sujeta a prueba técnica, y varios puntos críticos requieren validación antes de construir (ver el Anexo A de la especificación), entre ellos:

- Si la API/conector de Loyverse permite crear ventas y generar la comanda en la impresora de cocina.
- Si cada plato tiene SKU/item ID y cómo se controla el stock.
- El historial mínimo de pedidos disponible para entrenar el modelo.
- La modalidad de despliegue de n8n.

## Plan de trabajo

| Hito | Enfoque | Estado |
|---|---|---|
| H1 — Descubrimiento | Mapa AS-IS/TO-BE, reglas, catálogo, responsables, línea base y accesos | Pendiente |
| H2 — Datos y menú | Libro de Sheets, validaciones, protecciones y formularios | Pendiente |
| H3 — Conversación IA | Webhook WhatsApp, prompt versionado, extracción y derivación humana | Pendiente |
| H4 — Operación integrada | Pedidos en n8n, Loyverse y comanda, estados, idempotencia y alertas | Pendiente |
| H5 — Reportes y previsión | Cierre por Gmail, cuadre pedido/TPV y modelo de previsión | Pendiente |
| H6 — Piloto y salida | Pruebas, capacitación, manual operativo y acta de habilitación | Pendiente |

## Estructura propuesta del repositorio

```text
.
├── README.md
├── docs/
│   └── Ficha_Especificacion_Panaderia_Tomasseli.md   # especificación funcional y técnica
├── h1_descubrimiento/        # mapa AS-IS/TO-BE, línea base, inventario de accesos
├── h2_datos_menu/            # diccionario de datos, plantillas de Sheets y Forms
├── h3_conversacion/          # prompts versionados, esquema de extracción
├── h4_operacion/             # workflows de n8n exportados (.json), mapeo SKU–Loyverse
├── h5_reportes_prevision/    # plantilla del cierre diario, notebooks/modelo, recomendación de uso
├── h6_piloto/                # plan de pruebas, manual operativo, acta
└── pruebas/                  # casos P-01 a P-16 y sus resultados
```

> Es una propuesta organizada por hitos; se puede ajustar al comenzar la construcción.

## Pruebas

El plan de pruebas de integración (P-01 a P-16) está en la sección 4.3 de la especificación. Cubre menú, pedidos completos e incompletos, duplicados, fallas de cada integración, comanda de cocina, cierre diario, permisos y la previsión de pedidos frente a su línea base.

## Seguridad y privacidad

- **No subir al repositorio** credenciales, tokens de API, claves, exportaciones de n8n con credenciales ni datos reales de clientes.
- Los secretos viven en el almacén de credenciales de n8n o en propiedades protegidas, nunca en celdas, prompts ni mensajes.
- Cuentas institucionales con MFA, permisos por rol y acceso mínimo a las hojas.
- Antes del piloto deben definirse el aviso de privacidad, la finalidad, la retención y el responsable de la atención de solicitudes.
- Los datos de ejemplo y de prueba deben ser ficticios.

## Cómo contribuir

1. Crear una rama a partir de la principal para cada cambio.
2. Documentar en el mismo cambio los ajustes a reglas, prompts, mapeos o versiones del modelo, con su motivo.
3. Mantener los prompts y los workflows versionados y con posibilidad de reversión.
4. Verificar que los cambios no incluyan secretos antes de hacer commit.

## Documentación

- [Especificación técnica completa](docs/Ficha_Especificacion_Panaderia_Tomasseli.md): necesidades, entendimiento, estructuración, implementación y decisiones pendientes.
