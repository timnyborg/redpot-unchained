# flake8: noqa

import os

from fpdf import FPDF

MODULE_DIRECTORY = os.path.dirname(__file__)


class ExtendedFPDF(FPDF):  # pragma: no cover
    """A legacy tool from the php days, translated into python to support old pdf document generators
    NOTE: DO NOT build new pdfs on fpdf.  Instead use Weasyprint with Django's html template rendering.
    """

    def __init__(self):
        self.widths = None
        self.aligns = None
        super(ExtendedFPDF, self).__init__()

    def basic_table(self, header, data, col_widths, borders, font_type, cell_type):
        """# *************************************************************************
        *Basic table
        *Outputs simple table onto the page:
        *header - array containing column headings
        *data - multi-array containing rows/field data
        *col_widths - array containing width settings for each column in table
        *borders - TLRB border indicators for each row in the table
        *font_type - indicator as to size of text to be used
        *cell_type - cell or multi_cell depending on amount of text to be displayed
        ***************************************************************************/"""

        #  Header
        i = 0
        j = 0
        if header:
            if font_type == 'large':
                self.set_font('arial_ttf', 'B', 12)
            elif font_type == 'medium':
                self.set_font('arial_ttf', 'B', 10)
            elif font_type == 'small':
                self.set_font('arial_ttf', '', 8)
            for col in header:
                self.cell(col_widths[i], 7, col, borders[j])
                i += 1
                j += 1

            self.ln()

        # Data
        if font_type == 'large':
            self.set_font('arial_ttf', 'B', 10)
        elif font_type == 'medium':
            self.set_font('arial_ttf', '', 9)
        elif font_type == 'small':
            self.set_font('arial_ttf', '', 8)

        for row in data:
            i = 0
            for col in row:
                if cell_type == 'Cell':
                    self.cell(col_widths[i], 5, col, borders[j])
                else:
                    self.multi_cell(col_widths[i], 4, col, borders[j])
                i += 1
                j += 1

            self.ln()

    def improved_multi_cell_table(
        self,
        header=None,
        data=None,
        footer=None,
        header_border=1,
        header_align='C',
        footer_border=1,
        draw_border=True,
        fill=False,
        fonts=None,
    ):
        if data:
            h = 5 * max(self.line_count(self.widths[i], d) for i, d in enumerate(data))
        else:
            h = 7

        if self.y + h > self.page_break_trigger:
            self.add_page()

        if header:
            #  Header
            self.set_font('arial_ttf', 'B', 10)
            for i in range(len(header)):
                w = self.widths[i]
                self.cell(w, 7, header[i], header_border, 0, header_align)

            self.ln()

        elif data:
            for i in range(len(data)):
                w = self.widths[i]
                a = self.aligns[i] or 'L'
                # Save the current position
                x = self.get_x()
                y = self.get_y()
                # Draw the border
                if draw_border:
                    self.rect(x, y, w, h)

                if fill:
                    self.rect(x, y, w, h, style='F')

                # Print the text
                if fonts:
                    # Three-item tuples, e.g. ('', 'B', 11)
                    self.set_font(*fonts[i])

                self.multi_cell(w, 5, data[i], 0, a)

                # Put the position to the right of the cell
                self.set_xy(x + w, y)

            self.ln(h)

        else:
            #  Closing line
            self.set_font('arial_ttf', 'B', 10)
            tmp_w = []
            for i in range(len(footer)):
                w = self.widths[i]
                tmp_w.append(w)
                self.cell(w, 7, footer[i], footer_border, 0, 'R')  # Useless footerfill was here

            self.cell(sum(tmp_w), 0, '')

    def improved_table(
        self,
        header,
        data,
        col_widths,
        footer,
        footer_col_widths,
        border=0,
        fill=False,
        footerfill=False,
        header_align='L',
    ):

        #  Column widths
        w = col_widths
        #  Header
        self.set_font('arial_ttf', 'B', 10)
        for i in range(len(header)):
            self.cell(w[i], 7, header[i], border, 0, header_align)

        self.ln()
        #  Data
        self.set_font('arial_ttf', '', 10)

        from itertools import cycle

        if fill:
            try:
                # If we've got an iterable object for the fill (eg striping), we'll use it
                fill = cycle(fill)
            except TypeError:
                # Otherwise it's a constant
                fill = cycle([fill])

        for row in data:
            z = len(row)
            y = 0
            x = 0

            if fill:
                field_fill = next(fill)
            else:
                field_fill = False

            for col in row:
                if z != y + 1:
                    self.cell(w[y], 6, col, border, 0, '', field_fill)

                else:
                    self.cell(w[y], 6, col, border, 0, 'R', field_fill)
                y += 1

            self.ln()
            x += 1

        # Closing line
        self.set_font('arial_ttf', 'B', 10)

        for i in range(len(footer)):
            if footerfill:
                footer_fill = footerfill[i]
                self.set_fill_color(230, 230, 230)
            else:
                footer_fill = False
            self.cell(footer_col_widths[i], 7, footer[i], border, 0, 'R', footer_fill)

        self.cell(sum(w), 0, '')

    def set_widths(self, w):
        # Set the array of column widths
        self.widths = w

    def set_aligns(self, a):
        # Set the array of column alignments
        self.aligns = a

    def line_count(self, w, txt):
        # Computes the number of lines a multi_cell of width w will take
        cw = self.current_font['cw']

        if w == 0:
            w = self.w - self.r_margin - self.x
        wmax = (w - 2 * self.c_margin) * 1000 / self.font_size
        s = txt.strip("\r")  # TODO: Make sure this translation works
        nb = len(s)
        if nb > 0 and s[nb - 1] == "\n":
            nb -= 1
        sep = -1
        i = 0
        j = 0
        l = 0
        nl = 1
        while i < nb:
            c = s[i]
            if c == "\n":
                i += 1
                sep = -1
                j = i
                l = 0
                nl += 1

            if c == ' ':
                sep = i
            l += cw[ord(c)]  # 556 is a good default

            if l > wmax:
                if sep == -1:
                    if i == j:
                        i += 1

                else:
                    i = sep + 1
                sep = -1
                j = i
                l = 0
                nl += 1

            else:
                i += 1
        return nl

    # Wrapper function to allow a the class to have parent reference
    def PrettyTable(self, **kwargs):
        pretty_table = self._PrettyTable(self, **kwargs)
        return pretty_table

    # Inner pretty table class, returned by the wrapper
    class _PrettyTable:
        def __init__(
            self,
            parent,
            header=None,
            body=[],
            footer=None,
            border={},
            fill={},
            align={},
            width={},
            height={},
            font={},
            sticky_header=False,
        ):
            from itertools import cycle

            self.parent = parent

            # Fill style dicts with defaults
            self.border = {
                'header': None,
                'body': None,
                'footer': None,
            }
            self.border.update(border)
            self.fill = {'header': None, 'body': None, 'footer': None}
            self.fill.update(fill)
            self.align = {'header': 'L', 'body': 'L', 'footer': 'L'}
            self.align.update(align)
            self.width = {
                'header': None,
                'body': None,
                'footer': None,
            }
            self.width.update(width)
            self.height = {
                'header': 7,
                'body': 5,
                'footer': 7,
            }
            self.height.update(height)
            self.font = {
                'header': ('arial_ttf', 'B', 10),
                'body': ('arial_ttf', '', 10),
                'footer': ('arial_ttf', 'B', 10),
            }
            self.font.update(font)

            # Create an iterable for body fill
            if not isinstance(self.fill['body'], (list, tuple)):
                self.fill['body'] = [self.fill['body']]
            self.body_fill = cycle(self.fill['body'])

            self._header = None
            if header:
                self.set_header(header)

            self._body = []
            self.body(body)

            self._footer = None
            if footer:
                self.set_footer(footer)

            self.sticky_header = sticky_header

        def _new_page_check(self, height):
            if self.parent.y + height > self.parent.page_break_trigger:
                self.parent.add_page()
                if self.sticky_header:
                    self._print_header()

        def _print_row(self, widths, line_height, data, borders, aligns, fill=None):
            if not data:  # Deal with empty rows
                return

            # Convert constant styling to iterable.  Move this to top?
            if not isinstance(borders, (list, tuple)):
                borders = [borders] * len(data)
            if not isinstance(aligns, (list, tuple)):
                aligns = [aligns] * len(data)

            cell_height = line_height * max(self.parent.line_count(width, text) for width, text in zip(widths, data))
            self._new_page_check(cell_height)

            for width, text, border, align in zip(widths, data, borders, aligns):
                x, y = self.parent.x, self.parent.y
                if border:
                    self.parent.rect(self.parent.x, self.parent.y, width, cell_height)
                if fill:
                    self.parent.set_fill_color(*fill)
                    self.parent.rect(x, y, width, cell_height, style='F')
                self.parent.multi_cell(width, line_height, text, 0, align, 0)
                self.parent.x, self.parent.y = x + width, y
            self.parent.ln(cell_height)

        def _print_header(self):
            if self._header:
                self.parent.set_font(*self.font['header'])
                self._print_row(
                    self.width['header'],
                    self.height['header'],
                    self._header,
                    self.border['header'],
                    self.align['header'],
                    self.fill['header'],
                )

        def _print_body(self):
            # Body
            self.parent.set_font(*self.font['body'])

            for row in self._body:
                self._print_row(
                    self.width['body'],
                    self.height['body'],
                    row,
                    self.border['body'],
                    self.align['body'],
                    next(self.body_fill),
                )

        def _print_footer(self):
            # Footer
            if self._footer:
                self.parent.set_font(*self.font['footer'])
                self._print_row(
                    self.width['footer'],
                    self.height['footer'],
                    self._footer,
                    self.border['footer'],
                    self.align['footer'],
                    self.fill['footer'],
                )

        def render(self):
            self._print_header()
            self._print_body()
            self._print_footer()

        def set_header(self, header):
            self._header = header

        def body(self, _body):
            # Ensure list of lists for body
            if not _body:
                _body = [[]]
            elif not isinstance(_body[0], (list, tuple)):
                _body = [_body]

            self._body += _body

        def set_footer(self, footer):
            self._footer = footer


