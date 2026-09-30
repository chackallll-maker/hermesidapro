import requests, json

for coin in ['ripple','stellar','hedera-hashgraph']:
    mkt = f'https://api.coingecko.com/api/v3/coins/{coin}/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1'
    mr = requests.get(mkt, timeout=15)
    print(f'=== {coin} ===')
    print('status:', mr.status_code)
    try:
        mdata = mr.json()
        print('type:', type(mdata))
        if isinstance(mdata, list):
            lst = mdata[:3]
            for m in lst:
                ex = m.get('market',{}).get('symbol','?') if isinstance(m.get('market'), dict) else '?'
                price = m.get('current_price')
                h1 = m.get('price_change_percentage_1h_in_currency')
                h24 = m.get('price_change_percentage_24h_in_currency')
                vol = m.get('total_volume')
                print(f'  {ex} price={price}  1h%={h1}  24h%={h24}  vol={vol}')
        else:
            print(json.dumps(mdata, indent=2)[:500])
    except Exception as e:
        print('err:', e)
        print(mr.text[:300])
