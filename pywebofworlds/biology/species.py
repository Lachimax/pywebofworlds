import pywebofworlds.utils as u
import pywebofworlds.params as p
from pywebofworlds import BaseObject

class Species(BaseObject):
    def __init__(
            self,
            identifier: str = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.fertility_rate = 3