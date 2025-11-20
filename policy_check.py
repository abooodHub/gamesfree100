import json
import sys
import os

def load(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def merge(data):
    all_games = []
    for key, d in data.items():
        if not isinstance(d, dict):
            continue
        def add(g):
            all_games.append((key, g))
        if isinstance(d.get('discounted_games'), list):
            for g in d['discounted_games']:
                t = g[6] if len(g) > 6 else ''
                if isinstance(t, str) and '100%' in t:
                    add(g)
        if isinstance(d.get('discounted_list'), list):
            for g in d['discounted_list']:
                t = g[6] if len(g) > 6 else ''
                if isinstance(t, str) and '100%' in t:
                    add(g)
        if key != 'steam':
            for name in ('free_games', 'free_list'):
                if isinstance(d.get(name), list):
                    for g in d[name]:
                        t = g[6] if len(g) > 6 else ''
                        if isinstance(t, str) and ('100%' in t) and ('Coming Soon' not in t) and ('مجاني دائماً' not in t):
                            add(g)
    return all_games

def main():
    epic = load('epic_goods_detail.json')
    gog = load('gog_goods_detail.json')
    steam = load('free_goods_detail.json')
    data = {'epic': epic, 'gog': gog, 'steam': steam}
    merged = merge(data)
    errs = []
    for store, g in merged:
        t = g[6] if len(g) > 6 else ''
        if not (isinstance(t, str) and '100%' in t):
            errs.append((store, g[0] if g else 'unknown', t))
        if isinstance(t, str) and ('Coming Soon' in t or 'مجاني دائماً' in t):
            errs.append((store, g[0] if g else 'unknown', t))
    print(f"merged_count={len(merged)}")
    if errs:
        print("violations=")
        for v in errs[:20]:
            print(f"- {v[0]} | {v[1]} | {v[2]}")
        sys.exit(1)
    print("policy_ok=true")
    sys.exit(0)

if __name__ == '__main__':
    main()