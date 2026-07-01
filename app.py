from flask import Flask, redirect, render_template, request, session, url_for
from datetime import datetime
import json
from uuid import uuid4
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'fogon-secret-key'

PAQUETES_CARNE = [
    {
        "id": 1,
        "nombre": "Pa' que no te Atragantes",
        "descripcion": "1kg de carne asada, 2 salchichas asadas, 2 cebollas asadas, 2 papas asadas con mantequilla, 1 refresco (2.5 lt a elegir), tortillas y salsas a elegir.",
        "precio": "$440 MXN",
    },
    {
        "id": 2,
        "nombre": "1kg Pa'que Amarre",
        "descripcion": "1kg de carne asada, 2 salchichas asadas, 2 cebollas asadas, 2 papas asadas con mantequilla, tortillas y salsas a elegir.",
        "precio": "$380 MXN",
    },
    {
        "id": 3,
        "nombre": "1/2kg Pal' Antojo",
        "descripcion": "1/2kg de carne asada, 2 salchichas asadas, 2 cebollas asadas, 2 papas asadas con mantequilla, tortillas y salsas a elegir.",
        "precio": "$200 MXN",
    },
    {
        "id": 4,
        "nombre": "Una Bien Servida",
        "descripcion": "4 tacos de tortilla amarilla grande, 1 papa o salchicha asada (a elegir), 1 cebolla asada, preperados a su gusto.",
        "precio": "$100 MXN",
    },
    {
        "id": 5,
        "nombre": "PAPON ASADO",
        "descripcion": "1 papa asada grande con mantequilla, queso y carne asada.",
        "precio": "65 MXN",
    },
    {
        "id": 6,
        "nombre": "PA TOMAR",
        "descripcion": "1 bebida de 2.5 ltros (a elegir).",
        "precio": "60 MXN",
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


PEDIDOS_CONFIRMADOS = load_pedidos()


@app.route('/')
def inicio():
    return render_template('index.html', paquetes=PAQUETES_CARNE)


@app.route('/pedido/<int:paquete_id>', methods=['GET', 'POST'])
def pedido(paquete_id):
    paquete = next((p for p in PAQUETES_CARNE if p["id"] == paquete_id), None)
    if paquete is None:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        agregar_bebida = request.form.get('agregar_bebida')
        if agregar_bebida is not None:
            session['pending_bebida'] = {
                'agregar_bebida': agregar_bebida == 'si',
            }
            return redirect(url_for('completar_pedido', paquete_id=paquete_id))

    return render_template('bebida.html', paquete=paquete)


@app.route('/pedido/<int:paquete_id>/completar', methods=['GET', 'POST'])
def completar_pedido(paquete_id):
    paquete = next((p for p in PAQUETES_CARNE if p["id"] == paquete_id), None)
    if paquete is None:
        return redirect(url_for('inicio'))

    pending_bebida = session.get('pending_bebida')
    if not pending_bebida:
        return redirect(url_for('pedido', paquete_id=paquete_id))

    mensaje = None
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        metodo_pago = request.form.get('metodo_pago', '').strip()
        telefono = request.form.get('telefono', '').strip()
        domicilio = request.form.get('domicilio', '').strip()

        if nombre and metodo_pago and telefono and domicilio:
            session['pending_confirmation'] = {
                'paquete_id': paquete['id'],
                'paquete_nombre': paquete['nombre'],
                'cliente': nombre,
                'metodo_pago': metodo_pago,
                'telefono': telefono,
                'domicilio': domicilio,
                'agregar_bebida': pending_bebida['agregar_bebida'],
                'timestamp': datetime.utcnow().isoformat() + 'Z',
            }
            session.pop('pending_bebida', None)
            return redirect(url_for('confirmacion', paquete_id=paquete_id))
        else:
            mensaje = "Por favor completa tu nombre, método de pago, teléfono y domicilio."

    return render_template('pedido.html', paquete=paquete, mensaje=mensaje, action_url=url_for('completar_pedido', paquete_id=paquete_id))


@app.route('/pedido/<int:paquete_id>/bebida', methods=['GET'])
def bebida(paquete_id):
    return redirect(url_for('pedido', paquete_id=paquete_id))


@app.route('/pedido/<int:paquete_id>/confirmacion', methods=['GET', 'POST'])
def confirmacion(paquete_id):
    paquete = next((p for p in PAQUETES_CARNE if p['id'] == paquete_id), None)
    if paquete is None:
        return redirect(url_for('inicio'))

    pending_confirmation = session.get('pending_confirmation')
    if not pending_confirmation:
        return redirect(url_for('pedido', paquete_id=paquete_id))

    if request.method == 'POST':
        pedido = {
            'id': uuid4().hex,
            'paquete_id': pending_confirmation['paquete_id'],
            'paquete_nombre': pending_confirmation['paquete_nombre'],
            'cliente': pending_confirmation['cliente'],
            'metodo_pago': pending_confirmation['metodo_pago'],
            'telefono': pending_confirmation.get('telefono', ''),
            'domicilio': pending_confirmation.get('domicilio', ''),
            'agregar_bebida': pending_confirmation['agregar_bebida'],
            'timestamp': pending_confirmation['timestamp'],
        }
        PEDIDOS_CONFIRMADOS.append(pedido)
        save_pedidos(PEDIDOS_CONFIRMADOS)
        session.pop('pending_confirmation', None)
        return redirect(url_for('ver_pedidos'))

    return render_template('confirmacion.html', paquete=paquete, pedido=pending_confirmation)


@app.route('/pedidos')
def ver_pedidos():
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