class Observable:
    def __init__(self):
        self.observers = []

    def notify_observers(self, **kwargs):
        for observer in self.observers:
            observer.update(**kwargs)

    def set_observer(self, observer):
        self.observers.append(observer)
