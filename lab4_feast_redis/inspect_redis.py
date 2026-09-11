import os
import sys
import redis
from tabulate import tabulate

def inspect_redis():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", 6379))
    
    print(f"Connecting to Redis at {host}:{port}...")
    try:
        r = redis.Redis(host=host, port=port, decode_responses=False)
        r.ping()
        print("Connected to Redis successfully.\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure Redis is running (docker compose up -d redis)")
        return

    # Database overview
    dbsize = r.dbsize()
    info = r.info("memory")
    used_mem = info.get("used_memory_human", "N/A")
    peak_mem = info.get("used_memory_peak_human", "N/A")

    print("=" * 65)
    print("REDIS STORAGE OVERVIEW")
    print("=" * 65)
    print(f"Total Keys:        {dbsize}")
    print(f"Used Memory:       {used_mem}")
    print(f"Peak Memory:       {peak_mem}")
    print("=" * 65)

    # Scan for Feast keys
    cursor, keys = r.scan(cursor=0, count=50)
    print(f"\nDiscovered {len(keys)} keys in active scan:")

    key_rows = []
    for k in keys[:15]:
        k_type = r.type(k).decode("utf-8")
        ttl = r.ttl(k)
        ttl_str = "No Expiry (-1)" if ttl == -1 else f"{ttl}s"
        
        # Display key representation
        try:
            readable_key = k.decode("utf-8")
        except UnicodeDecodeError:
            readable_key = repr(k)[:40] + "..."
            
        if k_type == "hash":
            num_fields = r.hlen(k)
            detail = f"{num_fields} feature fields"
        elif k_type == "string":
            val_len = len(r.get(k))
            detail = f"{val_len} bytes"
        else:
            detail = k_type

        key_rows.append([readable_key, k_type, ttl_str, detail])

    headers = ["Key", "Type", "TTL", "Content Summary"]
    print(tabulate(key_rows, headers=headers, tablefmt="fancy_grid"))
    
    if len(keys) > 15:
        print(f"\n... and {len(keys) - 15} more keys.")

if __name__ == "__main__":
    inspect_redis()
