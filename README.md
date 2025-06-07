# PumpFun Watcher

**PumpFun Watcher** is a Python module for real-time monitoring of tokens on the [Pump.fun](https://pump.fun/) Solana launchpad. It provides instant live price updates from the bonding curve by connecting to Solana RPC/WebSocket endpoints. This tool is for bot developers, traders, and anyone who wants timely, automatic price data for any PumpFun-launched SPL token.

> _Open-sourced due to the lack of public, easy-to-use resources for programmatic PumpFun monitoring._

---

## Features

- **Realtime Price Monitoring:** Instantly receive price updates from the PumpFun bonding curve.
- **Automatic Decimal Handling:** Correctly parses SPL token decimals for accurate price reporting.
- **Bonding Curve Account Decoding:** Decodes PumpFun bonding curve account data on the fly.
- **WebSocket Support:** Handles reconnects and live feed robustness.
- **Helper Utilities:** Includes a script to fetch the correct bonding curve address for any mint.

---

## Usage

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Get the Bonding Curve Address for Your Token

Use the included helper:

```python
from fetch_pair_addr import fetch_pair_addr

mint = "YourTokenMintHere"
curve_addr = fetch_pair_addr(mint)
print("Bonding curve address:", curve_addr)
```

### 3. Run the Watcher

```python
import asyncio
from pumpfun_watcher import watch_pumpfun_curve

async def handle_price(price):
    print("Live price:", price)

CURVE_ADDR = "YourCurveAddressHere"
mint = "YourTokenMintHere"
asyncio.run(watch_pumpfun_curve(CURVE_ADDR, mint, handle_price))
```

---

## Modules

- **pumpfun_watcher.py**  
  Main module for connecting and decoding PumpFun bonding curves.
  - `watch_pumpfun_curve(curve_addr, mint, callback)` – calls your callback on every price update.

- **fetch_pair_addr.py**  
  Helper to get the PumpFun bonding curve address for any SPL token mint, using the [Dexscreener API](https://api.dexscreener.com/).

---

## Example: Full Script

```python
from fetch_pair_addr import fetch_pair_addr
from pumpfun_watcher import watch_pumpfun_curve
import asyncio

async def print_price(price):
    print("Live price:", price)

mint = "YourTokenMintHere"
curve_addr = fetch_pair_addr(mint)
if curve_addr:
    asyncio.run(watch_pumpfun_curve(curve_addr, mint, print_price))
else:
    print("Bonding curve not found on Dexscreener.")
```

---

## Why Open Source?

There are almost no open resources for real-time on-chain monitoring of PumpFun tokens. This code is for devs, bot builders, and anyone who wants direct, fast access to the PumpFun bonding curve.

**PRs, issues, and forks are welcome!**

---

## Disclaimer

- Developer tool: Use at your own risk.
- Test before using with real funds.
- Not affiliated with Pump.fun or Solana.

---

## License

MIT

---

## Credits

- [construct](https://construct.readthedocs.io/)
- [websockets](https://websockets.readthedocs.io/)
- [Dexscreener](https://dexscreener.com/)
