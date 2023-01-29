import os

import pywebofworlds.history as t
import pywebofworlds.params as p

active = {}
registry = {}


class BaseObject:
    active_dict = active
    registry_dict = registry
    path_slug = "base"
    category = "base"

    def __init__(self, **kwargs):
        self.name: str = None
        if "name" in kwargs:
            self.name = str(kwargs["name"])
        self.id: str
        if "id" in kwargs:
            self.id = str(kwargs["id"])
        else:
            self.id = self.generate_id()
        if self.id in self.active_dict:
            self.active_dict[self.id] = self

        self.path: str = None
        if "path" in kwargs:
            self.path = str(kwargs["path"])

    def generate_id(self):
        n = 0
        identifier = self._generate_id(n)
        while identifier in self.registry_dict and self.registry_dict[identifier] != self.path:
            n += 1
            identifier = self._generate_id(n)
        while identifier in self.active_dict and self.active_dict[identifier] is not self:
            n += 1
            identifier = self._generate_id(n)
        return identifier

    def _generate_id(self, n):
        return f"{self.name}_{n}"

    def to_dict(self):
        return self.__dict__.copy()

    def output_dict(self):
        dictionary = self.to_dict().copy()
        for key in dictionary:
            if isinstance(dictionary[key], t.Date):
                dictionary[key] = dictionary[key].__str__()
            if isinstance(dictionary[key], BaseObject):
                dictionary[key] = dictionary[key].id
                # nest this
        return dictionary

    def write(self):
        if self.path is None:
            self.path = self.param_path()
        p.save_params(file=self.path, dictionary=self.output_dict())

    def param_path(self):
        return os.path.join(
            p.data_subdir(obj_type=self.path_slug, category=self.category),
        )

    @classmethod
    def from_file(cls, path: str):
        dictionary = p.load_params(path)
        return cls(path=path, **dictionary)

    @classmethod
    def from_id(cls, identifier: str):
        if identifier in cls.active_dict[identifier]:
            return cls.active_dict[identifier]
        elif identifier in cls.registry_dict:
            return cls.from_file(path=cls.registry_dict[identifier])
        else:
            return None
