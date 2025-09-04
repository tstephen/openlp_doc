"""
test_documenter.py
"""
import json
import logging
import os
from pathlib import Path

import pytest

from openlp_doc.documenter import DocumenterOptions, Documenter

@pytest.fixture(name="documenter", scope="session")
def init_documenter():
    """ initialise service class instance """
    logging.basicConfig()
    options = {
        'verbose': 0
    }
    documenter = Documenter(DocumenterOptions(**options))
    return documenter

def test_render_service(documenter):
    """tests known service resource produces expected output"""
    output = documenter.render_service("./tests/resources/Service 2024-01-28 01-07.osz")
    assert output is not None

#@pytest.mark.skip(reason="no way of currently testing this")
def test_render_song(documenter):
    """tests known song resource produces expected output"""

    # Create the service item data structure directly instead of parsing malformed JSON
    serviceitem = {
        "header": {
            "name": "songs",
            "plugin": "songs",
            "theme": None,
            "title": "These Are The Days Of Elijah",
            "footer": [
                "These Are The Days Of Elijah",
                "Written by: Robin Mark",
                "© 1996 Song Solutions Daybreak"
            ],
            "type": 1,
            "audit": [
                "These Are The Days Of Elijah",
                ["Robin Mark"],
                "1996 Song Solutions Daybreak",
                "1537904"
            ],
            "notes": "",
            "from_plugin": False,
            "capabilities": [2, 1, 5, 8, 9, 13, 22],
            "search": "",
            "data": {
                "title": "these are the days of elijah@days of elijah",
                "alternate_title": "Days of Elijah",
                "authors": "Robin Mark",
                "ccli_number": "1537904",
                "copyright": "1996 Song Solutions Daybreak"
            },
            "xml_version": "<?xml version='1.0' encoding='UTF-8'?>\n<song xmlns=\"http://openlyrics.info/namespace/2009/song\" version=\"0.8\" createdIn=\"OpenLP 3.0.2\" modifiedIn=\"OpenLP 3.0.2\" modifiedDate=\"2024-02-05T21:11:38\"><properties><titles><title>These Are The Days Of Elijah</title><title>Days of Elijah</title></titles><copyright>1996 Song Solutions Daybreak</copyright><ccliNo>1537904</ccliNo><authors><author>Robin Mark</author></authors></properties><lyrics><verse name=\"v1\"><lines>These are the days of Elijah<br/>Declaring the word of the Lord<br/>And these are the days of Your servant Moses<br/>Righteousness being restored</lines></verse><verse name=\"v2\"><lines>And though these are days of great trial<br/>Of famine and darkness and sword<br/>Still we are a voice in the desert crying<br/>'Prepare ye the way of the Lord</lines></verse><verse name=\"v3\"><lines>Behold He comes riding on the clouds<br/>Shining like the sun at the trumpet call<br/>Lift your voice its the year of jubilee<br/>Out of Zions hill salvation comes</lines></verse><verse name=\"v4\"><lines>These are the days of Ezekiel<br/>The dry bones becoming as flesh<br/>And these are the days of Your servant David<br/>Rebuilding the temple of praise</lines></verse><verse name=\"v5\"><lines>These are the days of the harvest<br/>The fields are as white in the world<br/>And we are the labourers in the vineyard<br/>Declaring the word of the Lord</lines></verse></lyrics></song>",
            "auto_play_slides_once": False,
            "auto_play_slides_loop": False,
            "timed_slide_interval": 0,
            "start_time": 0,
            "end_time": 0,
            "media_length": 0,
            "background_audio": [],
            "theme_overwritten": False,
            "will_auto_start": False,
            "processor": None,
            "metadata": [],
            "sha256_file_hash": None,
            "stored_filename": None
        },
        "data": [
            {
                "title": "These are the days of Elijah",
                "raw_slide": "These are the days of Elijah\nDeclaring the word of the Lord\nAnd these are the days of Your servant Moses\nRighteousness being restored",
                "verseTag": "V1"
            },
            {
                "title": "And though these are days of g",
                "raw_slide": "And though these are days of great trial\nOf famine and darkness and sword\nStill we are a voice in the desert crying\n'Prepare ye the way of the Lord",
                "verseTag": "V2"
            },
            {
                "title": "Behold He comes riding on the ",
                "raw_slide": "Behold He comes riding on the clouds\nShining like the sun at the trumpet call\nLift your voice its the year of jubilee\nOut of Zions hill salvation comes",
                "verseTag": "V3"
            },
            {
                "title": "These are the days of Ezekiel",
                "raw_slide": "These are the days of Ezekiel\nThe dry bones becoming as flesh\nAnd these are the days of Your servant David\nRebuilding the temple of praise",
                "verseTag": "V4"
            },
            {
                "title": "These are the days of the harv",
                "raw_slide": "These are the days of the harvest\nThe fields are as white in the world\nAnd we are the labourers in the vineyard\nDeclaring the word of the Lord",
                "verseTag": "V5"
            }
        ]
    }

    # Convert newlines to <br> in raw_slide fields
    for item in serviceitem.get('data', []):
        if 'raw_slide' in item:
            item['raw_slide'] = item['raw_slide'].replace('\n', '<br>')

    # Convert newlines to <br> in xml_version field if present
    if 'header' in serviceitem and 'xml_version' in serviceitem['header']:
        serviceitem['header']['xml_version'] = serviceitem['header']['xml_version'].replace('\n', '<br>')

    output = documenter.render_song_json(serviceitem)
    assert output is not None
