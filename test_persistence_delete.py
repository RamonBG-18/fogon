import json
from pathlib import Path
from app import app, DATA_FILE

client = app.test_client()
# ensure clean start
if DATA_FILE.exists():
    DATA_FILE.unlink()

# create pedido
resp = client.post('/pedido/1', data={'nombre':'PersistTest','metodo_pago':'Tarjeta'})
assert resp.status_code == 302
# check file exists and contains the order
assert DATA_FILE.exists()
data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
assert any(p['cliente']=='PersistTest' for p in data)
print('created', len(data))
# find id
pid = next(p['id'] for p in data if p['cliente']=='PersistTest')
# delete
resp2 = client.post(f'/pedidos/eliminar/{pid}')
assert resp2.status_code == 302
# verify removed
data2 = json.loads(DATA_FILE.read_text(encoding='utf-8'))
print('after delete', len(data2))
assert not any(p['id']==pid for p in data2)
print('OK')
