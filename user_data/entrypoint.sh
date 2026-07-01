#!/bin/bash
echo "[entrypoint] Patching CCXT keysort..."

python3 << 'PYEOF'
import re

path = '/home/ftuser/.local/lib/python3.14/site-packages/ccxt/base/exchange.py'
with open(path, 'r') as f:
    content = f.read()

old = 'return dict(sorted(dictionary.items()))'
new = 'return dict(sorted(dictionary.items(), key=lambda kv: (str(kv[0]) if kv[0] is not None else "")))'

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print('CCXT keysort patched successfully')
else:
    print('CCXT keysort already patched or pattern not found')
PYEOF

echo "[entrypoint] Registering MeanRevertFilter..."

python3 << 'PYEOF'
import shutil, re

# 1. Copy custom filter to built-in pairlist directory
src = '/freqtrade/user_data/pairlists/MeanRevertFilter.py'
dst = '/freqtrade/freqtrade/plugins/pairlist/MeanRevertFilter.py'
shutil.copy2(src, dst)
print(f'MeanRevertFilter.py copied to {dst}')

# 2. Patch AVAILABLE_PAIRLISTS in constants.py
const_path = '/freqtrade/freqtrade/constants.py'
with open(const_path, 'r') as f:
    content = f.read()

old = '"VolatilityFilter",\n]'
new = '"VolatilityFilter",\n    "MeanRevertFilter",\n]'

if 'MeanRevertFilter' not in content:
    content = content.replace(old, new)
    with open(const_path, 'w') as f:
        f.write(content)
    print('AVAILABLE_PAIRLISTS patched: MeanRevertFilter added')
else:
    print('AVAILABLE_PAIRLISTS already contains MeanRevertFilter')
PYEOF

echo "[entrypoint] Starting freqtrade..."
exec freqtrade trade \
  --logfile /freqtrade/user_data/logs/freqtrade.log \
  --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite \
  --config /freqtrade/user_data/config.json \
  --config /freqtrade/user_data/config.private.json \
  --strategy E0V1E
