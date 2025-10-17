"""Simple pagination helpers for controller endpoints.

Supports opaque tokens (base64-encoded JSON) and an in-memory fallback
pagination for iterables (useful when model methods are mocked in tests).

Token shape examples:
 - {'type': 'offset', 'offset': 100}
 - {'type': 'last_key', 'key': {...}}  # reserved for pynamodb last_evaluated_key
"""
import base64
import json
from typing import Any, Iterable, List, Optional, Tuple


def encode_token(obj: Any) -> str:
    raw = json.dumps(obj, separators=(',', ':')).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii')


def decode_token(token: str) -> Any:
    try:
        raw = base64.urlsafe_b64decode(token.encode('ascii'))
        return json.loads(raw.decode('utf-8'))
    except Exception as e:
        raise ValueError('Invalid pagination token') from e


def paginate_list(items: Iterable[Any], limit: int, token: Optional[str]) -> Tuple[List[Any], Optional[str]]:
    """Paginate an in-memory list/iterable using offset tokens.

    Returns (page_items, next_token_or_None).
    If token is None, starts at offset 0.
    """
    lst = list(items)
    offset = 0
    if token:
        decoded = decode_token(token)
        if not isinstance(decoded, dict) or decoded.get('type') != 'offset':
            raise ValueError('Unsupported token type for in-memory pagination')
        offset = int(decoded.get('offset', 0))

    start = offset
    end = start + limit
    page = lst[start:end]
    if end < len(lst):
        next_token = encode_token({'type': 'offset', 'offset': end})
    else:
        next_token = None
    return page, next_token
