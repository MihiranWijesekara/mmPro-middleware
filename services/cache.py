import os
from diskcache import Cache

# Use the same env variable name set in Jenkins
cache_dir = os.getenv("CACHE_DIR", "/tmp/otp_cache")

try:
    os.makedirs(cache_dir, exist_ok=True)

    try:
        os.chmod(cache_dir, 0o755)
    except PermissionError:
        pass

    cache = Cache(cache_dir)
except Exception as e:
    print(f"Error initializing cache at {cache_dir}: {e}")
    cache = Cache("/tmp/otp_cache")
