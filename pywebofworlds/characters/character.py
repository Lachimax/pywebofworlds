import random as r
from typing import Union

import numpy as np

import pywebofworlds.params as p
import pywebofworlds.history as t
import pywebofworlds.biology.species as species
from pywebofworlds import BaseObject

from .demographic import DemographicSet
from .list import CharacterList

# TODO: Account for mixed ethnicities
# TODO: Choose and implement sexuality model
# TODO: gender model
# TODO: Automatic rebalance of random generation depending on in-use characters.
# TODO: Allow more flexible distributions of continuous traits - parent class DemographicSet with DiscreteDemoSet and
#   ContinuousDemoSet as subclasses? Eg for sexuality / gender, on spectra; age. Allow to specify distribution type
# TODO: Allow correlation of demographics - for example, rates of homosexuality and bisexuality differ between males and
#  females.

# TODO: Maybe implement a class for location, incorporating date systems, demographics etc - maybe integrate with maps
#   module.

# TODO: Name generator (from list from file)

registry = p.load_registry(obj_type="characters")
active = {}
character_dir = p.data_subdir(obj_type="characters", category="characters")


def update_registry():
    return p.update_registry(
        registry=registry,
        obj_type="characters",
        category="characters"
    )


def save_registry():
    p.save_registry(obj_type="characters", registry=registry)


# TODO: Rewrite all Character and CharacterList methods involving Demographics to allow a dictionary to be accepted, and
#   turned into a Demographic object in-method.


class Character(BaseObject):
    active_dict = active
    registry_dict = registry
    path_slug = "characters"
    category = "characters"

    def __init__(
            self,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.dob: t.Date = None
        if "dob" in kwargs:
            self.dob = t.Date(kwargs["dob"])

        # TODO: Account for non-biological parents, eg adoption
        self.mother: Character = None
        self.father: Character = None
        self.children: list = []
        self.traits: dict = {}
        self.used: bool = False

        self.character_set: CharacterList = None
        if "character_set" in kwargs:
            self.character_set = kwargs["character_set"]

        self.species: species.Species = None
        if "species" in kwargs:
            self.species = species.Species(kwargs["species"])

    def __str__(self):
        string = ''
        string += f'Name: {self.name}\n'
        string += f'Used: {self.used}\n'
        string += f'D.O.B.: {self.dob}\n'
        for trait in self.traits:
            string += f'{trait}: {self[trait]}\n'

        return string

    def __getitem__(self, item: str):
        return self.traits[item]

    def __setitem__(self, key: str, value):
        self.traits[key] = value

    # TODO: Option to rovide own distribution of ages
    def gen_dob(self, year, system: str = 'Gregorian', sigma: float = 34.):
        """
        Generate a date-of-birth, assuming the distribution of age is a Gaussian.
        :param year: Year of current setting.
        :param system: Date system.
        :param sigma: Standard deviation of age distribution; default is 34, for human populations.
        :return:
        """
        dob = t.Date(system=system)
        # TODO: Improve model of population age distribution. Probably has a flatter distribution that becomes a
        #  Gaussian for higher ages
        age = abs(np.random.normal(scale=sigma))
        yob = year - age
        dob.rand_date()
        dob.set_year(yob)

        self.dob = dob

    def trait_from_demographic(self, demographic_set: Union[DemographicSet, dict], trait: str = None):
        """
        Generate a character trait from a DemographicSet.
        :param trait: Name of trait.
        :param demographic_set: DemographicSet or dict containing demographic statistics.
        :return:
        """
        if type(demographic_set) is dict:
            if trait is None:
                raise ValueError('If demographics is a dict, trait must be provided.')
            else:
                demographic_set = DemographicSet(demographics=demographic_set, trait=trait)
        elif type(demographic_set) is not DemographicSet:
            raise TypeError('demographics must be dict or DemographicSet.')

        trait = demographic_set.trait
        demographic_set.check_sum()

        population = []
        for name in demographic_set.demographics:
            # TODO: This will only work to the nearest percent. Find a way around that?
            for j in range(int(np.round(100 * demographic_set[name]))):
                population.append(name)

        self[trait] = r.choice(population)

    def _generate_id(self, n: int = 0):
        return f"{self.dob.__str__()}_{self.name}_{n}"

