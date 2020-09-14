from typing import List, Union
import csv
import utils
from matplotlib import pyplot as plt
from tree import draw_tree_line
from matplotlib.patches import Rectangle

empty_strings = ['', ' ', None, 'None']


# TODO: Writing ancestors to CSV is redundant

class LanguageList:
    def __init__(self, path: str = None, name: str = None, roots: Union[str, List[str]] = None):
        self.name = name
        self.languages = {}
        self.roots = []
        if roots is not None:
            if type(roots) is str:
                roots = [roots]
            for root in roots:
                self.roots.append(self.add_empty_language(root))
        else:
            self.roots = None

        if path is not None:
            self.load_csv(path)

    def __getitem__(self, item):
        return self.languages[item]

    def __setitem__(self, key, value):
        self.languages[key] = value

    def add_empty_language(self, name: str):
        if name not in self.languages:
            Language(name=name, language_list=self)
        return self.languages[name]

    def add_language(self, name: str, year: Union[float, str], x: Union[float, str], family: str, parent: str,
                     ancestors: Union[str, List[str]], descendants: Union[str, List[str]]):
        language = self.add_empty_language(name=name)
        if type(descendants) is list:
            descendants = semicolon_list(descendants)
        if type(ancestors) is list:
            ancestors = semicolon_list(ancestors)
        else:
            raise TypeError('Only list or string accepted.')
        row = {'Name': name, 'Year': str(year), 'x': str(x), 'Family': family, 'Parent': parent, 'Ancestors': ancestors,
               'Descendants': descendants}
        language.import_csv_row(row)
        return language

    def show(self):
        for language in self.languages:
            self.languages[language].show()

    def plot(self, edge_style='square', arrow_size: float = 100.):
        figure = plt.figure()
        ax = figure.add_subplot(111)
        if self.roots is not None:
            for root in self.roots:
                root.plot(ax=ax, edge_style=edge_style, arrow_size=arrow_size)
        else:
            print("No root defined for Tree.")
        ax.invert_yaxis()
        plt.show()

    def load_csv(self, path: str = None):
        with open(path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                language = self.add_empty_language(name=row['Name'])
                language.import_csv_row(row)

    def write_csv(self, path):
        path = utils.sanitise_file_ext(path=path, ext='.csv')
        rows = self.csv()
        rows.sort(key=lambda r: (r[3], r[1], r[0]))
        header = ['Name', 'Year', 'x', 'Family', 'Parent', 'Ancestors', 'Descendants']
        # writing to csv file
        with open(path, 'w', newline='', encoding="utf-8") as csv_file:
            # creating a csv writer object
            csv_writer = csv.writer(csv_file)
            # writing the fields
            csv_writer.writerow(header)
            # writing the data rows
            csv_writer.writerows(rows)

    def csv(self):
        rows = []
        for language in self.languages:
            rows.append(self.languages[language].csv())
        return rows


def list_to_dict(languages: List['Language']):
    dicti = {}
    for language in languages:
        dicti[language.name] = language
    return dicti


class Language:
    def __init__(self, name: str, language_list: LanguageList, year: float = None, x: float = None, family: str = None,
                 parent: 'Language' = None,
                 ancestors: List['Language'] = None,
                 descendants: List['Language'] = None):

        self.name = str(name)
        self.language_list = language_list
        language_list[self.name] = self
        self.year = year
        self.x = x
        self.family = family
        self.plotted = False

        if ancestors not in empty_strings:
            self.ancestors = list_to_dict(ancestors)
        else:
            self.ancestors = {}

        if descendants not in empty_strings:
            self.descendants = list_to_dict(ancestors)
        else:
            self.descendants = {}

        if parent not in empty_strings:
            self.parent = parent
        else:
            self.parent = None

    def __str__(self):
        return self.name

    def import_csv_row(self, row):
        if self.year in empty_strings and row['Year'] not in empty_strings:
            self.year = float(row['Year'])
        if self.x in empty_strings and row['x'] not in empty_strings:
            self.x = float(row['x'])
        if self.family in empty_strings and row['Family'] not in empty_strings:
            self.family = str(row['Family'])
        if self.parent in empty_strings and row['Parent'] not in empty_strings:
            self.set_parent(name=row['Parent'])

        if row['Ancestors'] not in empty_strings:
            if row['Ancestors'][-1] != ';':
                row['Ancestors'] += ';'
            ancestor_strings = utils.split_string(row['Ancestors'])
            for ancestor in ancestor_strings:
                if ancestor[-1] == ' ':
                    ancestor = ancestor[:-1]
                if ancestor not in empty_strings:
                    self.add_ancestor(ancestor)

        if row['Descendants'] not in empty_strings:
            if row['Descendants'][-1] != ';':
                row['Descendants'] += ';'
            descendant_strings = utils.split_string(row['Descendants'])
            for descendant in descendant_strings:
                if descendant[-1] == ' ':
                    descendant = descendant[:-1]
                if descendant not in empty_strings:
                    self.add_descendant(descendant)

    def add_ancestor(self, name: str):
        if name not in self.ancestors:
            self.ancestors[name] = self.language_list.add_empty_language(name)
            self.ancestors[name].add_descendant(self.name)
        return self.ancestors[name]

    def add_descendant(self, name: str):
        if name not in self.descendants:
            self.descendants[name] = self.language_list.add_empty_language(name)
            self.descendants[name].add_ancestor(self.name)
        return self.descendants[name]

    def set_parent(self, name: str):
        self.parent = self.language_list.add_empty_language(name)

    def show(self):
        print(self.name, self.year, self.family, str(self.parent), self.show_ancestors(), self.show_descendants())

    def show_ancestors(self):
        ancestors = []
        for ancestor in self.ancestors:
            ancestors.append(str(self.ancestors[ancestor]))
        return ancestors

    def show_descendants(self):
        descendants = []
        for descendant in self.descendants:
            descendants.append(str(descendant))
        return descendants

    def plot(self, ax, edge_style='square', arrow_size: float = 100.):
        if not self.plotted and self.x is not None and self.year is not None:
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(self.x, self.year, str(self.name), fontsize=14,
                    verticalalignment='top', bbox=props)

            for descendant in self.descendants:
                descendant = self.descendants[descendant]
                if descendant.x is not None and descendant.year is not None:

                    if descendant.parent is self:
                        line_style = '-'
                    else:
                        line_style = ':'

                    draw_tree_line(ax=ax, origin_x=self.x, origin_y=self.year, destination_x=descendant.x,
                                   destination_y=descendant.year, colour='black', edge_style=edge_style,
                                   line_style=line_style, arrow_size=arrow_size)

                    descendant.plot(ax=ax, edge_style=edge_style, arrow_size=arrow_size)

            ax.scatter(self.x, self.year, c='red')

        self.plotted = True

    def csv(self):
        descendants_string = semicolon_list(self.descendants)
        ancestors_string = semicolon_list(self.ancestors)
        if self.parent is not None:
            parent = str(self.parent)
        else:
            parent = None
        return [self.name, str(self.year), self.x, str(self.family), parent, ancestors_string, descendants_string]


def semicolon_list(lst=List[str]):
    string_list = ""
    for string in lst:
        string_list += string + ";"
    return string_list
