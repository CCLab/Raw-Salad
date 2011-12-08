# -*- coding: utf-8 -*-

'''
Created on 25-08-2011
'''

from data_wrapper import CsvFile, CsvData

class DataValidator:
    
    """Class used to validate data in csv file. Uses schema to complete
    the task. Can check number of values in rows and their types. Also checks
    if each obligatory field has not empty value. Enables rule mechanism that
    allows correctly validating data with some exceptions in it, e.g. field
    nr 2 is obligatory, but should be empty if field 3 is 'abc'. If any error
    is found, logs it.
    Used schema must have at least following form:
    {
        "fields": [
            {
                "label": string,
                "type": string,
                "obligatory": bool,
            },
            ...
        ]
    }
    Other keys are ignored.
    """
    def __init__(self, file_name, fields, delimiter):
        """Initiates object.
        
        Arguments:
        file_name -- name of file with data
        fields -- description of fields
        delimiter -- delimiter in csv file
        """
        csv_file = CsvFile(file_name, quote='"', delim=delimiter) 
        self.data = CsvData(csv_file)
        self.fields_descr = fields[:]
        self.row_len = len(self.fields_descr)
        self.header_errors = []
        self.data_errors = []
        self.empty_fields = []
        
    def check_all(self):
        """Clears lists of errors and checks if header in the file is correct.
        If there are no errors in header, then data is checked.
        """
        self.header_errors = []
        self.data_errors = []
        self.empty_fields = []
        self.check_header()
        if self.is_header_correct():
            self.check_data()
        
    def is_header_correct(self):
        """Returns True if header is correct, False if not."""
        return self.header_errors == []
    
    def is_data_correct(self):
        """Returns True is data is correct, False if not."""
        return self.data_errors == []
    
    def is_all_correct(self):
        """Returns True if both header and data are correct, False if not."""
        return self.is_header_correct() and self.is_data_correct()
    
    def get_errors_log(self):
        """Returns string representing list of errors in header and data.
        Errors are separated by new line.
        """
        return '\n'.join(self.header_errors + self.data_errors)
        
    def check_header(self):
        """Catches errors in header and saves them. Gets expected names of
        fields in header from schema. Checks if:
        - all fields from schema are in the header
        - there is no unexpected fields(that were not described in schema)
        - order of fields in header is the same as order in schema
        """
        header = self.data.get_header()
        fields_names = [field_descr['label'] for field_descr in self.fields_descr]

        for name in fields_names:
            if name not in header:
                self.header_errors.append('HEADER: missing field %s' % name)
        
        header_copy = header[:]
        for name in fields_names:
            if name in header_copy:
                header_copy.remove(name)
        
        if header_copy != []:
            for name in header_copy:
                self.header_errors.append('HEADER: unknown field %s' % name)
        
        if self.is_header_correct():
            i = 0
            next_header_copy = header[:]
            for name in next_header_copy:
                if name != fields_names[i]:
                    self.header_errors.append('HEADER: field nr %d is %s, %s expected' %
                                       (name, i, fields_names[i]))                  
                i += 1
        else:
            self.header_errors.append('HEADER: will not check fields order due to previous errors')
    
    def check_data(self):
        """Checks data row by row. Checks if:
        - each row has expected number of fields
        - if fields are consistent with schema or rules 
        """
        row = self.data.get_next_row(row_type='list')
        i = 1
        while row is not None:
            if len(row) != self.row_len:
                self.data_errors.append('ROW nr %d: unexpected length of the row: %d' % (i, len(row)))
            field_nr = 0
            for field in row:
                self.check_field(field, i, field_nr)
                field_nr += 1
            
            row = self.data.get_next_row(row_type='list')
            i += 1
            
    def check_field(self, value, row_nr, field_nr):
        """Tries to validate field in a row. Checks if:
        - field is expected(its number is consistent with length of fields
          in schema), it is ok as long as rows have correct length
        - field has nonempty value when it is obligatory
        - float and int values can be correctly casted
        
        Arguments:
        value -- value in the field
        row_nr -- number of the row
        field_nr -- number of the field in the row
        """
        try:
            expected_type = self.fields_descr[field_nr]['type']
            obligatory = self.fields_descr[field_nr]['obligatory']
        except IndexError:
            self.data_errors.append('ROW nr %d, field nr %d(%s): unexpected field' %
                                    (row_nr, field_nr, self.fields_descr[field_nr]['label']))
            return
        
        if value == '':
            if obligatory:
                self.data_errors.append('ROW nr %d, field nr %d(%s): missing value(empty field)' %
                                   (row_nr, field_nr, self.fields_descr[field_nr]['label']))
                if field_nr not in self.empty_fields:
                    self.empty_fields.append(field_nr)
        else:
            if expected_type == 'string':
                pass
            elif expected_type == 'float':
                try:
                    float(value.replace(',','')) #  removing commas from number(if any exist)
                except ValueError:
                    self.data_errors.append('ROW nr %d, field nr %d(%s): value type is string, float expected' %
                                            (row_nr, field_nr, self.fields_descr[field_nr]['label']))
            elif expected_type == 'int':
                try:
                    int(value.replace(',',''))
                except ValueError:
                    value_type = 'float'
                    try:
                        float(value.replace(',',''))
                    except ValueError:
                        value_type = 'string'
                    self.data_errors.append('ROW nr %d, field nr %d(%s): value type is %s, int expected' %
                                            (row_nr, field_nr, value_type, self.fields_descr[field_nr]['label']))
    
    def get_empty_fields(self):
        """Returns list of fields' numbers that are obligatory, but empty
        in any row.
        """
        return self.empty_fields

