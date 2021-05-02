import os
from typing import List

from astropy import table
from numpy.ma import masked

from pywebofworlds import utils as u

na_vals = ["", None, masked]


def replace_all(string: str, replace: str, replace_with: str = ""):
    while replace in string:
        string = string.replace(replace, replace_with)
    return string


def generate_glossary_html(path_glossary: str,
                           path_output: str = None,
                           path_stories: str = None):
    """
    Wrapper function to convert glossary .csv to HTML, using a Glossary object.
    @param path_glossary:
    @param path_output:
    @param path_stories:
    @return:
    """
    glossary = Glossary(path=path_glossary, path_stories=path_stories)
    glossary.write_html(path_output)
    return glossary


# TODO: Comment!!!
# TODO: Catch bad story list entries.

class GlossaryEntry:
    def __init__(self, name: str, text: str, formatted_name: str = None, plural: str = None, alternate_name: str = None,
                 binomial: str = None,
                 word_type: str = "",
                 see: List[str] = None, stories: dict = None, mask: bool = False):
        self.name = name.lower()
        self.id = replace_all(self.name, " ", "-")
        while text.endswith(" "):
            text = text[:-1]
        if not text.endswith("."):
            text += "."
        if text.startswith("definitions"):
            text = text.split("@")
            text.pop(0)
        self.text = text
        self.formatted_name = formatted_name
        self.plural = plural
        self.alternate_name = alternate_name
        self.word_type = word_type
        if self.word_type is not None and ":" in self.word_type:
            self.word_type = self.word_type.split(":")
        self.binomial = binomial
        self.stories = stories
        if type(see) is list:
            self.see = self.see_to_dict(see)
        else:
            self.see = {}
        self.mask = mask

    @classmethod
    def from_row(cls, row: table.Row, stories: dict = None):

        formatted_name = None
        if row["formatted_name"] not in na_vals:
            formatted_name = row["formatted_name"]
        alternate_name = None
        if row["alternate_name"] not in na_vals:
            formatted_name = row["alternate_name"]
        plural = None
        if row["plural"] not in na_vals:
            plural = row["plural"]
        word_type = None
        if row["type"] not in na_vals:
            word_type = row["type"]
        binomial = None
        if row["binomial"] not in na_vals:
            binomial = row["binomial"]
            binomial = binomial.replace(binomial[0], binomial[0].upper(), 1)
        if row["mask"] in na_vals or row["mask"] == "FALSE":
            mask = False
        else:
            mask = True

        see = None
        if row["see"] not in na_vals:
            see_str = row["see"]
            see = []
            for string in see_str.split():
                if string[-1] != ";":
                    string += ";"
                string = string[:string.find(";")]
                see.append(string)

        return cls(name=row["name"],
                   formatted_name=formatted_name,
                   alternate_name=alternate_name,
                   text=row["text"],
                   plural=plural,
                   word_type=word_type,
                   binomial=binomial,
                   see=see,
                   stories=stories,
                   mask=mask
                   )

    def to_dict(self):
        dictionary = {"name": self.name,
                      "text": self.text}
        if self.plural is not None:
            dictionary["plural"] = self.plural
        if self.word_type is not None:
            type_str = ""
            if type(self.word_type) is list:
                for word in self.word_type:
                    type_str += f"{word}:"
                type_str = type_str[:-1]
            else:
                type_str = self.word_type
            dictionary["type"] = type_str
        if self.binomial is not None:
            dictionary["binomial"] = self.binomial

        return dictionary

    def see_to_dict(self, see):
        stories_dict = {}
        for name in see:
            if name in self.stories:
                story = self.stories[name]
                if ":" in name:
                    series = name[:name.find(":")]
                    if series not in stories_dict:
                        stories_dict[series] = [story]
                    else:
                        stories_dict[series].append(story)
                else:
                    stories_dict[name] = story
            else:
                raise ValueError(f"{name} missing from story list.")
        return stories_dict

    # TODO: Sort see by order in "stories (unless there is a primary source?)"
    def see_to_html(self):
        """
        Generate html code to represent the See list.
        """
        # If
        if not self.see:
            html_str = ""
        else:
            html_str = "See:\n" \
                       "\t\t<ul>\n"
            for short_title in self.see:
                story_html = f"\t\t\t<li>\n"
                story_entry = self.see[short_title]
                if type(story_entry) is list:
                    series_entry = self.stories[short_title]
                    series_title = series_entry['title']
                    url = series_entry['url']
                    if len(story_entry) == 0:
                        story_html += f'\t\t\t\t<a href="{url}" target="_blank"><i>{series_title}</i></a>\n'
                    if len(story_entry) == 1 and not story_entry[0]["mask"]:
                        story_html += f'\t\t\t\t<a href="{story_entry[0]["url"]}" target="_blank"><i>{series_title}</i> - {story_entry[0]["title"]}</a>\n'
                    else:
                        story_html += \
                            f"\t\t\t\t<i><a href='{url}' target='_blank'>{series_title}</a></i>\n" \
                            f"\t\t\t\t<ul>\n"
                        for sub_story_entry in story_entry:
                            story_html += f'\t\t\t\t\t<li><a href="{sub_story_entry["url"]}" target="_blank">{sub_story_entry["title"]}</a></li>\n'
                        story_html += "\t\t\t\t</ul>\n"
                else:
                    story_html += f'\t\t<i><a href="{story_entry["url"]}" target="_blank">{story_entry["title"]}</a></i>\n'

                story_html += "\t\t\t</li>\n"
                html_str += story_html

            html_str += "\t\t</ul>\n"

        return html_str

    def to_html(self):
        if self.mask:
            html_str = ""
        else:

            if self.formatted_name is not None:
                name = self.formatted_name
            else:
                name = self.name

            if self.alternate_name is not None:
                name = f"{name}</b> or <b>{self.alternate_name}"

            html_str = \
                f'\t<li id="{self.id}"><b>{name}'

            if self.plural is not None or self.binomial is not None:
                html_str += " ("

                if self.plural is not None:
                    html_str += f"pl. {self.plural}"
                    if self.binomial is not None:
                        html_str += "; "
                if self.binomial is not None:
                    if type(self.word_type) is list:
                        if self.word_type[0] == "taxon":
                            if self.word_type[1] in ["species", "subspecies"]:
                                html_str += f"<i>{self.binomial}</i>"
                            elif self.word_type[1] == "genus":
                                html_str += f"genus <i>{self.binomial}</i>"
                            else:
                                html_str += f"{self.word_type[0]} {self.binomial}"
                html_str += ")"

            text = ""
            if type(self.text) is list:
                text += self.text[0]
                text += "<ul>"
                for t in self.text[1:]:
                    text += f"<li>{t}</li>"
                text += "</ul>"
            else:
                text = self.text
            html_str += f":</b> {text} {self.see_to_html()}\n" \
                        f"\t</li>\n\n"
        return html_str


