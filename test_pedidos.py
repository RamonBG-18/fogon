from app import app
client = app.test_client()
# submit a test order
client.post('/pedido/1', data={'nombre':'ClienteLocal','metodo_pago':'Efectivo'})
r = client.get('/pedidos')
print(r.status_code)
print('ClienteLocal' in r.get_data(as_text=True))
