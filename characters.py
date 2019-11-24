import random as r
import timelines as t
import numpy as np
from typing import Union, Iterable, List
from astropy import table as tbl


# TODO: Account for mixed ethnicities
# TODO: Choose and implement sexuality model
# TODO: gender model
# TODO: Automatic rebalance of random generation depending on in-use characters.
# TODO: Allow more flexible distributions of continuous traits - parent class DemographicSet with DiscreteDemoSet and
#   ContinuousDemoSet as subclasses? Eg for sexuality / gender, on spectra; age
# TODO: Allow correlation of demographics - for example, rates of homosexuality and bisexuality differ between males and
#  females.

# TODO: Maybe implement a class for location, incorporating date systems, demographics etc - maybe integrate with maps
#   module.

class DemographicSet:
    """An object containing a set of mutually exclusive demographics, ideally adding to 100%. Each set contains one
    type of demographic.
    Demographics are given in the form of a dictionary, with the keys as the names of the demographics and the values
    as the percentage they make up.
    """

    def __init__(self, trait: str, demographics: Union[str, dict] = None):
        """
        Initialise the DemographicSet object.
        :param demographics: Either a dictionary containing the demographic information or a path to the file containing
        it.
        :param trait: Name of the demographic type, eg Sex, Ethnicity, Hand, etc.
        """
        self.demographics = {}
        self.trait = str(trait)
        if type(demographics) is dict:
            # Use the dict to set demographic information.
            self.add_demographics(demographics=demographics)
        elif type(demographics) is str:
            # Load the demographics information from file.
            self.read_from_file(demographics)
        else:
            raise TypeError('Demographics must be string or dict.')

    def __getitem__(self, key: str):
        return self.demographics[key]

    def __setitem__(self, key: str, value: float):
        self.demographics[key] = value

    def __str__(self):
        string = ''
        string += str(self.trait) + '\n'
        for name in self.demographics:
            string += self.demographics[name]

    def __len__(self):
        return len(self.demographics.keys())

    def add_demographics(self, demographics: dict):
        """Adds demographics to this DemographicSet and checks the sum of the percentages.
        :param demographics: a dictionary of demographic objects to be added.
        """

        for name in demographics:
            self[name] = float(demographics[name])

        total, check = self.check_sum()

        if not check:
            print("These demographics add to " + str(total) + "%")

    def sum_percentages(self):
        """
        Adds the total of all percentages in the DemographicSet.
        :return: Sum of percentages.
        """
        total = 0.

        for name in self.demographics:
            total += self[name]

        return total

    def check_sum(self, tolerance: float = 0.1):
        """
        Checks that the percentages in a list add up to 100 (or close enough)
        :return: (True if sum is within 0.1 of 100; otherwise False), (total)
        """

        total = self.sum_percentages()
        delta = 100 - total

        return not abs(delta) > tolerance, total

# Default DemographicSets based on Earth, 2016
sexes2016 = DemographicSet(trait='Sex',
                           demographics={'Female': 49.15,
                                         'Male': 49.15,
                                         'Intersex': 1.7})
species2016 = DemographicSet(trait='Species',
                             demographics={'Human': 100})
hands2016 = DemographicSet(trait='Hand',
                           demographics={'Right': 88,
                                         'Left': 10,
                                         'Cross': 1,
                                         'Ambidextrous': 1})

demographics2016 = (sexes2016, hands2016, species2016)


# TODO: Rewrite all Character and CharacterList methods involving Demographics to allow a dictionary to be accepted, and
#   turned into a Demographic object in-method.


class Character:
    def __init__(self, name: str = None):
        self.name = name
        self.dob = t.Date()
        # TODO: Account for non-biological parents, eg adoption
        self.mother = None
        self.father = None
        self.children = list()
        self.traits = {}
        self.used = False

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

    def det_dob(self, year, system: str = 'Julian', sigma: float = 34.):
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
        for name in demographic_set:
            # TODO: This will only work to the nearest percent. Find a way around that?
            for j in range(np.round(100 * demographic_set[name])):
                population.append(name)

        self[trait] = r.choice(population)


