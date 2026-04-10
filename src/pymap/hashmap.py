"""
pymap – a hand-rolled HashMap implemented in pure Python.

Collision resolution  : separate chaining (each bucket is a list of (key, value) pairs)
Default capacity      : 16 buckets
Load-factor threshold : 0.75  →  triggers automatic rehashing (doubling)
"""

from __future__ import annotations

from typing import Any, Generator, Hashable, Optional


_DELETED = object()  # sentinel – not used in chaining, kept for future open-addr variant


class HashMap:
    """Hash map with separate chaining and automatic rehashing."""

    DEFAULT_CAPACITY: int = 16
    LOAD_FACTOR: float = 0.75

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        self._capacity: int = capacity
        self._size: int = 0
        self._buckets: list[list[tuple[Any, Any]]] = [[] for _ in range(self._capacity)]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _bucket_index(self, key: Hashable) -> int:
        return hash(key) % self._capacity

    def _rehash(self) -> None:
        old_buckets = self._buckets
        self._capacity *= 2
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
        for bucket in old_buckets:
            for k, v in bucket:
                self.put(k, v)

    # ------------------------------------------------------------------
    # Core public API
    # ------------------------------------------------------------------

    def put(self, key: Hashable, value: Any) -> None:
        """Insert or update a key-value pair."""
        idx = self._bucket_index(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._load_factor() >= self.LOAD_FACTOR:
            self._rehash()

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if not found."""
        idx = self._bucket_index(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def remove(self, key: Hashable) -> Any:
        """Remove *key* and return its value; raises KeyError if absent."""
        idx = self._bucket_index(key)
        bucket = self._buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return v
        raise KeyError(key)

    def contains(self, key: Hashable) -> bool:
        """Return True if *key* exists in the map."""
        idx = self._bucket_index(key)
        return any(k == key for k, _ in self._buckets[idx])

    def clear(self) -> None:
        """Remove all entries."""
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

    # ------------------------------------------------------------------
    # Informational
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Number of key-value pairs currently stored."""
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _load_factor(self) -> float:
        return self._size / self._capacity

    def capacity(self) -> int:
        return self._capacity

    def keys(self) -> list[Any]:
        return [k for bucket in self._buckets for k, _ in bucket]

    def values(self) -> list[Any]:
        return [v for bucket in self._buckets for _, v in bucket]

    def items(self) -> list[tuple[Any, Any]]:
        return [(k, v) for bucket in self._buckets for k, v in bucket]

    # ------------------------------------------------------------------
    # Python protocol support
    # ------------------------------------------------------------------

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.put(key, value)

    def __getitem__(self, key: Hashable) -> Any:
        idx = self._bucket_index(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def __delitem__(self, key: Hashable) -> None:
        self.remove(key)

    def __contains__(self, key: object) -> bool:
        return self.contains(key)  # type: ignore[arg-type]

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Generator[Any, None, None]:
        for bucket in self._buckets:
            for k, _ in bucket:
                yield k

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k!r}: {v!r}" for k, v in self.items())
        return f"HashMap({{{pairs}}})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashMap):
            return NotImplemented
        return dict(self.items()) == dict(other.items())