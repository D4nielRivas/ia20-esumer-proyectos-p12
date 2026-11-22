"""Genera el historial sintético de pedidos de P12 para la previsión (H-9).

Dato FICTICIO: Tomasseli no ha entregado historial real. Este script lo
simula de forma reproducible (semilla fija) para entrenar y evaluar la
regresión por lote. Cuando haya datos reales, agregados y sin datos
personales, reemplazan este archivo con el mismo formato.

Uso (desde la raíz del repositorio, solo biblioteca estándar):

    python3 scripts/generar_pedidos_sinteticos.py

Salida: insumos/historial_pedidos.csv (UTF-8, con encabezado), una fila
por fecha, franja y opción ofrecida ese día (incluye las cantidades en
cero):

    fecha,franja,item_id,categoria,cantidad
    2026-08-30,11:30,ME004,ME,2

Supuestos de la simulación (decididos por el equipo el 22 Nov 2026):
- 12 semanas: del domingo 30 ago al sábado 21 nov de 2026 (84 días):
  10 semanas para entrenar y 2 para probar, con corte cronológico.
- Entre 60 y 90 almuerzos al día: más entre semana que el sábado y el
  domingo, con una tendencia leve al alza en el periodo. Los festivos
  de Colombia del periodo (12 oct, 2 nov y 16 nov) se comportan como
  domingo.
- 8 franjas de 30 minutos entre 11:30 y 15:30, con el pico de 12:00 a
  13:30.
- Cada almuerzo lleva un principal (Menú Especial o Menú Sencillo), una
  sopa y un jugo, elegidos entre las opciones del menú de ese día de la
  semana (insumos/menus_diarios.csv y detalle_menu_dia.csv). Una parte
  pide «sin sopa» o «sin jugo».
- Cada opción tiene una popularidad fija (derivada de la semilla), para
  que haya un patrón que la regresión pueda aprender.
"""
import csv
import datetime as dt
import random
from pathlib import Path

SEMILLA = 20261122
INICIO = dt.date(2026, 8, 30)
DIAS = 84
FESTIVOS = {dt.date(2026, 10, 12), dt.date(2026, 11, 2), dt.date(2026, 11, 16)}

FRANJAS = ["11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00"]
PESO_FRANJA = [0.06, 0.14, 0.20, 0.20, 0.16, 0.11, 0.08, 0.05]

# Almuerzos esperados por día de la semana (1 = lunes … 7 = domingo).
BASE_DIA = {1: 78, 2: 76, 3: 77, 4: 79, 5: 82, 6: 68, 7: 61}
TENDENCIA_TOTAL = 0.08      # +8 % entre el primer y el último día
RUIDO_DIA = 0.07            # variación diaria (desviación relativa)
MIN_DIA, MAX_DIA = 60, 90

PROB_ESPECIAL = 0.45        # el resto elige Menú Sencillo
PROB_SIN_SOPA = 0.08
PROB_SIN_JUGO = 0.05

RAIZ = Path(__file__).resolve().parent.parent
INSUMOS = RAIZ / "insumos"
SALIDA = INSUMOS / "historial_pedidos.csv"
COLUMNAS = ["fecha", "franja", "item_id", "categoria", "cantidad"]


def leer_menu():
    """Devuelve {dia_semana: {categoria: [item_id disponibles]}}."""
    dias = {}
    with open(INSUMOS / "menus_diarios.csv", encoding="utf-8") as f:
        orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for fila in csv.DictReader(f):
            dias[fila["id_menu_dia"]] = orden.index(fila["dia_semana"]) + 1
    categoria = {}
    with open(INSUMOS / "catalogo_items.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila["activo"] == "t":
                categoria[fila["id_item"]] = fila["id_categoria"]
    menu = {d: {} for d in range(1, 8)}
    with open(INSUMOS / "detalle_menu_dia.csv", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            item = fila["id_item"]
            if fila["disponible"] == "t" and item in categoria:
                d = dias[fila["id_menu_dia"]]
                menu[d].setdefault(categoria[item], []).append(item)
    return menu, categoria


def main():
    rng = random.Random(SEMILLA)
    menu, categoria = leer_menu()
    popularidad = {item: rng.uniform(0.6, 1.6) for item in sorted(categoria)}

    filas = []
    for i in range(DIAS):
        fecha = INICIO + dt.timedelta(days=i)
        dia = 7 if fecha in FESTIVOS else fecha.isoweekday()
        opciones = menu[fecha.isoweekday()]
        esperado = BASE_DIA[dia] * (1 + TENDENCIA_TOTAL * i / (DIAS - 1))
        total = round(esperado * (1 + rng.gauss(0, RUIDO_DIA)))
        total = max(MIN_DIA, min(MAX_DIA, total))

        conteo = {(f, item): 0 for f in FRANJAS
                  for items in opciones.values() for item in items}
        for _ in range(total):
            franja = rng.choices(FRANJAS, PESO_FRANJA)[0]
            cat = "ME" if rng.random() < PROB_ESPECIAL else "MS"
            elegidos = [cat]
            if rng.random() >= PROB_SIN_SOPA:
                elegidos.append("SP")
            if rng.random() >= PROB_SIN_JUGO:
                elegidos.append("JG")
            for c in elegidos:
                items = opciones[c]
                item = rng.choices(items, [popularidad[x] for x in items])[0]
                conteo[(franja, item)] += 1

        for (franja, item), cantidad in sorted(conteo.items()):
            filas.append({"fecha": fecha.isoformat(), "franja": franja,
                          "item_id": item, "categoria": categoria[item],
                          "cantidad": cantidad})

    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"{len(filas)} filas escritas en {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
