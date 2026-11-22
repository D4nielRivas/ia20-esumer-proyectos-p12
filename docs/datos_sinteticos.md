# Datos sintéticos de pedidos · P12

> **Dato ficticio.** Panadería Tomasseli todavía no ha entregado un historial real de pedidos. Este historial es **simulado** y sirve solo para entrenar y evaluar la previsión de pedidos (H-9, regla R17). El modelo que se entrena con él es **didáctico**: no predice la demanda real de la panadería.

Decisión del docente (22 Nov 2026): P12 conserva la previsión por regresión, entrenada con datos sintéticos generados por un script de Python con semilla fija y con sus supuestos documentados en este archivo.

## Archivos

| Qué | Dónde |
|---|---|
| Generador | `scripts/generar_pedidos_sinteticos.py` (solo biblioteca estándar, semilla fija `20261122`) |
| Salida | `insumos/historial_pedidos.csv` (UTF-8, con encabezado) |
| Entradas del generador | `insumos/menus_diarios.csv`, `insumos/detalle_menu_dia.csv` y `insumos/catalogo_items.csv` (solo las opciones activas y disponibles de cada día de la semana) |

Para regenerarlo, desde la raíz del repositorio:

```bash
python3 scripts/generar_pedidos_sinteticos.py
```

Con la misma semilla y los mismos CSV del menú, el archivo sale idéntico.

## Formato

Hay una fila por fecha, franja y opción ofrecida ese día, incluidas las que tienen cantidad cero. El archivo es agregado y **no tiene datos personales**.

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | fecha ISO | Día del servicio |
| `franja` | `HH:MM` | Inicio de la franja de 30 minutos (11:30 a 15:00) |
| `item_id` | texto | Opción del catálogo (ME…, MS…, SP…, JG…) |
| `categoria` | texto | `ME`, `MS`, `SP` o `JG` |
| `cantidad` | entero ≥ 0 | Unidades de esa opción pedidas en la franja |

```text
fecha,franja,item_id,categoria,cantidad
2026-08-30,11:30,ME004,ME,2
```

Es el mismo formato que la tabla `historial_pedidos` del README §3.2. Cuando Tomasseli entregue datos reales, agregados y sin datos personales, reemplazan este archivo con el mismo formato.

## Supuestos de la simulación

| Efecto | Supuesto | Parámetro en el script |
|---|---|---|
| Periodo | 12 semanas, del domingo 30 ago al sábado 21 nov de 2026 (84 días) | `INICIO`, `DIAS` |
| Volumen diario | Entre 60 y 90 almuerzos al día (recortado a ese rango) | `MIN_DIA`, `MAX_DIA` |
| Día de la semana | Más entre semana que el fin de semana. Almuerzos esperados: lunes 78, martes 76, miércoles 77, jueves 79, viernes 82, sábado 68, domingo 61 | `BASE_DIA` |
| Festivos de Colombia | Los del periodo (12 oct, 2 nov y 16 nov) se comportan como domingo | `FESTIVOS` |
| Tendencia | Aumento lineal leve: +8 % entre el primer y el último día | `TENDENCIA_TOTAL` |
| Franja horaria | 8 franjas de 30 minutos entre 11:30 y 15:30, con el pico de 12:00 a 13:30. Pesos: 6, 14, 20, 20, 16, 11, 8 y 5 % | `FRANJAS`, `PESO_FRANJA` |
| Ruido | Variación diaria normal con desviación relativa del 7 % | `RUIDO_DIA` |
| Composición del almuerzo | 1 principal (45 % Menú Especial y 55 % Menú Sencillo), 1 sopa y 1 jugo, elegidos entre las opciones del menú de ese día de la semana. El 8 % pide «sin sopa» y el 5 % «sin jugo» | `PROB_ESPECIAL`, `PROB_SIN_SOPA`, `PROB_SIN_JUGO` |
| Preferencia por opción | Cada opción tiene una popularidad fija entre 0,6 y 1,6, derivada de la semilla, para que haya un patrón que la regresión pueda aprender | `popularidad` |

## Lo que resultó

- 8.544 filas, 31 opciones distintas, del 30 ago al 21 nov de 2026.
- Entre 60 y 90 almuerzos al día (promedio de 77,6).
- Promedio de almuerzos por día de la semana: lunes 77,1, martes 83,2, miércoles 79,8, jueves 82,2, viernes 84,5, sábado 70,7 y domingo 65,6. Los promedios incluyen la tendencia y el ruido. El lunes queda más bajo porque dos de los festivos caen en lunes.

## Cómo se usa en la previsión

- **Corte cronológico, nunca aleatorio:** las 10 primeras semanas para entrenar y las 2 últimas para probar.
- **Línea base:** promedio por día de la semana y franja.
- **Modelos:** regresión lineal y árbol de regresión con scikit-learn. La elección queda en `research.md` de la spec 001.
- **Publicación:** la previsión se publica solo si su error en las 2 semanas de prueba es menor que el de la línea base. Si no la mejora, no se publica y se documenta. Siempre es solo informativa (R17).
- El modelo entrenado se guarda con joblib en `app/models/vN/`, FastAPI lo carga una sola vez y lo sirve en `GET /prevision`.

## Diferencias con la guía del curso

- **Estacionalidad.** La guía pide «estacionalidad». Aquí la única estacionalidad es la **semanal** (día de la semana y festivos), más una **tendencia** leve al alza. No hay efecto mensual, de quincena ni de temporada. Con 12 semanas de historia, un efecto mensual tampoco se podría validar con el corte de 10 + 2 semanas. Decisión del equipo del 22 Nov 2026: se documenta tal cual.
- **Duración.** La guía habla de «unos 3 meses». Aquí son 12 semanas (84 días).

## Limitaciones

- Las cantidades no reflejan la demanda real de Tomasseli. Las métricas sirven para comparar el modelo contra la línea base dentro del ejercicio, no para planear la cocina.
- El menú es la plantilla semanal de `insumos/`: no simula agotados, cambios de menú ni días sin servicio.
- Los efectos son independientes entre sí, y la popularidad de cada opción no cambia en el periodo.
