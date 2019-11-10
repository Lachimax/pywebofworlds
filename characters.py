import random as r
import timelines as t
import numpy as np


# TODO: Account for mixed ethnicities
# TODO: Choose and implement sexuality model
# TODO: gender model
# TODO: Automatic rebalance of random generation depending on in-use characters.

# TODO: Maybe implement a class for location, incorporating date systems, demographics etc.


class Demographic:
    """An object containing information about a demographic of a population, including the type (gender,
    ethnicity, etc.), name of the demographic, and percentage of the population it takes up.
    """

    def __init__(self, typ=None, name=None, percent=None):
        self.accepted_types = ['Ethnicity', 'Gender', 'Hand', 'Religion', 'Sex', 'Sexuality', 'Species']

        if typ is not None:
            if typ not in self.accepted_types:
                raise TypeError('Unaccepted demographic type')

            if not isinstance(typ, str):
                raise TypeError('type must be a string')
            else:
                self.type = typ

        else:
            self.type = None

        if name is not None:
            if not isinstance(name, str):
                raise TypeError('name must be a string')
            else:
                self.name = name

        else:
            self.name = None

        self.percent = percent

    def show(self):
        print(self.name + ', ' + str(self.percent) + '%')


class DemographicSet:
    """An object containing a set of demographics, ideally adding to 100%. Each set contains one type of demographic,
    ie one set for ethnicity, one for sex, etc.
    """

    def __init__(self, demos=None, typ=None):
        self.d_list = list()
        self.type = typ

        if demos is not None:
            self.type = demos[0].type
            self.add_demos(demos=demos)

    def __getitem__(self, key):
        return self.d_list[key]

    def __setitem__(self, key, value):
        self.d_list[key] = value

    def add_demos(self, demos):
        """Adds demographic objects to d_list

        :param demos: a list of demographic objects to be added.
        """

        if (not isinstance(demos, list)) | (not isinstance(demos[0], Demographic)):
            raise TypeError('demos must be a list of demographics')

        else:

            # Use the list to set the type, if the type is not already set.
            if self.type is None:
                self.type = demos[0].type

            for i in range(len(demos)):
                if demos[i].type != self.type:
                    raise ValueError('Demographics in a demographicSet object must be the same type')
                else:
                    self.d_list.append(demos[i])

            total = self.check_percentage()[1]
            check = self.check_percentage()[0]

            if not check:
                print("These demographics add to " + str(total) + "%")

    def show(self):
        print(str(self.type))
        for i in range(len(self.d_list)):
            self.d_list[i].show()

    def length(self):
        return len(self.d_list)

    def check_percentage(self):
        """
        Checks that the percentages in a list add up to 100 (or close enough)
        :return: True if sum is within 0.1 of 100; otherwise False;
        """

        total = 0

        for i in range(len(self.d_list)):
            total += self.d_list[i].percent

        delta = 100 - total

        if abs(delta) > 0.1:
            return False, total
        else:
            return True, total

    def sort_name(self):
        self.d_list.sort(key=lambda dem: dem.name)

    def sort_percent(self):
        self.d_list.sort(key=lambda dem: dem.percent)

    def write_to_file(self, title):

        outputvalues = np.zeros([len(self.d_list), 3], dtype=(str, 24))

        for i, dem in enumerate(self):
            outputvalues[i, 0] = str(i)
            outputvalues[i, 1] = str(dem.name)
            outputvalues[i, 2] = str(dem.percent) + '%'

        np.savetxt(title + '.txt', outputvalues,
                   fmt='%-6s %-11s %-11s ',
                   header='Type: ' + self.type + '\n' + 'No.: Group:      Percentage:'
                   )

    def read_from_file(self, path):
        with open(path, 'r') as f:
            first_line = f.readline()
            typ = first_line[8:]
            self.type = typ.replace('\n', '')

        dems = np.genfromtxt(path, dtype=None, names=True, skip_header=1)
        for i in dems['No']:
            dem = Demographic()
            if dems['Group'][i] != b'None':
                dem.name = str(dems['Group'][i]).replace("b", "").replace("'", "")
            if dems['Percentage'][i] != b'None':
                dem.percent = str(dems['Percentage'][i]).replace("b", "").replace("'", "").replace("%", "")

            self.d_list.append(dem)


