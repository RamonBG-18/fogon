from app import app, DATA_FILE
import json
client = app.test_client()
if DATA_FILE.exists():
    DATA_FILE.unlink()
# clear in-memory list
from app import PEDIDOS_CONFIRMADOS
PEDIDOS_CONFIRMADOS.clear()
client.post('/pedido/1', data={'nombre':'A','metodo_pago':'Efectivo'})
client.post('/pedido/2', data={'nombre':'B','metodo_pago':'Tarjeta'})
client.post('/pedido/3', data={'nombre':'C','metodo_pago':'Transferencia'})
# set timestamps
data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
data[0]['timestamp'] = '2025-12-31T00:00:00Z'
data[1]['timestamp'] = '2026-06-01T12:00:00Z'
data[2]['timestamp'] = '2026-06-15T09:30:00Z'
DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
from app import PEDIDOS_CONFIRMADOS
PEDIDOS_CONFIRMADOS[:] = data

r = client.get('/pedidos?date_from=2026-06-01')
print('--- /pedidos?date_from=2026-06-01 ---')
print(r.status_code)
print(r.get_data(as_text=True))

r2 = client.get('/pedidos?order=oldest')
print('--- /pedidos?order=oldest ---')
print(r2.status_code)
print(r2.get_data(as_text=True))
