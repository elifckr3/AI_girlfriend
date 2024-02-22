from enum import Enum
import redis
import logging
import json
from datetime import timedelta, datetime
import datetime as dt

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from string import Template


def is_bytes_not_parquet(data):
    if isinstance(data, bytes):
        return not data.startswith(b"PAR1")

    return False


class RedisConnect(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """
    In-memory > latency with scale
    Key-Value structure optimized
    Concurrency, atomicity, isolation, durability
    """

    host: str = "localhost"

    port: int = 6379

    db: int = 0

    _connection: redis.Redis | None = None
    # _tensor_serializer_context = pa.default_serialization_context()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connection = redis.Redis(host=self.host, port=self.port, db=self.db)

    @property
    def all_keys(self) -> list[str]:
        return [k.decode("utf-8") for k in self._connection.keys("*")]

    def exists(self, key: str) -> bool:
        return self._connection.exists(key)

    def read(self, key: str) -> Any:
        data = self._connection.get(key)

        if data is None:
            logging.error(f"failed to read from Redis - key: {key}")

        if isinstance(data, bytes) and is_bytes_not_parquet(data):
            data = json.loads(data.decode("utf-8"))

        return data

    def read_many(self, base_key: str) -> list[Any]:
        keys = self._connection.keys(f"{base_key}:*")

        logging.debug(f"Reading {len(keys)} keys from Redis")

        results = []
        for key in keys:
            result = self.read(key.decode("utf-8"))
            results.append(result)

        return results

    def write(self, key: str, data: Any):
        # if self.exists(key):
        #     logging.warning(
        #         f"Key '{key}' already exists in Redis. Overriding... (or saving)"
        #     )

        if not isinstance(data, str | bytes):
            data = json.dumps(data)

        res = self._connection.set(key, data)

        if res == 0:
            logging.error(f"failed to write to Redis - key: {key}")

    def delete(self, key: str):
        res = self._connection.delete(key)

        if res == 0:
            logging.error(f"failed to delete from Redis - key: {key}")

    def erase_db(self):
        try:
            self._connection.flushdb()
            logging.info("Entire Redis database erased successfully.")

        except Exception as e:
            logging.error(f"Failed to erase Redis database: {e}")
