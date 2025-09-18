from typing import Union

import pywebofworlds.utils as u


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
        string = 'Trait: ' + str(self.trait) + '\n'
        for name in self.demographics:
            string += name + ': ' + str(self.demographics[name]) + '\n'
        return string

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

    def write_to_file(self, path: str):
        """
        Writes the DemographicList to a .csv file.
        :param path: Path of file, including name.
        :return:
        """
        rows = []
        for group in self.demographics:
            rows.append(group + ',' + str(self.demographics[group]))
        u.write_wow_csv(path=path,
                        header='DemographicSet,Trait:,' + self.trait,
                        names=['Group:', 'Percentage:'],
                        rows=rows)

    def read_from_file(self, path: str):
        """
        Reads the DemographicList from a .csv file.
        :param path: Path of file, including name.
        :return:
        """
        header, names, rows = u.read_wow_csv(path=path, dtype=[str, float])
        self.trait = header[2]
        demographics = {}
        for row in rows:
            demographics[row[0]] = row[1]
        self.add_demographics(demographics=demographics)


# Default DemographicSets based on Earth, 2016
sexes2016 = DemographicSet(
    trait='Sex',
    demographics={
        'Female': 49.15,
        'Male': 49.15,
        'Intersex': 1.7
    }
)
species2016 = DemographicSet(
    trait='Species',
    demographics={
        'Human': 100
    }
)
hands2016 = DemographicSet(
    trait='Hand',
    demographics={
        'Right': 88,
        'Left': 10,
        'Cross': 1,
        'Ambidextrous': 1
    }
)

demographics2016 = (sexes2016, hands2016, species2016)
