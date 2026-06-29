import json
from pathlib import Path
from app import app, DATA_FILE

client = app.test_client()
# reset
if DATA_FILE.exists():
    DATA_FILE.unlink()
# clear in-memory list in case app already loaded data
app.PEDIDOS_CONFIRMADOS = []
DATA_FILE.write_text('[]', encoding='utf-8')

# create deterministic pedidos data directly on disk (no POSTs)
data = [
    {
        'id': 'idA', 'paquete_id': 1, 'paquete_nombre': 'Paquete Familiar', 'cliente': 'A', 'metodo_pago': 'Efectivo', 'timestamp': '2025-12-31T00:00:00Z'
    },
    {
        'id': 'idB', 'paquete_id': 2, 'paquete_nombre': 'Combo Compadres', 'cliente': 'B', 'metodo_pago': 'Tarjeta', 'timestamp': '2026-06-01T12:00:00Z'
    },
    {
        'id': 'idC', 'paquete_id': 3, 'paquete_nombre': 'Clásico Norteño', 'cliente': 'C', 'metodo_pago': 'Transferencia', 'timestamp': '2026-06-15T09:30:00Z'
    }
]
DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
app.PEDIDOS_CONFIRMADOS = data

# filter date_from 2026-06-01 should include B and C but not A
r = client.get('/pedidos?date_from=2026-06-01')
assert r.status_code == 200
text = r.get_data(as_text=True)
print('DEBUG /pedidos?date_from=2026-06-01')
print(text)
assert 'B' in text and 'C' in text and 'A' not in text

# order oldest should show A then B then C
r2 = client.get('/pedidos?order=oldest')
assert r2.status_code == 200
text2 = r2.get_data(as_text=True)
print('DEBUG /pedidos?order=oldest')
print(text2)
# ensure A appears before B and B before C by checking positions using the
# client label to avoid accidental matches in button text
sa = text2.index('Cliente:</strong> A')
sb = text2.index('Cliente:</strong> B')
sc = text2.index('Cliente:</strong> C')
assert sa < sb < sc

print('DATE & SORT OK')
