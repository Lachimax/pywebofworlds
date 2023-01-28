import pywebofworlds.utils as u


class Species:
    def __init__(
            self,
            **kwargs
    ):
        self.fertility_rate = 3

    @classmethod
    def from_file(cls, path: str):
        params = u.load_params(path)
        return cls(**params)
