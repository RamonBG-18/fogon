from flask import Flask, redirect, render_template, request, session, url_for
from datetime import datetime
import json
import re
from uuid import uuid4
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'fogon-secret-key'

PAQUETES_CARNE = [
    {
        "id": 1,
        "nombre": "1 kg Pa' Comer Aqui",
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
        "nombre": "2kg Pa'que Amarre de Verdad",
        "descripcion": "2 kilos de carne asada, 2 salchichas asadas, 4 cebollas asadas, 4 papas asadas con mantequilla, tortillas y salsas a elegir.",
        "precio": "$700 MXN",
    },
    {
        "id": 5,
        "nombre": "Una Bien Servida",
        "descripcion": "4 tacos de tortilla amarilla grande, 1 papa o salchicha asada (a elegir), 1 cebolla asada, preperados a su gusto.",
        "precio": "$100 MXN",
    },
    {
        "id": 6,
        "nombre": "PAPON ASADO",
        "descripcion": "1 papa asada grande con mantequilla, queso y carne asada.",
        "precio": "65 MXN",
    },
]

DATA_FILE = Path(__file__).parent / 'pedidos.json'

PRECIOS_BEBIDAS = {
    'Coca 600 ml': 30,
    'Coca 355 ml': 25,
    'Coca 2.5 Lt': 70,
    'Sprite 600 ml': 30,
    'Sprite 355 ml': 25,
    'Dr pepper 600 ml': 30,
    'Dr pepper 355 ml': 25,
    'Mundet 600 ml': 30,
    'Mundet 355 ml': 25,
    'Fanta Naranja 600 ml': 30,
    'Fanta Naranja 355 ml': 25,
}


def load_pedidos():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def save_pedidos(pedidos):
    DATA_FILE.write_text(json.dumps(pedidos, ensure_ascii=False, indent=2), encoding='utf-8')


def get_precio_numero(precio_text):
    if not precio_text:
        return 0
    match = re.search(r'(\d+)', str(precio_text))
    return int(match.group(1)) if match else 0


def calcular_total_pedido(paquete, bebidas):
    precio_paquete = get_precio_numero(paquete.get('precio', '')) if paquete else 0
    precio_bebidas = sum(PRECIOS_BEBIDAS.get(nombre, 0) * cantidad for nombre, cantidad in bebidas.items())
    return precio_paquete + precio_bebidas


PEDIDOS_CONFIRMADOS = load_pedidos()


@app.route('/')
def inicio():
    return render_template('index.html', paquetes=PAQUETES_CARNE)


@app.route('/pedido/<int:paquete_id>', methods=['GET', 'POST'])
def pedido(paquete_id):
    paquete = next((p for p in PAQUETES_CARNE if p["id"] == paquete_id), None)
    if paquete is None:
        return redirect(url_for('inicio'))

    session['pending_package_id'] = paquete_id
    return redirect(url_for('seleccionar_bebidas'))


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
                'bebidas': session.get('bebidas_seleccionadas', {}),
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


@app.route('/bebidas', methods=['GET', 'POST'])
def seleccionar_bebidas():
    bebidas = [
        {"nombre": "Coca 600 ml", "precio": "$30 MXN"},
        {"nombre": "Coca 355 ml", "precio": "$25 MXN"},
        {"nombre": "Coca 2.5 Lt", "precio": "$70 MXN"},
        {"nombre": "Sprite 600 ml", "precio": "$30 MXN"},
        {"nombre": "Sprite 355 ml", "precio": "$25 MXN"},
        {"nombre": "Dr pepper 600 ml", "precio": "$30 MXN"},
        {"nombre": "Dr pepper 355 ml", "precio": "$25 MXN"},
        {"nombre": "Mundet 600 ml", "precio": "$30 MXN"},
        {"nombre": "Mundet 355 ml", "precio": "$25 MXN"},
        {"nombre": "Fanta Naranja 600 ml", "precio": "$30 MXN"},
        {"nombre": "Fanta Naranja 355 ml", "precio": "$25 MXN"},
    ]

    cantidades = {}
    if request.method == 'POST':
        for bebida in bebidas:
            nombre = bebida['nombre']
            cantidad = request.form.get(f'cantidad_{nombre}', '0')
            try:
                cantidad_int = int(cantidad)
            except ValueError:
                cantidad_int = 0
            if cantidad_int > 0:
                cantidades[nombre] = cantidad_int

        session['bebidas_seleccionadas'] = cantidades
        session['pending_bebida'] = {
            'agregar_bebida': bool(cantidades),
            'bebidas': cantidades,
        }
        if cantidades:
            return redirect(url_for('confirmacion_bebidas'))
        return redirect(url_for('completar_pedido', paquete_id=session.get('pending_package_id', 1)))

    return render_template('bebidas.html', bebidas=bebidas)


@app.route('/bebidas/confirmacion', methods=['GET', 'POST'])
def confirmacion_bebidas():
    bebidas = session.get('bebidas_seleccionadas', {})
    if not bebidas:
        return redirect(url_for('completar_pedido', paquete_id=session.get('pending_package_id', 1)))

    if request.method == 'POST':
        return redirect(url_for('completar_pedido', paquete_id=session.get('pending_package_id', 1)))

    return render_template('confirmacion_bebidas.html', bebidas=bebidas)


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
            'bebidas': pending_confirmation.get('bebidas', {}),
            'estado': 'pendiente',
            'timestamp': pending_confirmation['timestamp'],
        }
        PEDIDOS_CONFIRMADOS.append(pedido)
        save_pedidos(PEDIDOS_CONFIRMADOS)
        session.pop('pending_confirmation', None)
        return redirect(url_for('ver_pedidos'))

    total_pedido = calcular_total_pedido(paquete, pending_confirmation.get('bebidas', {}))
    return render_template('confirmacion.html', paquete=paquete, pedido=pending_confirmation, total_pedido=total_pedido)


@app.route('/pedidos', methods=['GET', 'POST'])
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

    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id')
        nuevo_estado = request.form.get('estado')
        if pedido_id and nuevo_estado in {'pendiente', 'confirmado', 'entregado'}:
            global PEDIDOS_CONFIRMADOS
            if nuevo_estado == 'entregado':
                PEDIDOS_CONFIRMADOS = [p for p in PEDIDOS_CONFIRMADOS if p.get('id') != pedido_id]
            else:
                for p in PEDIDOS_CONFIRMADOS:
                    if p.get('id') == pedido_id:
                        p['estado'] = nuevo_estado
                        break
            save_pedidos(PEDIDOS_CONFIRMADOS)

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

    for pedido in pedidos:
        paquete = next((p for p in PAQUETES_CARNE if p['id'] == pedido.get('paquete_id')), None)
        pedido['total'] = calcular_total_pedido(paquete, pedido.get('bebidas', {}))

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