
import inspect

def s(template, **kwargs):
    "Usage: s(string, **locals())"
    if not kwargs:
        frame = inspect.currentframe()
        try:
            kwargs = frame.f_back.f_locals
        finally:
            del frame
        if not kwargs:
            kwargs = globals()
    return template.format(**kwargs)


