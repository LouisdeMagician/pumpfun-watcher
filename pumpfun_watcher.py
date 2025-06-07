#pumpfun_watcher.py
import asyncio
import websockets
import json
import base64
from construct import Struct, Int64ul, Flag, Bytes
import requests
import os
import logging
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Setup logging
def setup_logger(name="pumpfun_watcher") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
logger = setup_logger()

# Solana endpoints
RPC_URL = os.getenv("SOLANA_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=<your-api-key>")
WS_URL = os.getenv("WS_ENDPOINT", "wss://rpc.helius.xyz/?api-key=<your-api-key>")

# Pump.fun Bonding Curve struct
BondingCurve = Struct(
    "discriminator" / Bytes(8),
    "virtual_token_reserves" / Int64ul,
    "virtual_sol_reserves" / Int64ul,
    "real_token_reserves" / Int64ul,
    "real_sol_reserves" / Int64ul,
    "token_total_supply" / Int64ul,
    "complete" / Flag,
    "creator" / Bytes(32),
)

def get_token_decimals(mint_addr):
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
            "params": [mint_addr, {"encoding": "base64"}]
        }
        resp = requests.post(RPC_URL, json=payload, timeout=5)
        resp.raise_for_status()
        val = resp.json().get("result", {}).get("value")
        if not val or not val.get("data"):
            logger.error("Mint %s not found or not a mint account", mint_addr)
            return 0
        raw = base64.b64decode(val["data"][0])
        return raw[44]  # SPL mint decimals at offset 44
    except Exception as e:
        logger.error("Failed to fetch decimals for %s: %s", mint_addr, str(e))
        return 0

async def watch_pumpfun_curve(pair_addr, token_mint_addr, callback):
    """
    Subscribe to the Pump.fun bonding curve and call `callback(price: Decimal)`
    with each new price (UI style, matches pump.fun/ApePro chart).
    """
    reconnect_delay = 1
    token_decimals = get_token_decimals(token_mint_addr)
    if token_decimals == 0:
        logger.error("Failed to fetch decimals for mint %s", token_mint_addr)
        return

    while True:
        ws = None
        try:
            ws = await websockets.connect(WS_URL)
            logger.info("Connected to WebSocket for bonding curve %s", pair_addr)
            reconnect_delay = 1
            await ws.send(json.dumps({
                "jsonrpc": "2.0", "id": 1, "method": "accountSubscribe",
                "params": [pair_addr, {"encoding": "base64", "commitment": "confirmed"}]
            }))
            msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            if not msg.get("result"):
                raise ValueError("Invalid subscription response")

            while True:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                if msg.get("method") != "accountNotification":
                    continue
                b64_data = msg["params"]["result"]["value"]["data"][0]
                try:
                    raw = base64.b64decode(b64_data)
                    parsed = BondingCurve.parse(raw)
                    v_sol = parsed.virtual_sol_reserves / 1e9  # SOL
                    v_token = parsed.virtual_token_reserves / (10 ** token_decimals)
                    price = v_sol / v_token if v_token else 0
                    display_price = price * 10 if token_decimals == 6 else price
                    price_decimal = Decimal(str(display_price))
                    await callback(price_decimal)
                    logger.info("Live Price: %s", price_decimal)
                except Exception as e:
                    logger.error("Failed to parse bonding curve data for %s: %s", pair_addr, str(e))
                    continue
        except Exception as e:
            logger.error("WebSocket error for bonding curve %s: %s", pair_addr, str(e))
            if ws:
                await ws.close()
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 16)
        finally:
            if ws:
                logger.info("Shutting down WebSocket for bonding curve %s", pair_addr)
                await ws.close()

"""
# Example CLI usage
if __name__ == "__main__":
    import sys
    async def print_price(price): print(f"UI Display Price: {price:.12f} SOL")
    PAIR_ADDRESS = sys.argv[1] if len(sys.argv) > 1 else "8EiGdx3XVeWS6WdurL1pEm3PpHKbBZ9tUMSJKQdkqM29"
    TOKEN_MINT = sys.argv[2] if len(sys.argv) > 2 else "FwZDuAphAwfZz5Myg6zFZCErwkqD1kR9sjU26V3xpump"
    asyncio.run(watch_pumpfun_curve(PAIR_ADDRESS, TOKEN_MINT, print_price))
"""
