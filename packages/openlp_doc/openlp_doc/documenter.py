"""
documenter.py
"""

import io
import json
import zipfile
from os.path import splitext
from pathlib import Path

import pdfkit
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from .imager import ImageError, Imager


class DocumenterOptions(BaseModel):
    """options expected by Documenter"""

    verbose: int = 2
    slides: bool = False


class Documenter:
    """
    Render songs and services
    """

    def __init__(self, options):
        self.options = options
        import os

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.item_template = self.env.get_template("serviceitem.html")
        self.service_template = self.env.get_template("service.html")
        self.slides_template = self.env.get_template("slides.html")

        # Initialize the Imager for converting images to data URLs
        self.imager = Imager()

    def render_service(self, osj_file: str):
        """render a service from its JSON representation"""
        songs = []

        with zipfile.ZipFile(osj_file) as zf:
            with io.TextIOWrapper(
                zf.open("service_data.osj"), encoding="utf-8"
            ) as f:
                service = json.load(f)
                for idx, obj in enumerate(service):
                    if obj.get("serviceitem") is not None:
                        item = obj.get("serviceitem")
                        print(
                            f"{idx}: is a service item of type: {item.get('header', {}).get('plugin')}"
                        )
                        songs.append(self.render_item_json(item, zf))
                    else:
                        print(f"{idx}: not a service item: {obj}")

        out_file = splitext(osj_file)[0]
        if self.options.slides:
            output = self.slides_template.render(
                service=service,
                songs=songs,
            )
            out_file = f"{out_file}_slides"
        else:
            output = self.service_template.render(
                service=service,
                songs=songs,
                slides=self.options.slides,
            )
        with open(f"{out_file}.html", "w") as output_file:
            output_file.write(output)

        print(
            f"HTML generation successful. Output saved to '{out_file}.html'."
        )
        if not self.options.slides:
            pdfkit.from_file(
                f"{out_file}.html",
                f"{out_file}.pdf",
                verbose=True,
                options={
                    "enable-local-file-access": True,
                    "orientation": ("Portrait"),
                },
            )
            print(
                f"PDF generation successful. Output saved to '{out_file}.pdf'."
            )
        return output

    def _process_image_data(
        self, image_data: dict, zip_file: zipfile.ZipFile = None
    ) -> str:
        """
        Process image data and return a data URL

        Args:
            image_data: Dictionary containing image path information
            zip_file: ZipFile object to extract images from

        Returns:
            Data URL string for the image, or empty string if processing fails
        """
        try:
            if "parts" in image_data:

                if zip_file:
                    # OpenLP stores images as "f.png" and "thumbnails/f.png"
                    # but references them as "images/thumbnails/f.png"
                    # we want the full size option
                    zip_path = image_data["parts"][-1]
                    try:
                        with zip_file.open(zip_path) as img_file:
                            # Read image data and convert to data URL
                            image_bytes = img_file.read()
                            return self.imager.bytes_to_data_url(
                                image_bytes, splitext(zip_path)[1]
                            )
                    except KeyError:
                        print(f"Warning: Image not found in zip: {zip_path}")
                else:
                    # Fallback to file system (for tests)
                    # Join the parts to create the relative path
                    relative_path = Path(*image_data["parts"])
                    # Check if the file exists relative to current directory
                    if relative_path.exists() and relative_path.is_file():
                        return self.imager.to_data_url(relative_path)
                    else:
                        print(
                            f"Warning: Image file not found: {relative_path}"
                        )

        except (ImageError, Exception) as e:
            print(f"Error processing image: {e}")

        return ""

    def render_item_json(
        self, serviceitem: dict, zip_file: zipfile.ZipFile = None
    ):
        """render a single service item (song, slide etc.) from OpenLP JSON"""

        # Process images if this is an image service item
        if (
            serviceitem.get("header", {}).get("plugin") == "images"
            and "data" in serviceitem
        ):

            # Process each image in the data array
            for item in serviceitem["data"]:
                if "image" in item:
                    data_url = self._process_image_data(
                        item["image"], zip_file
                    )
                    if data_url:
                        # Add the data URL to the item for template use
                        item["data_url"] = data_url

        return self.item_template.render(item=serviceitem)
