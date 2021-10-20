"""PDf form def export module"""
import json
import traceback

from . import utils

class FormFieldDef():
    """PDF form field def class"""
    def on_get(self, req, resp):
        """ Implement GET """
        # pylint: disable=broad-except,no-member
        template_pdf = ''
        formfield_def = ''
        try:
            template_file = req.get_header('TEMPLATE_FILE')
            if template_file:
                template_pdf = utils.get_pdf_template(template_file)
                formfield_def = utils.get_pdf_keys(template_pdf)
                print(formfield_def)
                resp.text = json.dumps(formfield_def)

        except Exception as error:
            print(f"Failed to generate PDF: {error}")
            print(traceback.format_exc())
            resp.text = json.dumps(str(error))
        finally: # done with the temp file
            resp.text = json.dumps(formfield_def)

