from app import app, DATA_FILE

client = app.test_client()
if DATA_FILE.exists():
    DATA_FILE.unlink()
app.PEDIDOS_CONFIRMADOS = []

resp_page = client.get('/pedido/1')
assert resp_page.status_code == 200
text = resp_page.get_data(as_text=True)
assert '¿Deseo agregar una bebida de 2.5 litros?' in text
assert 'No. gracias' in text
assert 'Por favor' in text

resp_bebida = client.post('/pedido/1', data={'agregar_bebida': 'si'})
assert resp_bebida.status_code == 302
assert '/pedido/1/completar' in resp_bebida.headers['Location']

resp_form = client.get('/pedido/1/completar')
assert resp_form.status_code == 200
assert 'Completa tu pedido' in resp_form.get_data(as_text=True)

resp_confirm = client.post('/pedido/1/completar', data={'nombre': 'ClientePrueba', 'metodo_pago': 'Efectivo'})
assert resp_confirm.status_code == 302
assert '/pedido/1/confirmacion' in resp_confirm.headers['Location']

confirm_page = client.get('/pedido/1/confirmacion')
assert confirm_page.status_code == 200
assert 'Confirmar pedido' in confirm_page.get_data(as_text=True)

finalize = client.post('/pedido/1/confirmacion')
assert finalize.status_code == 302
assert finalize.headers['Location'].endswith('/pedidos')

pedidos = app.PEDIDOS_CONFIRMADOS
assert len(pedidos) == 1
assert pedidos[0]['cliente'] == 'ClientePrueba'
assert pedidos[0]['agregar_bebida'] is True
print('BEVERAGE FLOW OK')
