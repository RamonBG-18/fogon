from app import app, DATA_FILE

client = app.test_client()
if DATA_FILE.exists():
    DATA_FILE.unlink()
app.PEDIDOS_CONFIRMADOS = []

resp = client.post('/pedido/1', data={'nombre': 'ClienteLocal', 'metodo_pago': 'Efectivo'})
assert resp.status_code == 302
assert '/pedido/1/bebida' in resp.headers['Location']

resp2 = client.post('/pedido/1/bebida', data={'agregar_bebida': 'si'})
assert resp2.status_code == 302
assert '/pedido/1/confirmacion' in resp2.headers['Location']
resp3 = client.post('/pedido/1/confirmacion')
assert resp3.status_code == 302
r = client.get('/pedidos')
print(r.status_code)
print('ClienteLocal' in r.get_data(as_text=True))
