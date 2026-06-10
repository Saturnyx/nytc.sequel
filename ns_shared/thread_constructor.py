import threading


def construct_thread(fn, daemon=True) -> threading.Thread:
    cls = fn.__self__.__class__.__name__

    return threading.Thread(
        target=fn, name=f"{fn.__module__}.{cls}.{fn.__name__}", daemon=daemon
    )
