import cinesync


class EventHandler:
    def __init__(self, argv, session):
        self.session = session

    @classmethod
    def call_with_fn(cls, argv, session, fn):
        fn(cls(argv, session))
