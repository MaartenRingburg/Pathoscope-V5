# backend/modules/presets.py
import json
import os

PRESETS_FILE = 'presets.json'

def load_presets():
    if not os.path.exists(PRESETS_FILE):
        return {}
    return json.load(open(PRESETS_FILE))

def save_preset(name, config):
    p = load_presets()
    p[name] = config
    json.dump(p, open(PRESETS_FILE, 'w'))

def delete_preset(name):
    p = load_presets()
    if name in p:
        p.pop(name)
        json.dump(p, open(PRESETS_FILE, 'w'))