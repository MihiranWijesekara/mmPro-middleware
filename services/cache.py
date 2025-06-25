from diskcache import Cache
import os

# Prefer env-defined writable directory
cache_dir = os.getenv('CACHE_DIR', os.getenv('DISKCACHE_DIR', './.cache'))

try:
    os.makedirs(cache_dir, exist_ok=True)
    try:
        os.chmod(cache_dir, 0o755)
    except PermissionError:
        pass
        
    cache = Cache(cache_dir)
except Exception as e:
    print(f"Error initializing cache: {e}")
    # Fallback only if initial path fails
    fallback_dir = '/tmp/otp_cache'
    os.makedirs(fallback_dir, exist_ok=True)
    cache = Cache(fallback_dir)

# Ensure the cache is writable
