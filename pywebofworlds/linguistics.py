from typing import List, Union
import csv

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import pywebofworlds.utils as utils
from pywebofworlds.tree import draw_tree_line

empty_strings = ['', ' ', None, 'None']
starting_colours = ['red', 'blue', 'green', 'cyan']


# TODO: Writing ancestors to CSV is redundant

def list_colors_by_hue():
    # Remove all colors up to the given
    colors = mcolors.CSS4_COLORS
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                     name)
                    for name, color in colors.items())
    colors = [name for hsv, name in by_hsv]
    return colors


def remove_last_character_if(string: str, char: str = ' '):
    if string[-1] == char:
        string = string[:-1]
    return string


def remove_first_character_if(string: str, char: str = ' '):
    if string[0] == char:
        string = string[1:]
    return string


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

    def reset_plotted(self):
        for language in self.languages:
            self.languages[language].plotted = False

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

    def list_families(self):
        families = []
        for language in self.languages:
            language = self.languages[language]
            family = language.family
            if family not in families:
                families.append(family)
        families.sort()
        return families

    def list_families_from_node(self, language: 'Language', families: list = None, rec=0, max_rec=100):
        rec += 1
        if rec < max_rec:
            if families is None:
                families = []
            if language.family not in families:
                families.append(language.family)
            for descendant in language.descendants:
                descendant = language.descendants[descendant]
                families = list(
                    set(families + self.list_families_from_node(language=descendant, families=families, rec=rec,
                                                                max_rec=max_rec)))
        return families

    def show(self):
        for language in self.languages:
            self.languages[language].show()

    def plot(self, edge_style='square', arrow_size: float = 100.):
        colors = list_colors_by_hue()

        figure = plt.figure()
        ax = figure.add_subplot(111)
        if self.roots is not None:

            for j, root in enumerate(self.roots):
                families = {}
                starting_colour = starting_colours[j]
                colours_family = colors[colors.index(starting_colour):]
                for i, family in enumerate(self.list_families_from_node(root)):
                    families[family] = colours_family[i]
                root.plot(ax=ax, edge_style=edge_style, arrow_size=arrow_size, families=families)
        else:
            print("No root defined for Tree.")
        self.reset_plotted()
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
        rows.sort(key=lambda r: (r[3], r[2], r[1], r[0]))
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
                 parent: str = None,
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

        if type(parent) is str and parent not in empty_strings:
            self.set_parent(name=parent)
        else:
            self.parent = None

    def __str__(self):
        return self.name

    def import_csv_row(self, row):
        if self.year in empty_strings and row['Year'] not in empty_strings:
            self.year = float(row['Year'])
        if self.x in empty_strings and row['x'] not in empty_strings:
            self.x = float(row['x'])
        family = row['Family']
        if self.family in empty_strings and family not in empty_strings:
            family = remove_last_character_if(string=family, char=';')
            self.family = family
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
        self.parent.add_descendant(name=self.name)
        self.add_ancestor(name=name)

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

    def plot(self, ax, edge_style='square', arrow_size: float = 100., families=None):
        if families is not None:
            color = families[self.family]
        else:
            color = 'red'
        if not self.plotted and self.x is not None and self.year is not None:
            props = dict(boxstyle='round', alpha=0.5, facecolor=color)
            ax.text(self.x, self.year, str(self.name), fontsize=14,
                    verticalalignment='top', bbox=props)

            for descendant in self.descendants:
                descendant = self.descendants[descendant]
                if descendant is not self and descendant.x is not None and descendant.year is not None:

                    if descendant.parent is self:
                        line_style = '-'
                    else:
                        line_style = ':'
                    draw_tree_line(ax=ax, origin_x=self.x, origin_y=self.year, destination_x=descendant.x,
                                   destination_y=descendant.year, colour=color, edge_style=edge_style,
                                   line_style=line_style, arrow_size=arrow_size)

                    descendant.plot(ax=ax, edge_style=edge_style, arrow_size=arrow_size, families=families)

            ax.scatter(self.x, self.year, c=color)

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
