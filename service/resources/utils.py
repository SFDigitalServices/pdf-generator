import os
import requests
import traceback
import time
import pdfrw

# PDF Format Keys
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_FIELD_TYPE = '/FT'
ANNOT_FIELD_FLAG = 'Ff'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
PARENT_KEY = '/Parent'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

def write_fillable_pdf(basename, data_dict, keyfile):
    '''
    Generates a read-only PDF
    '''
    # Merge it with the original PDF
    output_pdf_path = os.path.join(os.path.dirname(__file__), 'filled/output_1.pdf')
    merge_pdf(basename, output_pdf_path, data_dict,  keyfile)

    # Circle back and handle grouped buttons
    #do_buttons(basename, data_dict, keyfile)
def merge_pdf(input_pdf_path, output_pdf_path, data_dict, pdf_keys):
    """
    Combine data with pdf tempate
    """
    print(data_dict)
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        for annotation in annotations:
            # only form fields matter
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                # check for grouped radios
                if annotation['/AS'] and annotation[PARENT_KEY] \
                    and annotation[PARENT_KEY][ANNOT_FIELD_TYPE] == '/Btn':
                    radio_button(annotation,  data_dict)
                    #print(annotation)
                elif annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY].to_unicode()
                    if key in data_dict:
                        form_type = field_type(annotation)
                        if form_type == 'text':
                            text_form(annotation, data_dict[key])
                            annotation.update(pdfrw.PdfDict(AP=''))
                        elif form_type == 'list':
                            listbox(annotation, data_dict[key])
                        elif form_type == 'checkbox':
                            checkbox(annotation, data_dict[key])
                        elif form_type == 'radio':
                            radio_button(annotation, data_dict[key])
                        elif form_type == 'combo':
                            combobox(annotation, data_dict[key])
                            annotation.update(pdfrw.PdfDict(AP=''))
                            print(key + " " + str(annotation['/V']) + " " + str(annotation['/AS']))
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

def field_type(annotation):
    ft = annotation[ANNOT_FIELD_TYPE]
    ff = annotation[ANNOT_FIELD_FLAG]

    if ft == '/Tx':
        return 'text'
    if ft == '/Ch':
        if ff and int(ff) & 1 << 17:  # test 18th bit
            return 'list'
        else:
            return 'combo'
    if ft == '/Btn':
        if ff and int(ff) & 1 << 15:  # test 16th bit
            return 'radio' #non-grouped radios
        else:
            return 'checkbox'

def radio_button(annotation, data_dict):
    key = annotation[PARENT_KEY][ANNOT_FIELD_KEY].to_unicode()
    value  = data_dict[key]
    if '/N' in annotation['/AP']:
        selected = annotation['/AP']['/N'].keys()[1].strip(('/'))
        if selected == value:
            for data_key in data_dict:
                if key == data_key:
                    annotation[PARENT_KEY].update(pdfrw.PdfDict(V=pdfrw.objects.pdfname.BasePdfName(f'/{value}')))

def checkbox(annotation, value, export=None):
    if export:
        export = '/' + export
    else:
        keys = annotation['/AP']['/N'].keys()
        if '/Off' in keys:
            keys.remove('/Off')
        export = keys[0]
    if value:
        annotation.update(pdfrw.PdfDict(V=export, AS=export))

def combobox(annotation, value):
    if type(value) is list:
        listbox(annotation, value)
    else:
        export=None
        value = pdfrw.objects.pdfstring.PdfString.encode(str(value))
        for each in annotation['/Opt']:
            if type(each) is list:
                if each[1].to_unicode()==value:
                    export = each[0].to_unicode()
            else:
                export = value
        if export is None:
            raise KeyError(f"Export Value: {value} Not Found")
        annotation.update(pdfrw.PdfDict(V=value, AS=value))

def listbox(annotation, values):
    pdfstrs=[]
    for value in values:
        export=None
        for each in annotation['/Opt']:
            if type(each) is pdfrw.objects.pdfarray.PdfArray:
                if each[1].to_unicode()==str(value):
                    export = each[1].to_unicode()
            elif each.to_unicode()==str(value):
                export = each.to_unicode()
        if export is None:
            raise KeyError(f"Export Value: {value} Not Found")
        pdfstrs.append(pdfrw.objects.pdfstring.PdfString.encode(export))
    annotation.update(pdfrw.PdfDict(V=pdfstrs, AS=pdfstrs))

def text_form(annotation, pdfstr):
    annotation.update(pdfrw.PdfDict(V=pdfstr, AS=pdfstr))

def get_pdf_template(file_url):
    """
    Downloads data mapping from a source
    """
    r = requests.get(file_url, stream=True)
    chunk_size = 2000
    ts = time.time()
    #template_pdf = os.path.dirname(__file__) + '/template/tmp_' + str(ts) + '.pdf'
    template_pdf = os.path.dirname(__file__) + '/filled/SolarPanelTemplate.pdf'
    try:
        with open(template_pdf, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
            return template_pdf
    except Exception as error:
        print(f"Failed to get PDF template: {error}")
        print(traceback.format_exc())
        return ''

def get_pdf_keys(template_pdf):
    '''
    Helper function for generating pdf form field keys, debugging, etc.
    '''

    template_pdf = pdfrw.PdfReader(template_pdf)
    annotations = template_pdf.pages[0][ANNOT_KEY]
    keys = {}
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    type = annotation[ANNOT_FIELD_TYPE]
                    keys[key] = type
                elif annotation['/AS']:
                    parent_key = annotation[PARENT_KEY][ANNOT_FIELD_KEY][1:-1].strip('(').strip(')')
                    field = annotation['/AP']['/D'].keys()[1].strip('/')
                    if parent_key not in keys:
                        keys[parent_key] = {}
                        keys[parent_key]['type'] = 'BUTTONS'
                        keys[parent_key]['child'] = []
                        keys[parent_key]['annot_type'] = annotation[ANNOT_FIELD_TYPE]
                        keys[parent_key]['subtype'] = annotation[SUBTYPE_KEY]
                        keys[parent_key]['parentkey'] = annotation[PARENT_KEY][ANNOT_FIELD_KEY]

                    keys[parent_key]['child'].append(field)
                else:
                    continue
    return keys
