from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime
import json
from uuid import uuid4
from pathlib import Path

app = Flask(__name__)

PAQUETES_CARNE = [
    {
        "id": 1,
        "nombre": "Paquete Familiar",
        "descripcion": "3kg de Sirloin, 1kg de salchicha para asar, tortillas, cebollitas y salsa.",
        "precio": "$850 MXN",
    },
    {
        "id": 2,
        "nombre": "Combo Compadres",
        "descripcion": "2kg de Ribeye calidad Angus, 1 bolsa de carbón, aguacates y tortillas de harina.",
        "precio": "$1,200 MXN",
    },
    {
        "id": 3,
        "nombre": "Clásico Norteño",
        "descripcion": "2kg de Arrachera marinada, queso menonita para fundir y guacamole.",
        "precio": "$750 MXN",
    },
]


DATA_FILE = Path(__file__).parent / 'pedidos.json'


def load_pedidos():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def save_pedidos(pedidos):
    DATA_FILE.write_text(json.dumps(pedidos, ensure_ascii=False, indent=2), encoding='utf-8')


# Almacenamiento en memoria de pedidos confirmados (se carga desde `pedidos.json`).
PEDIDOS_CONFIRMADOS = load_pedidos()


@app.route('/')
def inicio():
    return render_template('index.html', paquetes=PAQUETES_CARNE)


@app.route('/pedido/<int:paquete_id>', methods=['GET', 'POST'])
def pedido(paquete_id):
    paquete = next((p for p in PAQUETES_CARNE if p["id"] == paquete_id), None)
    if paquete is None:
        return redirect(url_for('inicio'))

    mensaje = None
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        metodo_pago = request.form.get('metodo_pago', '').strip()

        if nombre and metodo_pago:
            # Guardamos el pedido en memoria y en disco
            pedido = {
                'id': uuid4().hex,
                'paquete_id': paquete['id'],
                'paquete_nombre': paquete['nombre'],
                'cliente': nombre,
                'metodo_pago': metodo_pago,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
            }
            PEDIDOS_CONFIRMADOS.append(pedido)
            save_pedidos(PEDIDOS_CONFIRMADOS)
            return redirect(url_for('ver_pedidos'))
        else:
            mensaje = "Por favor completa tu nombre y método de pago."

    return render_template('pedido.html', paquete=paquete, mensaje=mensaje)


@app.route('/pedidos')
def ver_pedidos():
    # Mostramos los pedidos confirmados con filtros y orden.
    q = request.args.get('q', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    order = request.args.get('order', 'recent')

    def parse_iso(ts):
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace('Z', ''))
        except Exception:
            return None

    # Lee desde disco para que los filtros siempre usen los datos persistidos
    items = load_pedidos()

    if q:
        ql = q.lower()
        items = [p for p in items if ql in p.get('cliente', '').lower() or ql in p.get('paquete_nombre', '').lower() or ql in p.get('metodo_pago', '').lower()]

    if date_from or date_to:
        df = None
        dt = None
        try:
            if date_from:
                df = datetime.fromisoformat(date_from).date()
            if date_to:
                dt = datetime.fromisoformat(date_to).date()
        except Exception:
            df = dt = None

        if df or dt:
            filtered = []
            for p in items:
                ts = parse_iso(p.get('timestamp'))
                if ts is None:
                    continue
                d = ts.date()
                if df and d < df:
                    continue
                if dt and d > dt:
                    continue
                filtered.append(p)
            items = filtered

    # Ordenar por timestamp
    def key_ts(p):
        ts = parse_iso(p.get('timestamp'))
        return ts or datetime.min

    reverse = True if order != 'oldest' else False
    pedidos = sorted(items, key=key_ts, reverse=reverse)

    return render_template('pedidos.html', pedidos=pedidos, q=q, date_from=date_from, date_to=date_to, order=order)



@app.route('/pedidos/eliminar/<pedido_id>', methods=['POST'])
def eliminar_pedido(pedido_id):
    global PEDIDOS_CONFIRMADOS
    antes = len(PEDIDOS_CONFIRMADOS)
    PEDIDOS_CONFIRMADOS = [p for p in PEDIDOS_CONFIRMADOS if p.get('id') != pedido_id]
    if len(PEDIDOS_CONFIRMADOS) != antes:
        save_pedidos(PEDIDOS_CONFIRMADOS)
    return redirect(url_for('ver_pedidos'))


if __name__ == '__main__':
    app.run(debug=True)