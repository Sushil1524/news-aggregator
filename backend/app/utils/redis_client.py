"""Redis client factory that supports:
- normal redis:// or rediss:// URLs via `redis` library
- Upstash REST API via `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN`

When the REST variables are present the adapter will call Upstash REST
endpoints so you don't need a local Redis server.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import json
import requests
import redis as redis_lib
from typing import Any


class UpstashRESTClient:
    def __init__(self, rest_url: str, token: str):
        self.base = rest_url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def _command(self, *args):
        url = f"{self.base}/command"
        # Try several payload shapes commonly used with Upstash REST
        attempts = []
        attempts.append(list(args))                  # JSON array like ["INCR","key"]
        attempts.append({"cmd": list(args)})       # {"cmd": [..]}
        attempts.append({"command": list(args)})   # {"command": [..]}
        attempts.append({"commands": [list(args)]})

        last_resp = None
        for payload in attempts:
            try:
                resp = requests.post(url, json=payload, headers=self.headers, timeout=5)
                last_resp = resp
                if resp.status_code >= 400:
                    # not successful; try next shape
                    # log the response body for debugging
                    text = None
                    try:
                        text = resp.text
                    except Exception:
                        text = '<no body>'
                    print(f"[UpstashREST] {resp.status_code} for payload {payload}: {text}")
                    continue

                # success
                try:
                    data = resp.json()
                except Exception:
                    return resp.text

                # Upstash returns results in different keys sometimes; prefer 'result'
                if isinstance(data, dict):
                    if 'result' in data:
                        return data['result']
                    if 'output' in data:
                        return data['output']
                    return data
                return data
            except requests.exceptions.RequestException as e:
                print(f"[UpstashREST] request failed for payload {payload}: {e}")
                last_resp = None
                continue

        # If we reach here, all attempts failed — log last response details
        if last_resp is not None:
            try:
                print(f"[UpstashREST] final response: {last_resp.status_code} {last_resp.text}")
            except Exception:
                print("[UpstashREST] final response unreadable")
        else:
            print(f"[UpstashREST] no response received for command {args}")
        return None

    # Minimal set of operations used by the app
    def incr(self, key: str):
        return self._command("INCR", key)

    def hset(self, key: str, field: str, value: str):
        return self._command("HSET", key, field, value)

    def expire(self, key: str, seconds: int):
        return self._command("EXPIRE", key, seconds)

    def hgetall(self, key: str):
        res = self._command("HGETALL", key)
        # Upstash returns list: [field1, val1, field2, val2]
        if isinstance(res, list):
            it = iter(res)
            out = {}
            for i in range(0, len(res), 2):
                try:
                    k = res[i]
                    v = res[i+1]
                except Exception:
                    break
                out[str(k)] = v
            return out
        if isinstance(res, dict):
            return res
        return {}

    def keys(self, pattern: str):
        res = self._command("KEYS", pattern)
        return res or []

    def get(self, key: str):
        return self._command("GET", key)

    def delete(self, key: str):
        return self._command("DEL", key)


class FallbackProxy:
    """Wraps either a redis-py client or UpstashRESTClient and provides
    the same method names used in the services.
    """
    def __init__(self, client: Any):
        self._client = client

    def __getattr__(self, name: str):
        def _call(*args, **kwargs):
            try:
                attr = getattr(self._client, name)
                return attr(*args, **kwargs)
            except Exception as e:
                print(f"[RedisAdapter] {name} failed: {e}")
                # Conservative defaults used by services
                if name == 'keys':
                    return []
                if name == 'hgetall':
                    return {}
                return None

        return _call


def get_redis_client():
    """Return an adapter that implements the minimal Redis operations used
    by the app. Prefers Upstash REST if `UPSTASH_REDIS_REST_URL` + token
    are present. Otherwise tries `UPSTASH_REDIS_URL` / `REDIS_URL` via
    redis-py, then falls back to localhost redis.
    """
    # Prefer the standard redis TLS URL (works with redis-py) if present
    redis_url = os.getenv('UPSTASH_REDIS_URL') or os.getenv('REDIS_URL')
    if redis_url:
        try:
            client = redis_lib.from_url(redis_url, decode_responses=True)
            return FallbackProxy(client)
        except Exception as e:
            print(f"[RedisAdapter] redis client creation failed for URL {redis_url}: {e}")

    # Fall back to Upstash REST if provided
    rest_url = os.getenv('UPSTASH_REDIS_REST_URL')
    rest_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    if rest_url and rest_token:
        return FallbackProxy(UpstashRESTClient(rest_url, rest_token))

    # As a last resort, try local Redis
    try:
        client = redis_lib.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True,
        )
        return FallbackProxy(client)
    except Exception as e:
        print(f"[RedisAdapter] redis client creation failed for localhost: {e}")
        # If REST info exists, return REST client; otherwise return a null proxy
        if rest_url and rest_token:
            return FallbackProxy(UpstashRESTClient(rest_url, rest_token))
        return FallbackProxy(None)


__all__ = ['get_redis_client']
