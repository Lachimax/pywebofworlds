import csv
import os

from astropy import table

from typing import List

na_vals = ["", None]


class GlossaryEntry:
    def __init__(self, name: str, text: str, plural: str = None, word_type: str = "", binomial: str = None,
                 see: List[str] = None):
        self.name = name
        self.text = text
        self.plural = plural
        self.word_type = word_type
        self.binomial = binomial
        self.see = []
        self.see.append(see)

    @classmethod
    def from_row(cls, row):

        plural = None
        if row["plural"] not in na_vals:
            plural = row["plural"]
        word_type = None
        if row["type"] not in na_vals:
            word_type = row["type"]
        binomial = None
        if row["binomial"] not in na_vals:
            binomial = row["binomial"]

        see_str = row["see"]
        see_split = []
        for string in see_str.split():
            string = string[:string.find(";")]
            see_split.append(string)

        return cls(name=row["name"],
                   text=row["text"],
                   plural=plural,
                   word_type=word_type,
                   binomial=binomial,
                   see=see_split
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

        return


class Glossary:
    def __init__(self, path: str):
        story_path = os.path.join(path, "stories.csv")
        glossary_path = os.path.join(path, "glossary.csv")

        self.glossary_table = table.Table.read(glossary_path, format="ascii.csv")
        self.story_table = table.Table.read(story_path, format="ascii.csv")

        self.glossary = {}
        self.parse_glossary()

    def parse_glossary(self):
        for row in self.glossary_table:
            entry = GlossaryEntry.from_row(row=row)
            self.glossary[entry.name] = entry
