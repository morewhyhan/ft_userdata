import ccxt, numpy as np, time

exchange = ccxt.okx({"options": {"defaultType": "swap"}})
pairs = ["ETH/USDT:USDT", "SOL/USDT:USDT", "DOGE/USDT:USDT", "AAVE/USDT:USDT", "ADA/USDT:USDT", "INTC/USDT:USDT", "XRP/USDT:USDT", "BNB/USDT:USDT"]

print("Pair                 2h_dips/d  2h_bounce%  1h_range%  Verdict")
print("-" * 68)

for pair in pairs:
    try:
        ohlcv = exchange.fetch_ohlcv(pair, "30m", limit=960)
        if len(ohlcv) < 200:
            print("%s  insuff data" % pair)
            continue
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        rng = (highs - lows) / closes * 100
        avg_range = float(np.mean(rng))
        dips = 0
        bounces = 0
        w = 4  # 4 x 30m = 2h
        for i in range(w, len(closes) - w - 1):
            prev = closes[i - w]
            dip_low = np.min(lows[i : i + w])
            dip_pct = (prev - dip_low) / prev * 100
            if dip_pct >= 1.5:
                dips += 1
                fut_hi = np.max(highs[i + w : i + w + w])
                rec_pct = (fut_hi - dip_low) / dip_low * 100
                if rec_pct >= 0.75:
                    bounces += 1
        days = len(ohlcv) / 48.0
        dpd = dips / days if days > 0 else 0
        br = bounces / dips * 100 if dips > 0 else 0
        if dpd >= 2 and br >= 60:
            v = "GOOD"
        elif dpd >= 1 and br >= 50:
            v = "OK"
        else:
            v = "TOO STABLE"
        print("%-20s %8.1f %9.0f%% %9.2f%% %15s" % (pair, dpd, br, avg_range, v))
        time.sleep(0.8)
    except Exception as e:
        print("%s  error: %s" % (pair, e))