class Character:
    def __init__(self):

        self.dob = t.Date()
        self.ethnicity = None
        self.gender = None
        self.hand = None
        self.name = None
        self.religion = None
        self.sex = None
        self.sexuality = None
        self.species = None

        #TODO: Account for non-biological parents, eg adoption

        self.mother = None
        self.father = None
        self.children = list()

        self.used = False

    def set_dob(self):
        x=5

    def det_dob(self, year, system='Julian'):
        # Here I assume the distribution of age is a Gaussian, with a standard deviation of 34. This should vary for different species.
        dob = t.Date(system=system)
        # TODO Implement different std dev for different species' lifespans.
        # TODO: Improve model of population age distribution. Probably has a flatter distribution that becomes a Gaussian for higher ages
        age = abs(np.random.normal(scale=34))

        yob = year - age

        dob.rand_date()
        dob.set_year(yob)

        self.dob = dob

    def det_ethnic(self, demos):

        if demos.type != 'Ethnicity':
            raise ValueError('Demographic type must be Ethnicity')

        if not demos.check_percentage()[0]:
            raise NameError('demographic list does not add to 100')

        ethnicities = list()
        for i in range(demos.length()):
            for j in range(int(100 * demos[i].percent)):
                ethnicities.extend([demos[i].name])

        eth = r.choice(ethnicities)
        self.ethnicity = eth

    def det_hand(self, demos=DemographicSet(
        [Demographic('Hand', 'Right', 88), Demographic('Hand', 'Left', 10), Demographic('Hand', 'Cross-dominant', 1),
         Demographic('Hand', 'Ambidextrous', 1)])):

        if demos.type != 'Hand':
            raise ValueError('Demographic type must be Hand')

        if not demos.check_percentage()[0]:
            raise ValueError('demographic list does not add to 100')

        hands = list()
        for i in range(demos.length()):
            for j in range(int(100 * demos[i].percent)):
                hands.extend([demos[i].name])

        hand = r.choice(hands)
        self.hand = hand

    def det_religion(self, demos):

        if demos.type != 'Religion':
            raise ValueError('Demographic type must be Religion')

        if not demos.check_percentage()[0]:
            raise NameError('demographic list does not add to 100')

        religions = list()
        for i in range(demos.length()):
            for j in range(int(100 * demos[i].percent)):
                religions.extend([demos[i].name])

        rel = r.choice(religions)
        self.religion = rel

    def det_sex(self, demos=DemographicSet(
        [Demographic('Sex', 'Female', 49.15), Demographic('Sex', 'Male', 49.15), Demographic('Sex', 'Intersex', 1.7)])):

        if demos.type != 'Sex':
            raise ValueError('Demographic type must be Sex')

        if not demos.check_percentage()[0]:
            raise NameError('demographic list does not add to 100')

        sexes = list()
        for i in range(demos.length()):
            for j in range(int(100 * demos[i].percent)):
                sexes.extend([demos[i].name])

        sex = r.choice(sexes)
        self.sex = sex

    def det_species(self, demos=DemographicSet([Demographic('Species', 'Human', 100)])):

        if demos.type != 'Species':
            raise ValueError('Demographic type must be Species')

        if not demos.check_percentage()[0]:
            raise ValueError('demographic list does not add to 100')

        species = list()
        for i in range(demos.length()):
            for j in range(int(100 * demos[i].percent)):
                species.extend([demos[i].name])

        sp = r.choice(species)
        self.species = sp

    def show(self):
        string = ''
        if self.name is not None:
            string = string + 'Name: ' + str(self.name) + ', '
        if self.dob is not None:
            string = string + 'D.O.B.: ' + self.dob.show() + ', '
        if self.species is not None:
            string = string + 'Species: ' + str(self.species) + ', '
        if self.sex is not None:
            string = string + 'Sex: ' + str(self.sex) + ', '
        if self.gender is not None:
            string = string + 'Gender: ' + str(self.gender) + ', '
        if self.ethnicity is not None:
            string = string + 'Ethnicity: ' + str(self.ethnicity) + ', '
        if self.hand is not None:
            string = string + 'Hand: ' + str(self.hand) + ', '
        if self.religion is not None:
            string = string + 'Religion: ' + str(self.religion) + ', '
        if self.sexuality is not None:
            string = string + 'Sexuality: ' + str(self.sexuality) + ', '

        return string


