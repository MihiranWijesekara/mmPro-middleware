import os
from diskcache import Cache

# Use only CACHE_DIR, which is set in Jenkins
cache_dir = os.getenv("CACHE_DIR")

if not cache_dir:
    raise EnvironmentError("CACHE_DIR environment variable is not set")

try:
    os.makedirs(cache_dir, exist_ok=True)

    try:
        os.chmod(cache_dir, 0o755)
    except PermissionError:
        pass  # ignore if we can't set permissions

    cache = Cache(cache_dir)
except Exception as e:
    raise RuntimeError(f"Failed to initialize cache at {cache_dir}: {e}")
