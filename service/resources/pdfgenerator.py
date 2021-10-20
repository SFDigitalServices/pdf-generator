"""Welcome export module"""
import os
import json
import traceback
from typing_extensions import final
import falcon
import sentry_sdk
from . import utils
from .hooks import validate_access

@falcon.before(validate_access)
class PDFGenerator():
    """PDFGenerator class"""
    def on_post(self, req, resp):
        """ Implement POST """
        # pylint: disable=broad-except,no-member
        template_pdf = ''
        try:
            data = json.loads(req.bounded_stream.read())
            template_file = req.get_header('TEMPLATE_FILE')
            if template_file:
                template_pdf = utils.get_pdf_template(template_file)
                pdf_keys = utils.get_pdf_keys(template_pdf)
                utils.write_fillable_pdf(template_pdf, data['request']['data'], pdf_keys)

        except Exception as error:
            print(f"Failed to generate PDF: {error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(error))
        finally: # done with the temp file
            print("done")
            #os.remove(template_pdf)

