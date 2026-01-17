def ensure_str(s, encoding="utf-8", errors="strict"):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return str(s)


def view_memcached_keys(host="127.0.0.1:11211"):
    from pymemcache.client.base import Client

    # Подключение к Memcached
    client = Client(("127.0.0.1", 11211))

    keys = {}
    for key, val in client.stats("items").items():
        _, slab, field = ensure_str(key).split(":")
        if field != "number" or val == 0:
            continue
        item_request = client.stats("cachedump", slab, str(val + 10))
        for record, details in item_request.items():
            keys[ensure_str(record)] = ensure_str(details)

    print("\n".join(f"{k}: {v}" for k, v in keys.items()))


def view_redis_keys(host="127.0.0.1", port=6379, db=0):
    import redis

    client = redis.Redis(host=host, port=port, db=db)

    keys = client.keys("*")

    for key in keys:
        print(ensure_str(key))

    from pymemcache.client.base import Client
