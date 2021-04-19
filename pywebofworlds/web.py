import os
from typing import List

from astropy import table
from numpy.ma import masked

from pywebofworlds import utils as u

na_vals = ["", None, masked]


class GlossaryEntry:
    def __init__(self, name: str, text: str, plural: str = None, word_type: str = "", binomial: str = None,
                 see: List[str] = None, stories: dict = None, mask: bool = False):
        self.name = name
        self.text = text
        self.plural = plural
        self.word_type = word_type
        self.binomial = binomial
        self.stories = stories
        if type(see) is list:
            self.see = self.see_to_dict(see)
        else:
            self.see = {}
        self.mask = mask

    @classmethod
    def from_row(cls, row: table.Row, stories: dict = None):

        plural = None
        if row["plural"] not in na_vals:
            plural = row["plural"]
        word_type = None
        if row["type"] not in na_vals:
            word_type = row["type"]
        binomial = None
        if row["binomial"] not in na_vals:
            binomial = row["binomial"]
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
            dictionary["type"] = self.word_type
        if self.binomial is not None:
            dictionary["binomial"] = self.binomial

        return dictionary

    def see_to_dict(self, see):
        stories_dict = {}
        for name in see:
            story = self.stories[name]
            if ":" in name:
                series = name[:name.find(":")]
                if series not in stories_dict:
                    stories_dict[series] = [story]
                else:
                    stories_dict[series].append(story)
            else:
                stories_dict[name] = story
        return stories_dict

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
                    if len(story_entry) == 1 and not story_entry[0]["mask"]:
                        story_html += f'\t\t\t\t<i><a href="{story_entry[0]["url"]}">{series_title}</i> - {story_entry[0]["title"]}</a>\n'
                    elif len:
                        story_html += \
                            f"\t\t\t\t<i><a href='{url}'>{series_title}</a></i>\n" \
                            f"\t\t\t\t<ul>\n"
                        for sub_story_entry in story_entry:
                            story_html += f'\t\t\t\t\t<li><a href="{sub_story_entry["url"]}">{sub_story_entry["title"]}</a></li>\n'
                        story_html += "\t\t\t\t</ul>\n"
                else:
                    story_html += f'\t\t<i><a href="{story_entry["url"]}">{story_entry["title"]}</a></i>\n'

                story_html += "\t\t\t</li>\n"
                html_str += story_html

            html_str += "\t\t</ul>\n"

        return html_str

    def to_html(self):
        if self.mask:
            html_str = ""
        else:
            html_str = \
                f"\t<li><b>{self.name}:</b> {self.text} {self.see_to_html()}\n" \
                f"\t</li>\n\n"
        return html_str


# TODO: Check if the files are correctly formatted
# TODO: Write to file; and
# TODO: write empty template file (as classmethod using dummy instance)
class Glossary:
    def __init__(self, path: str):
        story_path = os.path.join(path, "stories.csv")
        glossary_path = os.path.join(path, "glossary.csv")

        self.glossary_table = table.Table.read(glossary_path, format="ascii.csv", encoding="utf-16")
        self.glossary_table.sort('name')
        self.story_table = table.Table.read(story_path, format="ascii.csv", encoding="utf-16")

        self.stories = {}
        self.parse_story_table()

        self.glossary = {}
        self.parse_glossary()

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

    def __getitem__(self, key):
        return self.glossary[key]

    def __setitem__(self, key: str, value: GlossaryEntry):
        if value is not GlossaryEntry:
            raise TypeError("Can only directly set values of type GlossaryEntry")
        self.glossary[key] = value
