from PyPDF2 import utils, PdfFileReader
from commonutils import commonutils
import io
import os


class PDF:
    def __init__(self, source, name):
        self.source = source
        self.name = name
        self.pdfReader = PdfFileReader(io.BytesIO(self.source))

    def is_10K(self):
        try:
            if self.pdfReader.isEncrypted:
                self.decrypt()
            if self.pdfReader is None:
                return False
            for i in range(0, self.pdfReader.getNumPages()):
                pageObj = self.pdfReader.getPage(i)
                text = str(pageObj.extractText())
                if 'SECURITIES AND EXCHANGE COMMISSION' and 'Washington, D.C. 20549' in text:
                    if '10-K' in text:
                        return True
                    else:
                        return False

        except utils.PdfReadError as e:
            self.log_error('Error while reading from PDF object {0}: {1}'.format(self.name, str(e)))
            return None

    def get_year(self):
        try:
            if self.pdfReader.isEncrypted:
                self.decrypt()
            if self.pdfReader is None:
                return -1
            for i in range(0, self.pdfReader.getNumPages()):
                pageObj = self.pdfReader.getPage(i)
                text = str(pageObj.extractText())
                if 'SECURITIES AND EXCHANGE COMMISSION' and 'Washington, D.C. 20549' in text:
                    text = str(pageObj.extractText()).split(',')[2].lstrip(' ')
                    if commonutils.is_number(text[:4]):
                        year = int(float(text[:4]))
                        return year
                    else:
                        return -1

        except utils.PdfReadError as e:
            self.log_error('Error while reading from PDF object {0}: {1}'.format(self.name, str(e)))
            return None

    def decrypt(self):
            try:
                self.pdfReader.decrypt('')
                print('File Decrypted (PyPDF2)')
            except NotImplementedError as e:
                command = ("cp " + self.name +
                           " temp.pdf; qpdf --password='' --decrypt temp.pdf " + self.name
                           + "; rm temp.pdf")
                os.system(command)
                try:
                    fp = open(self.name)
                    print('File Decrypted (qpdf)')
                    return PdfFileReader(fp)
                except FileNotFoundError as e:
                    self.log_error('Error while reading from encrypted file {0}: {1}'.format(self.name, str(e)))
                    return None

    def log_error(self, e):
        print(e)

