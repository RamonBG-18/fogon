from flask import Flask, redirect, render_template, request, url_for

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
            mensaje = f"Pedido confirmado para {nombre}. Método de pago: {metodo_pago}."
        else:
            mensaje = "Por favor completa tu nombre y método de pago."

    return render_template('pedido.html', paquete=paquete, mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)