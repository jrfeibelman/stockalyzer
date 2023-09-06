class ConfigurationManager:

    def __new__(cls):
        if not cls.hasInstance():
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def hasInstance(cls) -> bool:
        return hasattr(cls, '_instance')

    def initialize(self, config):
        self._enforce_controls = config.get_value('EnforceControls', False)
        return True

    def get_enforce_controls(self):
        return self._enforce_controls