class CharacterList:
    # TODO: Implement multiple names
    def __init__(self, characters: Union[List[Character], str] = None, year: int = 2016, location: str = 'Earth',
                 demographics_list: Iterable = demographics2016):

        if characters is None:
            self.characters = []
        if type(characters) is str:
            self.read_from_file(path=characters)
        elif type(characters) is list:
            # TODO: Sanitise types in list
            self.characters = characters
        else:
            raise TypeError('characters must be list or str.')

        self.demographics_list = {}
        if demographics_list is None:
            for demographic_set in demographics_list:
                self.add_demographic_set(demographic_set)

        self.date = t.Date(year=year)
        self.location = location
        if self.location == 'Earth':
            self.system = 'Julian'

    def __getitem__(self, item):
        return self.characters[item]

    def __setitem__(self, key, value):
        self.characters[key] = value

    def __len__(self):
        return len(self.characters)

    def __str__(self):
        string = ""
        for i in range(len(self)):
            string += str(i) + ' ' + str(self.characters[i])
        return string

    def add_demographic_set(self, demographic_set: Union[DemographicSet, dict], trait: str = None):
        """
        Add a set of demographics to the CharacterList.
        :param demographic_set:
        :param trait
        :return:
        """
        if type(demographic_set) is dict:
            if trait is not None:
                demographic_set = DemographicSet(trait=str(trait), demographics=demographic_set)
            else:
                raise ValueError('If demographic_set is dict, trait must be provided.')
        elif type(demographic_set) is not DemographicSet:
            raise TypeError('demographic_set must be dict or DemographicSet, not ' + str(type(demographic_set)))

        self.demographics_list[demographic_set.trait] = demographic_set

    def add_character(self, character: Character):
        """
        Add a Character to the CharacterList
        :param character: Character to add.
        :return:
        """
        self.characters.append(character)

    def generate_character(self, add: bool = True):
        """
        Generate a Character with random demographics using those in this CharacterList.
        :param add: Add to this CharacterList?
        :return:
        """
        character = Character()
        character.det_dob(self.date.year, self.system)
        for trait in self.demographics_list:
            character.trait_from_demographic(demographic_set=self.demographics_list[trait])
        if add:
            self.add_character(character=character)
        return character

    def random_character(self):
        """
        Return a random Character from the CharacterList.
        :return: Character object selected at random from the CharacterList.
        """
        return r.choice(self.characters)

    def populate(self, num: int):
        """
        Adds num randomly generated Characters (using self.gen_char()) to the CharacterList.
        :param num: Number of Characters to add.
        """
        for i in range(num):
            self.generate_character(add=True)

    def depopulate(self):
        """
        Removes all unused characters (ie with used==False) from the CharacterList
        :return:
        """
        for character in self.characters:
            if not character.used:
                self.characters.remove(character)

    def sort_by_trait(self, trait: str):
        """
        :param trait:
        :return:
        """
        if trait in self.demographics_list:
            self.characters.sort(key=lambda char: char[trait])
        else:
            raise ValueError('Trait not recognised.')

    def sort_name(self):
        """
        Sort the CharacterList by name.
        """
        self.characters.sort(key=lambda char: char.name)

    def sort_dob(self):
        """
        Sort the CharacterList by date-of-birth.
        """
        self.characters.sort(key=lambda char: char.dob.show())

    def out_dobs(self, typ: str = None):
        """
        Return a list of character dates of birth from the CharacterList.
        :param typ: format of date to return; currently only supports entire date or just year.
        :return: List
        """
        lst = list()
        if typ is None:
            for char in self.characters:
                lst.append(char.dob)

        if typ == 'year':
            for char in self.characters:
                lst.append(char.dob.year)

        return lst

    def read_from_file(self, path: str):
        """
        Loads a saved character list from a csv file.
        :param path: Path to csv file.
        """
        chars = np.genfromtxt(path, dtype=None, names=True)
        for i in chars['No']:
            char = Character()
            if chars['DOB'][i] != b'None':
                char.dob.str_to_date(chars['DOB'][i])
            if chars['Ethnicity'][i] != b'None':
                char.ethnicity = str(chars['Ethnicity'][i]).replace("b", "").replace("'", "")
            if chars['Gender'][i] != b'None':
                char.gender = str(chars['Gender'][i]).replace("b", "").replace("'", "")
            if chars['Hand'][i] != b'None':
                char.hand = str(chars['Hand'][i]).replace("b", "").replace("'", "")
            if chars['Name'][i] != b'None':
                char.name = str(chars['Name'][i]).replace("b", "").replace("'", "")
            if chars['Religion'][i] != b'None':
                char.religion = str(chars['Religion'][i]).replace("b", "").replace("'", "")
            if chars['Sex'][i] != b'None':
                char.sex = str(chars['Sex'][i]).replace("b", "").replace("'", "")
            if chars['Sexuality'][i] != b'None':
                char.sexuality = str(chars['Sexuality'][i]).replace("b", "").replace("'", "")
            if chars['Species'][i] != b'None':
                char.species = str(chars['Species'][i]).replace("b", "").replace("'", "")

            if chars['Used'][i] == 1:
                char.used = True
            if chars['Used'][i] == 0:
                char.used = False

            self.characters.append(char)

    def write_to_file(self, path):
        """
        Saves this character list to csv file.
        :param path: Path of csv file to save.
        """
        output_values = np.zeros([len(self.characters), 11], dtype=(str, 24))
        if path[-4:] != '.csv':
            path += '.csv'

        for i, chara in enumerate(self):
            output_values[i, 0] = str(i)
            output_values[i, 1] = str(chara.name)
            output_values[i, 2] = str(chara.dob.show())
            output_values[i, 3] = str(chara.species)
            output_values[i, 4] = str(chara.sex)
            output_values[i, 5] = str(chara.gender)
            output_values[i, 6] = str(chara.ethnicity)
            output_values[i, 7] = str(chara.hand)
            output_values[i, 8] = str(chara.religion)
            output_values[i, 9] = str(chara.sexuality)

            if chara.used is False:
                output_values[i, 10] = '0'
            elif chara.used is True:
                output_values[i, 10] = '1'

        np.savetxt(path + '.csv', output_values,
                   fmt='%-6s,%-11s,%-11s,%-11s,%-8s,%-8s,%-11s,%-11s,%-11s,%-11s,%-1s',
                   header='No.:,Name:,D.O.B.:,Species:,Sex:,Gender:,Ethnicity:,Hand:,Religion:,Sexuality:,Used:'
                   )
