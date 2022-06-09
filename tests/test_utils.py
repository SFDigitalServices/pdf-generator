# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import json
import os
from unittest.mock import patch
from testfixtures import ShouldRaise
from service.resources import utils

basename = os.path.dirname(__file__)
file_url = "https://sfdsoewd.blob.core.usgovcloudapi.net/uploads/solarpanel/SolarPanelTemplatev3.pdf"
input = basename + "/template/SolarPanelTemplateTest.pdf"
output = basename + "/filled/test_output.pdf"

with open('tests/mocks/submissions.json', 'r') as file_obj:
        mock_data = json.load(file_obj)

with open('tests/mocks/bad-submission.json', 'r') as file_obj:
        bad_mock_data = json.load(file_obj)

def test_write_fillable_pdf():
    # pylint: disable=unused-argument
    """
        Test utils: write fillable pdf
    """
    # happy path
    response = utils.write_fillable_pdf(basename, mock_data, file_url)
    assert len(response) > len(basename)

    # exceptions - IOError
    with ShouldRaise(Exception):
        fakebasename = "dummy/" + basename
        utils.write_fillable_pdf(fakebasename, mock_data, file_url)

    # exceptions - ValueError
    with ShouldRaise(Exception):
        bad_file_url = file_url + ".pdf"
        utils.write_fillable_pdf(basename, mock_data, bad_file_url)

def test_merge_pdf():
    # pylint: disable=unused-argument
    """
        Test utils: merge_pdf
    """
    # happy path
    response = utils.merge_pdf(input, output, mock_data)
    assert response == output

    # exceptions - ValueError
    with ShouldRaise(Exception):
        bad_input = file_url + ".pdf"
        response = utils.merge_pdf(bad_input, output, mock_data)

    os.remove(output)


