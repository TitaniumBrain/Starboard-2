import time


class Cooldown:
    __slots__ = ("rate", "per", "_window", "_tokens", "_last")

    def __init__(self, rate, per):
        self.rate = int(rate)
        self.per = float(per)
        self._window = 0.0
        self._tokens = self.rate
        self._last = 0.0

    def get_tokens(self, current=None):
        if not current:
            current = time.time()

        tokens = self._tokens

        if current > self._window + self.per:
            tokens = self.rate
        return tokens

    def get_retry_after(self, current=None):
        current = current or time.time()
        tokens = self.get_tokens(current)

        if tokens == 0:
            return self.per - (current - self._window)

        return 0.0

    def update_rate_limit(self, current=None):
        current = current or time.time()
        self._last = current

        self._tokens = self.get_tokens(current)

        # first token used means that we start a new rate limit window
        if self._tokens == self.rate:
            self._window = current

        # check if we are rate limited
        if self._tokens == 0:
            return self.per - (current - self._window)

        # we're not so decrement our tokens
        self._tokens -= 1

        # see if we got rate limited due to this token change, and if
        # so update the window to point to our current time frame
        if self._tokens == 0:
            self._window = current

    def reset(self):
        self._tokens = self.rate
        self._last = 0.0

    def copy(self):
        return Cooldown(self.rate, self.per)

    def __repr__(self):
        return (
            f"<Cooldown rate: {self.rate} per: {self.per} window: "
            f"{self._window} tokens: {self._tokens}>"
        )


class FlexibleCooldownMapping:
    """Same as CooldownMapping, but each key can have
    a different rate/per setting"""

    def __init__(self):
        self._cache: dict[str, "Cooldown"] = {}

    def copy(self):
        ret = FlexibleCooldownMapping()
        ret._cache = self._cache.copy()
        return ret

    @staticmethod
    def _bucket_key(cooldown_key):
        return cooldown_key

    def _verify_cache_integrity(self, current=None):
        # we want to delete all cache objects that haven't been used
        # in a cooldown window. e.g. if we have a  command that has a
        # cooldown of 60s and it has not been used in 60s then that
        # key should be deleted
        current = current or time.time()
        dead_keys = [
            k for k, v in self._cache.items() if current > v._last + v.per
        ]
        for k in dead_keys:
            del self._cache[k]

    def get_bucket(self, cooldown_key, rate, per, current=None) -> Cooldown:
        self._verify_cache_integrity(current)
        key = self._bucket_key(cooldown_key)
        if key not in self._cache:
            bucket = Cooldown(rate, per)
            self._cache[key] = bucket
        else:
            bucket = self._cache[key]

        return bucket

    def update_rate_limit(self, cooldown_key, rate, per, current=None):
        bucket = self.get_bucket(cooldown_key, rate, per, current)
        return bucket.update_rate_limit(current)


class CooldownMapping:
    def __init__(self, original: "Cooldown"):
        self._cache = {}
        self._cooldown = original

    def copy(self):
        ret = CooldownMapping(self._cooldown)
        ret._cache = self._cache.copy()
        return ret

    @property
    def valid(self):
        return self._cooldown is not None

    @classmethod
    def from_cooldown(cls, rate, per):
        return cls(Cooldown(rate, per))

    @staticmethod
    def _bucket_key(cooldown_key):
        return cooldown_key

    def _verify_cache_integrity(self, current=None):
        # we want to delete all cache objects that haven't been used
        # in a cooldown window. e.g. if we have a  command that has a
        # cooldown of 60s and it has not been used in 60s then that
        # key should be deleted
        current = current or time.time()
        dead_keys = [
            k for k, v in self._cache.items() if current > v._last + v.per
        ]
        for k in dead_keys:
            del self._cache[k]

    def get_bucket(self, cooldown_key, current=None):
        self._verify_cache_integrity(current)
        key = self._bucket_key(cooldown_key)
        if key not in self._cache:
            bucket = self._cooldown.copy()
            self._cache[key] = bucket
        else:
            bucket = self._cache[key]

        return bucket

    def update_rate_limit(self, cooldown_key, current=None):
        bucket = self.get_bucket(cooldown_key, current)
        return bucket.update_rate_limit(current)