class ContedPDF(ExtendedFPDF):  # pragma: no cover
    """A legacy tool providing common document layouts
    NOTE: DO NOT build new pdfs on fpdf.  Instead use Weasyprint with Django's html template rendering.
    """

    bottom_left_text = ''  # Content to appear in the footer
    bottom_right_text = ''

    """Forms the base of all of our pdf templates, with a header, footer (eventually), and font initialization
    """

    def __init__(self):
        # We need an explicitly unicode-compatible font, so we've included andaddress
        #  defined it
        # (NB: Any font needs to be placed in the fpdf folder within the web2py source: .../gluon/contrib/fpdf/font)
        super(ContedPDF, self).__init__()

        self.add_font('arial_ttf', '', os.path.join(MODULE_DIRECTORY, 'fonts', 'LiberationSans-Regular.ttf'), uni=True)
        self.add_font('arial_ttf', 'B', os.path.join(MODULE_DIRECTORY, 'fonts', 'LiberationSans-Bold.ttf'), uni=True)
        self.add_font('roboto_ttf', '', os.path.join(MODULE_DIRECTORY, 'fonts', 'Roboto-Light.ttf'), uni=True)
        self.add_font('roboto_ttf', 'B', os.path.join(MODULE_DIRECTORY, 'fonts', 'Roboto-Bold.ttf'), uni=True)
        self.add_font('roboto_ttf', 'I', os.path.join(MODULE_DIRECTORY, 'fonts', 'Roboto-LightItalic.ttf'), uni=True)
        self.set_font('arial_ttf')
        self.set_margins(20, 20)
        self.set_auto_page_break(True, margin=28)  # Gives us the bottom margin for the footer
        self.alias_nb_pages()
        self.add_page()

    def header(self):
        # Header is automatically included onto the top of every page
        # Logo
        logo = os.path.join(MODULE_DIRECTORY, 'images', 'document_logo.png')
        self.image(logo, 160, 20, 30, 30)

        # Title
        self.set_font('', '', 12)
        self.cell(30, 6, 'DEPARTMENT FOR CONTINUING EDUCATION', ln=1)
        self.set_font_size(9)
        self.cell(30, 4, 'Rewley House, 1 Wellington Square, Oxford, OX1 2JA', ln=1)
        self.cell(30, 4, 'Tel: +44 (0)1865 270360       Fax: +44 (0)1865 280760', ln=1)
        self.cell(30, 4, 'enquiries@conted.ox.ac.uk         www.conted.ox.ac.uk', ln=1)
        self.ln(20)

    def footer(self):
        # Footer is automatically included onto the bottom of every page
        # Position at 1.5 cm from bottom
        self.set_y(-25)
        self.cell(0, 4, '', 'T', 1)  # Horizontal line
        self.set_font('', '', 8)

        if self.bottom_left_text:
            self.cell(0, 3, self.bottom_left_text)

        if self.bottom_right_text:
            self.cell(0, 3, self.bottom_right_text, 0, 1, 'R')
            # Page number.  {nb} does WEIRD stuff to the formatting, so we include the cell differently depending on
            # the preceding cell
            self.cell(174, 3, 'Page %s/{nb}' % self.page_no(), 0, 1, 'R')
        else:
            self.cell(0, 3, 'Page %s/{nb}' % self.page_no(), 0, 1, 'R')

    def address_block(self, block):
        self.set_font('', '', 12)
        for line in block:
            self.cell(0, 5, line, ln=1)
