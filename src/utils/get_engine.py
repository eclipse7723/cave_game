from src.utils.Singelton import SingletonMeta


def get_engine():
    engine_name = "GameEngine"
    engine = SingletonMeta._instance.get(engine_name)
    return engine
