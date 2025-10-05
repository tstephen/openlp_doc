"""
documenter.py
"""

import io
import json
import zipfile
from os.path import splitext

import pdfkit
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel


class DocumenterOptions(BaseModel):
    """options expected by Documenter"""

    verbose: int = 2


class Documenter:
    """
    Render songs and services
    """

    def __init__(self, options):
        self.options = options
        self.env = Environment(loader=FileSystemLoader("./openlp_doc/templates"))
        self.song_template = self.env.get_template("serviceitem.html")
        self.service_template = self.env.get_template("service.html")

    def render_service(self, osj_file: str):
        """render a service from its JSON representation"""
        songs = []

        with zipfile.ZipFile(osj_file) as zf:
            with io.TextIOWrapper(zf.open("service_data.osj"), encoding="utf-8") as f:
                service = json.load(f)
                for idx, obj in enumerate(service):
                    if obj.get("serviceitem") is not None:
                        songs.append(self.render_song_json(obj.get("serviceitem")))
                    else:
                        print(f"not a service item: {obj}")

        output = self.service_template.render(service=service, songs=songs)
        out_file = splitext(osj_file)[0]
        with open(f"{out_file}.html", "w") as output_file:
            output_file.write(output)

        print(f"HTML generation successful. Output saved to '{out_file}.html'.")
        pdfkit.from_file(
            f"{out_file}.html",
            f"{out_file}.pdf",
            verbose=True,
            options={"enable-local-file-access": True},
        )
        print(f"PDF generation successful. Output saved to '{out_file}.pdf'.")
        return output

    def render_song_json(self, serviceitem: dict):
        """render a single song from its JSON representation"""
        return self.song_template.render(song=serviceitem)
