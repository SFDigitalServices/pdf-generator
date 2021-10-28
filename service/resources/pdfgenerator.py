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
        output_pdf = ''
        try:
            data = json.loads(req.bounded_stream.read())
            template_file = req.get_header('TEMPLATE_FILE')
            if template_file and data:
                basename = os.path.dirname(__file__)
                output_pdf = utils.write_fillable_pdf(basename, data, template_file)
                with open(output_pdf, 'rb') as fd:
                    pdf = fd.read()
                    resp.body = pdf
                    fd.close()
        except ValueError as value_error:
            print(f"Failed to merge form data: {value_error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(value_error))
        except IOError as io_error:
            print(f"Failed to read PDF template: {io_error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(io_error))
        except Exception as error:
            print(f"Failed to generate PDF: {error}")
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500   # pylint: disable=no-member
            resp.text = json.dumps(str(error))
        finally: # clean up
            if len(output_pdf) > 1:
                os.remove(output_pdf)

