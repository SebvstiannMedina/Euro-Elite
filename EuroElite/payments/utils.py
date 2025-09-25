import hmac
import hashlib

def flow_sign(params: dict, secret_key: str) -> str:
    to_sign = "".join(f"{k}{params[k]}" for k in sorted(params.keys()) if k != "s")
    return hmac.new(secret_key.encode(), to_sign.encode(), hashlib.sha256).hexdigest()
