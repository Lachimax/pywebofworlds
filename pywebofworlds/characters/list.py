import random as r
from typing import Union, Iterable, List

import pywebofworlds.history as t
import pywebofworlds.utils as u

from .character import Character
from .demographic import DemographicSet, demographics2016

class CharacterList:
    # TODO: Implement multiple names
    def __init__(self, characters: Union[List[Character], str] = None, year: int = 2016, location: str = 'Earth',
                 demographics_list: Iterable = demographics2016):

        if characters is None:
            characters = []

        if type(characters) is str:
            self.characters = []
            self.read_from_file(path=characters)
        elif type(characters) is list:
            # TODO: Sanitise types in list
            self.characters = characters
        else:
            raise TypeError('characters must be list or str.')

        self.demographics_list = {}
        if demographics_list is not None:
            for demographic_set in demographics_list:
                self.add_demographic_set(demographic_set)

        self.date = t.Date(year=year)
        self.location = location
        if self.location == 'Earth':
            self.system = 'Gregorian'
        else:
            self.system = None

    def __getitem__(self, item):
        return self.characters[item]

    def __setitem__(self, key, value):
        self.characters[key] = value

    def __len__(self):
        return len(self.characters)

    def __str__(self):
        string = f"Date: {self.date}\n"
        string += f"Date System: {self.system}\n"
        string += f"Location: {self.location}\n"
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
        character.gen_dob(self.date.year, self.system)
        for trait in self.demographics_list:
            character.trait_from_demographic(demographic_set=self.demographics_list[trait])
        if add:
            self.add_character(character=character)
        return character

    # TODO: Method for propagating and assigning a new trait, from demographic, to existing characters.

    def random_character(self):
        """
        Return a random Character from the CharacterList.
        :return: Character object selected at random from the CharacterList.
        """
        return r.choice(self.characters)

    def add_characters(self, num: int):
        """
        Adds num randomly generated Characters (using self.gen_char()) to the CharacterList.
        :param population: Number of Characters to add.
        """
        for i in range(num):
            self.generate_character(add=True)

    def populate(self, population: int):
        """
        Adds or removes characters to match population.
        Characters with used==True are immune to removal.
        :param population:
        :return:
        """

    def depopulate(self):
        """
        Removes all unused characters (ie with used==False) from the CharacterList
        :return:
        """
        for character in self.characters:
            if not character.used:
                self.characters.remove(character)

    def repopulate(self, num: int):
        """
        Adds num randomly generated Characters to the CharacterList, taking the existing
        characters into account.
        :return:
        """
        # Create an AccountedFor placeholder Demographic that is the fraction occupied by the existing characters?

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

    # TODO: Read/write associated demographic sets along with the character list

    def write_to_file(self, path: str):
        """
        Writes the CharacterList to a .csv file.
        :param path: Path of file, including name.
        :return:
        """
        rows = []
        names = ['No.:', 'Name:', 'Used:', 'D.O.B.:']
        for trait in self.demographics_list:
            names.append(trait + ':')
        for i, char in enumerate(self.characters):
            row = f'{i},{char.name},{char.used},{char.dob}'
            for trait in char.traits:
                row += ',' + char[trait]
            rows.append(row)

        header = 'CharacterList,'
        header += f"Date:,{self.date},"
        header += f"Date System:,{self.system},"
        header += f"Location:,{self.location},"

        u.write_wow_csv(
            path=path,
            header=header,
            names=names,
            rows=rows
        )

    def read_from_file(self, path: str):
        """
        Reads the CharacterList from a .csv file.
        :param path: Path of file, including name.
        :return:
        """
        header, names, rows = u.read_wow_csv(path=path, dtype=[int, str, bool, str])
        self.date = header[2]
        self.system = header[4]
        self.location = header[6]
        for row in rows:
            char = Character()
            char.used = row[2]
            char.dob = t.Date(string=row[3])
            for i in range(4, len(row)):
                char[names[i]] = row[i]
            self.add_character(character=char)
