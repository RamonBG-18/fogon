from app import app, DATA_FILE


def reset_state():
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    app.PEDIDOS_CONFIRMADOS = []


def test_flujo_completo_del_pedido_con_bebidas():
    reset_state()
    client = app.test_client()

    resp_page = client.get('/pedido/1')
    assert resp_page.status_code == 302
    assert resp_page.headers['Location'].endswith('/bebidas')

    resp_bebidas = client.post('/bebidas', data={'cantidad_Coca 600 ml': '2', 'cantidad_Sprite 355 ml': '1'})
    assert resp_bebidas.status_code == 302
    assert '/bebidas/confirmacion' in resp_bebidas.headers['Location']

    resp_confirm = client.post('/bebidas/confirmacion')
    assert resp_confirm.status_code == 302
    assert '/pedido/1/completar' in resp_confirm.headers['Location']

    resp_form = client.post('/pedido/1/completar', data={
        'nombre': 'ClientePrueba',
        'metodo_pago': 'Efectivo',
        'telefono': '5512345678',
        'domicilio': 'Calle 123',
    })
    assert resp_form.status_code == 302
    assert '/pedido/1/confirmacion' in resp_form.headers['Location']

    resp_finalize = client.post('/pedido/1/confirmacion')
    assert resp_finalize.status_code == 302
    assert resp_finalize.headers['Location'].endswith('/pedidos')

    pedidos = app.PEDIDOS_CONFIRMADOS
    assert len(pedidos) == 1
    assert pedidos[0]['cliente'] == 'ClientePrueba'
    assert pedidos[0]['bebidas'] == {'Coca 600 ml': 2, 'Sprite 355 ml': 1}


if __name__ == '__main__':
    test_flujo_completo_del_pedido_con_bebidas()
