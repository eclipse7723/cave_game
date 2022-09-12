class SingletonMeta(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance[cls.__name__] = instance
        return cls._instance[cls.__name__]
