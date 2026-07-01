import ccxt, numpy as np, json, requests, time, random

exchange = ccxt.okx({'options': {'defaultType': 'swap'}})
r = requests.get('http://freqtrader:123@localhost:8080/api/v1/whitelist')
wl = json.loads(r.text)['whitelist']
random.seed(42)
sample = random.sample(wl, min(12, len(wl)))

print(f'{"Pair":<20} {"daily_range%":>10} {"swings/d":>8} {"bounce_3h%":>9} {"vol":>7} {"score":>7}')
print('-'*65)

for pair in sample:
    try:
        # 1h data for 30 days
        data = exchange.fetch_ohlcv(pair, '1h', limit=720)
        if len(data) < 300:
            print(f'{pair:<20} insuff data')
            continue
        closes = np.array([c[4] for c in data])
        highs = np.array([c[2] for c in data])
        lows = np.array([c[3] for c in data])
        
        # Daily range (average)
        ranges = (highs - lows) / closes * 100
        avg_range = np.mean(ranges)
        
        # Swings: how often does price dip 3% then recover 1.5%+ within 3 candles (3h)
        swings = 0
        bounces = 0
        for i in range(len(closes)-6):
            # Check 3-candle dip
            low3 = np.min(lows[i:i+3])
            close_before = closes[max(0,i-1)]
            dip_pct = (close_before - low3) / close_before * 100
            if dip_pct >= 3:
                swings += 1
                # Recovery within next 3 candles
                high_next3 = np.max(highs[i+3:i+6]) if i+6 <= len(highs) else np.max(highs[i+3:])
                if (high_next3 - low3) / low3 * 100 >= 1.5:
                    bounces += 1
        
        days = len(data)/24
        swings_per_day = swings/days if days>0 else 0
        bounce_rate = bounces/swings*100 if swings>0 else 0
        
        # 20d vol
        od = exchange.fetch_ohlcv(pair, '1d', limit=25)
        cd = np.array([c[4] for c in od])
        rd = np.diff(cd)/cd[:-1]
        vol = np.std(rd)*np.sqrt(20)
        
        score = swings_per_day * bounce_rate/100 * 10
        print(f'{pair:<20} {avg_range:>9.2f}% {swings_per_day:>7.1f} {bounce_rate:>8.0f}% {vol:>6.3f} {score:>6.1f}')
    except Exception as e:
        print(f'{pair:<20} {e}')
    time.sleep(0.3)
