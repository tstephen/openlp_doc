"""
suite testing bpmn_documenter class
"""
import json
import logging
import os
from pathlib import Path

import pytest

from openlp_doc.documenter import BpmDocumenterOptions, Documenter

@pytest.fixture(name="documenter", scope="session")
def init_validator():
    """ initialise service class instance """
    logging.basicConfig()
    options = {
        'verbose': 0
    }
    validator = Documenter(BpmDocumenterOptions(**options))
    return validator

def test_render_service(documenter):
    """tests known service resource produces expected output"""
    output = documenter.render_service("./tests/resources/service_data.osj")
    assert output is not None

@pytest.mark.skip(reason="no way of currently testing this")
def test_render_song(documenter):
    """tests known song resource produces expected output"""

    serviceitam = '''{
        "serviceitem": {
        "header": {
            "name": "songs",
            "plugin": "songs",
            "theme": null,
            "title": "Days of Elijah",
            "footer": [
            "Days of Elijah",
            "Written by: James Ferguson",
            "© CityAlight Music"
            ],
            "type": 1,
            "audit": [
            "Days of Elijah",
            [
                "James Ferguson"
            ],
            "CityAlight Music",
            "7121853"
            ],
            "notes": "",
            "from_plugin": true,
            "capabilities": [
            2,
            1,
            5,
            8,
            9,
            13,
            22
            ],
            "search": "",
            "data": {
            "title": "days of elijah@",
            "alternate_title": "",
            "authors": "James Ferguson",
            "ccli_number": "7121853",
            "copyright": "CityAlight Music"
            },
            "auto_play_slides_once": false,
            "auto_play_slides_loop": false,
            "timed_slide_interval": 0,
            "start_time": 0,
            "end_time": 0,
            "media_length": 0,
            "background_audio": [],
            "theme_overwritten": false,
            "will_auto_start": false,
            "processor": null,
            "metadata": [],
            "sha256_file_hash": null,
            "stored_filename": null
        },
            "title": "Days of Elijah",
            "footer": [
        "data": [
            {
            "title": "These are the days of Elijah",
            "raw_slide": "These are the days of Elijah\nDeclaring the word of the Lord\nAnd these are the days of Your servant Moses\nRighteousness being restored\nAnd though these are days of great trial\nOf famine and darkness and sword\nStill, we are the voice in the desert crying\n'Prepare ye the way of the Lord!'",
            "verseTag": "V1"
            },
            {
            "title": "Behold He comes riding on the ",
            "raw_slide": "Behold He comes riding on the clouds\nShining like the sun at the trumpet-call\nLift your voice, it's the year of jubilee\nAnd out of Zion's hill salvation comes, oh come",
            "verseTag": "C1"
            },
            {
            "title": "These are the days of Ezekiel",
            "raw_slide": "These are the days of Ezekiel\nThe dry bones becoming as flesh\nAnd these are the days of Your servant David\nRebuilding a temple of praise\nAnd these are the days of the harvest\nThe fields are as white in Your world\nAnd we are the labourers in Your vineyard\nDeclaring the word of the Lord!",
            "verseTag": "V2"
            }
        ]
      }
    }'''
    documenter.render_song(serviceitam)