# TODO: Check if the files are correctly formatted
# TODO: Write to file; and
# TODO: write empty template file (as classmethod using dummy instance)
# TODO: auto-hyperlinking within file;

class Glossary:
    def __init__(self, path: str, path_stories: str = None):

        if os.path.isdir(path):
            self.filename_csv = "glossary.csv"
            path_glossary = path
        else:
            path_glossary, self.filename_csv = os.path.split(path)

        if path_stories is None:
            path_stories = os.path.join(path_glossary, "stories.csv")
        elif os.path.isdir(path_stories):
            path_stories = os.path.join(path_stories, "stories.csv")

        self.glossary_table = table.Table.read(os.path.join(path_glossary, self.filename_csv), format="ascii.csv",
                                               encoding="utf-8")
        self.glossary_table.sort('name')
        self.story_table = table.Table.read(path_stories, format="ascii.csv", encoding="utf-16")

        self.stories = {}
        self.parse_story_table()

        self.glossary = {}
        self.parse_glossary()

        self.types = {}
        # self.count_types()

    def parse_story_table(self):
        self.stories = {}

        for row in self.story_table:
            title = row["short_title"]
            if row["mask"] in na_vals or row["mask"] == "FALSE":
                mask = False
            else:
                mask = True
            story_dict = {"short_title": row["short_title"],
                          "title": row["title"],
                          "url": row["url"],
                          "mask": mask}
            self.stories[title] = story_dict
        return self.stories

    def parse_glossary(self):
        for row in self.glossary_table:
            entry = GlossaryEntry.from_row(row=row, stories=self.stories)
            self.glossary[entry.name] = entry
        return self.glossary

    def to_html(self):
        html_str = "<ul>\n"
        for entry in self.glossary:
            html_str += self[entry].to_html()
        html_str += "</ul>"
        return html_str

    def write_html(self, path):
        path = u.sanitise_file_ext(path=path, ext=".html")
        html_str = self.to_html()
        with open(path, "w") as file:
            file.write(html_str)
        return html_str

    def count_types(self):
        types = {}
        sums = {}
        for item in self:
            word_type = item.word_type
            if word_type is not None:
                if type(word_type) is list:
                    this_dict = {}
                    # for i, word in enumerate(word_type):
                    #     if word in types:
                    #         if types[word] is dict:
                else:
                    types = increment_dict(types, word_type)

        self.types = types

    def __getitem__(self, key):
        return self.glossary[key]

    def __setitem__(self, key: str, value: GlossaryEntry):
        if value is not GlossaryEntry:
            raise TypeError("Can only directly set values of type GlossaryEntry")
        self.glossary[key] = value


def increment_dict(dictionary: dict, key: str, add: int = 1):
    if key in dictionary:
        if type(dictionary[key]) is int:
            dictionary[key] += add
        else:
            raise ValueError(f"Dictionary value at '{key}' is not int.")
    else:
        dictionary[key] = add
    return dictionary
