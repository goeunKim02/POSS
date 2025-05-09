class EventBus :
    listeners = {}

    @classmethod
    def on(cls, event, callback) :
        if event not in cls.listeners :
            cls.listeners[event] = []
        cls.listeners[event].append(callback)

    @classmethod
    def off(cls, event, callback=None) :
        if event in cls.listeners :
            if callback :
                cls.listeners[event].remove(callback)
            else :
                cls.listeners[event] = []

    @classmethod
    def emit(cls, event, *args, **kwargs) :
        if event in cls.listeners :
            for callback in cls.listeners[event] :
                callback(*args, **kwargs)