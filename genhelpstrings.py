"""Automatically generate guidemd/helpstrings.md guide from guiscript/_guis/help.py"""

import guiscript
import json

class GenHelpStrings:
    content = """[<- Back to guide](./guide.md)
# Help Strings
This same strings can be accessed calling the following functions.
"""

    @classmethod
    def gen_help_string(cls, name, string):
        cls.content += f"\n## {name}()\n```"
        cls.content += string
        cls.content += "\n```\n"
        
    @classmethod
    def generate(cls):
        cls.gen_help_string("help_element_types", guiscript.help_element_types())
        cls.gen_help_string("help_callbacks", guiscript.help_callbacks())
        cls.gen_help_string("help_events", guiscript.help_events())
        cls.gen_help_string("help_buffers", guiscript.help_buffers())
        cls.gen_help_string("help_z_index", json.dumps(guiscript.help_z_index(), indent=2))
        cls.gen_help_string("help_navigation", guiscript.help_navigation())
        cls.gen_help_string("help_rich_text", guiscript.help_rich_text())
        cls.gen_help_string("help_style_script", guiscript.help_style_script())
        
    @classmethod
    def save(cls):
        with open("guidemd/helpstrings.md", "w") as file:
            file.write(cls.content)
            
GenHelpStrings.generate()
GenHelpStrings.save()
