from typing import List, Union
import csv
import utils
from matplotlib import pyplot as plt
from tree import draw_tree_line
from matplotlib.patches import Rectangle

empty_strings = ['', ' ', None, 'None']

class LanguageList:
    def __init__(self, path: str = None, name: str = None, roots: Union[str, List[str]] = 'Classical Latin'):
        self.name = name
        self.languages = {}
        self.roots = []
        if type(roots) is str:
            roots = [roots]
        for root in roots:
            self.roots.append(self.add_empty_language(root))
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

    def show(self):
        for language in self.languages:
            self.languages[language].show()

    def plot(self, edge_style='square'):
        figure = plt.figure()
        ax = figure.add_subplot(111)
        if self.roots is not None:
            for root in self.roots:
                root.plot(ax=ax, edge_style=edge_style)
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

        if ancestors not in [None, ' ', '']:
            self.ancestors = list_to_dict(ancestors)
        else:
            self.ancestors = {}

        if descendants not in [None, ' ', '']:
            self.descendants = list_to_dict(ancestors)
        else:
            self.descendants = {}

        if parent not in [None, ' ', '']:
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

        ancestor_strings = utils.split_string(row['Ancestors'])
        for ancestor in ancestor_strings:
            if ancestor not in empty_strings:
                self.add_ancestor(ancestor)

        descendant_strings = utils.split_string(row['Descendants'])
        for descendant in descendant_strings:
            if descendant not in empty_strings:
                self.add_descendant(descendant)

    def add_ancestor(self, name: str):
        if name not in self.ancestors:
            self.ancestors[name] = self.language_list.add_empty_language(name)
            self.ancestors[name].add_descendant(self.name)

    def add_descendant(self, name: str):
        if name not in self.descendants:
            self.descendants[name] = self.language_list.add_empty_language(name)
            self.descendants[name].add_ancestor(self.name)

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

    def plot(self, ax, edge_style='square'):
        if not self.plotted:
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(self.x, self.year, str(self.name), fontsize=14,
                    verticalalignment='top', bbox=props)

            for descendant in self.descendants:
                descendant = self.descendants[descendant]

                if descendant.parent is self:
                    line_style = '-'
                else:
                    line_style = ':'
                draw_tree_line(ax=ax, origin_x=self.x, origin_y=self.year, destination_x=descendant.x,
                               destination_y=descendant.year, colour='black', edge_style=edge_style,
                               line_style=line_style)
                descendant.plot(ax=ax, edge_style=edge_style)

            ax.scatter(self.x, self.year, c='red')

        self.plotted = True

    def csv(self):
        descendants_string = ""
        for descendant in self.descendants:
            descendants_string += descendant + ";"
        ancestors_string = ""
        for ancestor in self.ancestors:
            ancestors_string += ancestor + ";"
        if self.parent is not None:
            parent = str(self.parent)
        else:
            parent = None
        return [self.name, str(self.year), self.x, self.family, parent, ancestors_string, descendants_string]
