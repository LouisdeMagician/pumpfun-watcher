# fetch_pair_addr.py
import requests

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens"

def fetch_pair_addr(mint: str) -> str | None:
    """
    Fetches the PumpFun bonding curve (pair) address for a given mint using the Dexscreener API.
    Returns the address as a string, or None if not found.
    """
    url = f"{DEXSCREENER_API}/{mint}"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        pairs = data.get("pairs", [])
        # Filter for PumpFun (case-insensitive match)
        for pair in pairs:
            dex_id = pair.get("dexId", "").lower()
            if "pumpfun" in dex_id or "pump-fun" in dex_id:
                return pair.get("pairAddress")
        return None
    except Exception as e:
        print(f"Error fetching bonding curve address for {mint}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    mint = input("Enter mint address: ").strip()
    curve_addr = fetch_pair_addr(mint)
    if curve_addr:
        print("PumpFun bonding curve address:", curve_addr)
    else:
        print("No PumpFun bonding curve found for this mint.")
