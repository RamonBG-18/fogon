from app import app, DATA_FILE


def reset_state():
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    app.PEDIDOS_CONFIRMADOS = []


def test_bebidas_seleccionadas_no_se_mezclan_en_pedidos_nuevos():
    reset_state()
    client = app.test_client()

    # Primer pedido con paquete 7 y bebidas seleccionadas
    client.post('/pedido/7')
    client.post('/bebidas', data={'cantidad_Coca 600 ml': '2', 'cantidad_Sprite 355 ml': '1'})
    client.post('/bebidas/confirmacion')
    client.post('/pedido/7/completar', data={
        'nombre': 'Ana',
        'metodo_pago': 'Efectivo',
        'telefono': '5551234',
        'domicilio': 'Calle 1',
    })
    client.post('/pedido/7/confirmacion')

    # Segundo pedido sin bebidas
    client.post('/pedido/1', data={'agregar_bebida': 'no'})
    client.post('/pedido/1/completar', data={
        'nombre': 'Luis',
        'metodo_pago': 'Transferencia',
        'telefono': '5559999',
        'domicilio': 'Calle 2',
    })
    client.post('/pedido/1/confirmacion')

    assert len(app.PEDIDOS_CONFIRMADOS) == 2
    assert app.PEDIDOS_CONFIRMADOS[0]['bebidas'] == {'Coca 600 ml': 2, 'Sprite 355 ml': 1}
    assert app.PEDIDOS_CONFIRMADOS[1]['bebidas'] == {}


if __name__ == '__main__':
    test_bebidas_seleccionadas_no_se_mezclan_en_pedidos_nuevos()
