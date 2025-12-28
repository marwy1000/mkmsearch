def request_delay(min_seconds: float = 8.0, max_seconds: float = 12.0) -> float:
    import random
    mean = (min_seconds + max_seconds) / 2
    std_dev = (max_seconds - min_seconds) / 6  # 99.7% within range in normal dist

    while True:
        delay = random.normalvariate(mean, std_dev)
        if min_seconds <= delay <= max_seconds:
            return round(delay, 3)