# -*- coding: utf-8 -*-

'''
Created on 08-09-2011
'''

import csv

class CsvFile:
    
    """Class used as a wrapper for csv file. Can automatically detect dialect
    of the file or use specified quotechar and delimiter values. 
    """
    
    def __init__(self, filename, quote=None, delim=None, enc='utf-8'):
        """Opens file and creates csv reader object. If quote or delim are
        not specified, then Sniffer object is used to find file's dialect.
        
        Arguments:
        filename -- name of the csv file
        quote -- char used for quoting in the csv file
        delim -- char used as delimiter in the csv file
        enc -- file's encoding format
        """
        self.name = filename
        self.file = open(filename, 'rb')
        self.quote = quote
        self.delim = delim
        if quote or delim:
            self.dialect = None
        else:
            self.dialect = csv.Sniffer().sniff(self.file.read(1024))
            self.file.seek(0)
        self.create_reader()
        self.encoding = enc
    
    def create_reader(self):
        """Creates csv reader object using sniffed dialect
        or quote/delim parameters, depending on what was passed in constructor.
        """
        if self.dialect:
            self.reader = csv.reader(self.file, self.dialect)
        else:
            if self.quote and self.delim:
                self.reader = csv.reader(self.file, quotechar=self.quote, delimiter=self.delim)
            elif self.quote:
                self.reader = csv.reader(self.file, quotechar=self.quote)
            else:
                self.reader = csv.reader(self.file, delimiter=self.delim)
    
    def get_next(self):
        """Reads next line from the file and decodes it using utf-8 decoder."""
        line = self.reader.next()
        #x = [el.decode('utf-8') for el in line]
        try:
            return [el.decode(self.encoding) for el in line]
        except UnicodeDecodeError:
            return line
    
    def get_filename(self):
        """Returns file name."""
        return self.name
    
    def reset(self):
        """Moves to the begining of the file and creates another reader."""
        self.file.seek(0)
        self.create_reader()
    
    def close(self):
        """Closes csv file."""
        self.file.close()


class CsvData:
    
    """Class used to read a csv file. Can read the file at once or row by row.
    Can read lines of the file as lists or dicts. Assumes that the first line
    is header.
    """
    
    def __init__(self, csvfile):
        """Initiates header and rows list. Assumes that the file is not empty
        and has at least one line, which is treated as header.
        
        Arguments:
        csvfile -- CsvFile object, must be at begining position
        """
        self.file = csvfile
        self.header = []
        self.rows = []
        self.header = self.file.get_next()

    def __del__(self):
        """Closes csv file."""
        self.file.close()
    
    def get_next_row(self, row_type='dict'):
        """Gets a next row of the file. If all the file is read, returns None.
        Otherwise returns row in specified type.
        
        Arguments:
        row_type -- specifies the form of the next row, can be 'dict' or 'list'
        """
        if row_type not in ['dict', 'list']:
            raise RuntimeError('Wrong value of parameter row_type')
        try:
            row = self.file.get_next()
            if row_type == 'list':
                return row
            row_dict = {}
            i = 0
            while i < len(self.header):
                col = self.header[i]
                row_dict[col] = row[i]
                i += 1
            return row_dict
        except StopIteration:
            return None
        
    def build(self, rows_type='dict'):
        """Reads all lines from the file and saves them in specified form.
        
        Arguments:
        rows_type -- the same meaning as in get_next_row, specifies form of
                     rows in which rows will be saved, can be 'dict' or 'list'
        """
        row = self.get_next_row(rows_type)
        while row is not None:
            self.rows.append(row)
            row = self.get_next_row(rows_type)
            
    def get_header(self):
        """Returns header of the file as list."""
        return self.header
    
    def get_row(self, i):
        """Returns row nr i of the file. Can be called only if build method
        has been used. Otherwise rows are not saved.
        
        Arguments:
        i -- number of the row(0 for first row)
        """
        return self.rows[i]
    
    def get_rows(self):
        """Returns a copy of the list of all rows of the file."""
        return self.rows[:]
    
    def get_filename(self):
        """Returns name of the csv file."""
        return self.file.get_filename()
        
    def count_values(self, key):
        """Returns dict with all values that appear in field specified by
        key in all rows of the file. Can be used only if the build() method
        has been called and row type is 'dict'.
        
        Arguments:
        key -- value from header
        """
        count_dict = {}
        different_values = 0
        for row in self.rows:
            value = row[key]
            if value not in count_dict and value is not None:
                count_dict[value] = True
                different_values += 1
        
        return {'number': different_values, 'values': count_dict}


class Data:
    
    """Class used to save data in csv file."""
    
    def __init__(self, rows):
        """Saves passed values.
        
        Arguments:
        rows -- data to save, it must be list
        """
        self.rows = rows
        
    def save(self, name, delim=';', quote='"', quoting=csv.QUOTE_NONNUMERIC):
        """Opens file with name = name. Delimiter and quote char values
         can be specified. If file can't be opened, no data will be saved.
        
        Arguments:
        name -- name of the file that will contain data
        delim -- delimiter in the csv file
        quote -- quote char in the cav file
        quoting -- quoting style
        """
        try:
            file = open(name, 'wb')
        except IOError:
            print 'File %s cannot be opened' % name
        writer = csv.writer(file, delimiter=delim, quotechar=quote,
                             quoting=csv.QUOTE_NONNUMERIC)

        for row in self.rows:
            writer.writerow(row)
        file.close()
