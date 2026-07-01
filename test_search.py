from pathlib import Path
import json
from app import app, DATA_FILE

client = app.test_client()
# reset
if DATA_FILE.exists():
    DATA_FILE.unlink()
# create several pedidos
client.post('/pedido/1', data={'nombre':'Alice','metodo_pago':'Efectivo'})
client.post('/pedido/1/bebida', data={'agregar_bebida':'si'})
client.post('/pedido/1/confirmacion')
client.post('/pedido/2', data={'nombre':'Bob','metodo_pago':'Tarjeta'})
client.post('/pedido/2/bebida', data={'agregar_bebida':'no'})
client.post('/pedido/2/confirmacion')
client.post('/pedido/3', data={'nombre':'Carlos','metodo_pago':'Transferencia'})
client.post('/pedido/3/bebida', data={'agregar_bebida':'si'})
client.post('/pedido/3/confirmacion')

r_all = client.get('/pedidos')
assert r_all.status_code == 200
text = r_all.get_data(as_text=True)
assert 'Alice' in text and 'Bob' in text and 'Carlos' in text

r_q = client.get('/pedidos?q=Alice')
assert r_q.status_code == 200
assert 'Alice' in r_q.get_data(as_text=True)
assert 'Bob' not in r_q.get_data(as_text=True)

r_q2 = client.get('/pedidos?q=tarj')
assert r_q2.status_code == 200
assert 'Bob' in r_q2.get_data(as_text=True)
assert 'Alice' not in r_q2.get_data(as_text=True)

print('SEARCH OK')