class CharacterList:
    def __init__(self, year=2016, location='Earth',
                 sexes=DemographicSet(
                     [Demographic('Sex', 'Female', 49.15), Demographic('Sex', 'Male', 49.15),
                      Demographic('Sex', 'Inter', 1.7)]),
                 ethnicities=None,
                 species=DemographicSet([Demographic('Species', 'Human', 100)]),
                 hands=DemographicSet([Demographic('Hand', 'Right', 88), Demographic('Hand', 'Left', 10),
                                       Demographic('Hand', 'Cross', 1),
                                       Demographic('Hand', 'Ambi', 1)])):

        self.chars = list()

        self.date = t.Date(year=year)
        self.location = location
        if self.location == 'Earth':
            self.system = 'Julian'

        if ethnicities is not None:
            self.eth_demo = ethnicities
        self.sex_demo = sexes
        self.hand_demo = hands
        self.spec_demo = species

    def __getitem__(self, item):
        return self.chars[item]

    def add_char(self, char):
        self.chars.append(char)

    def gen_char(self):
        char = Character()
        if self.eth_demo is not None:
            char.det_ethnic(self.eth_demo)
        char.det_hand(self.hand_demo)
        char.det_sex(self.sex_demo)
        char.det_species(self.spec_demo)
        char.det_dob(self.date.year, self.system)

        return char

    def rand_char(self):
        return r.choice(self.chars)

    def populate(self, num):
        for i in range(num):
            self.add_char(self.gen_char())

    def length(self):
        return len(self.chars)

    def show(self):
        for i in range(self.length()):
            print(str(i) + ' ' + self.chars[i].show())

    def sort_dob(self):
        self.chars.sort(key=lambda char: char.dob.show())

    def sort_ethnic(self):
        self.chars.sort(key=lambda char: char.ethnicity)

    def sort_hand(self):
        self.chars.sort(key=lambda char: char.hand)

    def sort_name(self):
        self.chars.sort(key=lambda char: char.name)

    def sort_religion(self):
        self.chars.sort(key=lambda char: char.religion)

    def sort_sex(self):
        self.chars.sort(key=lambda char: char.sex)

    def sort_species(self):
        self.chars.sort(key=lambda char: char.species)

    def out_dobs(self, type=None):
        lst = list()
        if type is None:
            for char in self.chars:
                lst.append(char.dob)

        if type == 'year':
            for char in self.chars:
                lst.append(char.dob.year)

        return lst

    def read_from_file(self, path):
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

            self.chars.append(char)

    def write_to_file(self, title):

        outputvalues = np.zeros([len(self.chars), 11], dtype=(str, 24))

        for i, chara in enumerate(self):
            outputvalues[i, 0] = str(i)
            outputvalues[i, 1] = str(chara.name)
            outputvalues[i, 2] = str(chara.dob.show())
            outputvalues[i, 3] = str(chara.species)
            outputvalues[i, 4] = str(chara.sex)
            outputvalues[i, 5] = str(chara.gender)
            outputvalues[i, 6] = str(chara.ethnicity)
            outputvalues[i, 7] = str(chara.hand)
            outputvalues[i, 8] = str(chara.religion)
            outputvalues[i, 9] = str(chara.sexuality)

            if chara.used is False:
                outputvalues[i, 10] = '0'
            elif chara.used is True:
                outputvalues[i, 10] = '1'

        np.savetxt(title + '.txt', outputvalues,
                   fmt='%-6s %-11s %-11s %-11s %-8s %-8s %-11s %-11s %-11s %-11s %-1s',
                   header='No.: Name:       D.O.B.:     Species:    Sex:     Gender:  Ethnicity:  Hand:       Religion:   Sexuality:  Used:'
                   )
        #
        # print(outputvalues)



class FamilyTree:
    def __init__(self, root=None):
        if type(root) is FamilyTreeNode:
            self.root = root

        else:
            self.root = None


class FamilyTreeNode:

    def __init__(self, parent=None, children=None):

        if type(parent) is FamilyTreeNode:
            self.parent = parent
        else:
            self.parent = None

        for child in children:
            if type(child) is FamilyTreeNode:
                self.children.append(child)

        else:
            self.children = list()


