class AutoInit:
    def __init__(self, **args):
        for (k, v) in args.items():
            if not hasattr(self, k):
                raise RuntimeError("Unknown attribute: ", k)
            setattr(self, k, v)
