# -*- coding: utf-8 -*-

'''
Created on 25-08-2011
'''

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
    def __init__(self, csv_data, schema_descr):
        """Initiates object.
        
        Arguments:
        csv_data -- CsvData object
        schema_descr -- description of schema, must have following keys:
                        fields -- objects describing fields in data,
                        important_order -- if order 
        """
        self.data = csv_data
        self.fields_descr = schema_descr['fields']
        self.row_len = len(schema_descr['fields'])
        self.header_errors = []
        self.data_errors = []
        self.empty_fields = []
        self.rules = []
        self.add_rules()
    
    # TODO: change it so that it accepts rules saved in a file
    def add_rules(self):
        """Adds rules. Now it's hardcoded method and should be changed so that
        rules can be read from a file.
        """
        # example of a hardcoded rule
        """caly_kraj_cond = {
            6: ['Cały kraj', 'Dolnośląskie', 'Kujawsko-pomorskie', 'Lubelskie',
                'Lubuskie', 'Łódzkie', 'Małopolskie', 'Mazowieckie', 'Opolskie',
                 'Podkarpackie', 'Podlaskie', 'Pomorskie', 'Śląskie',
                 'Warmińsko-mazurskie', 'Wielkopolskie', 'Zachodniopomorskie' 
                ]
        }
        caly_kraj_exp_vals = {
            7: [''],
            8: ['']
        }
        caly_kraj_rule = Rule(caly_kraj_cond, caly_kraj_exp_vals)
        self.rules.append(caly_kraj_rule)
        """
        
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
                expected = self.get_expected_values(row, field_nr)
                self.check_field(field, i, field_nr, expected)
                field_nr += 1
            
            row = self.data.get_next_row(row_type='list')
            i += 1
            
    def check_field(self, value, row_nr, field_nr, exp_values=[]):
        """Tries to validate field in a row. Checks if:
        - value is in the list of expected values(if it is not empty)
        - field is expected(its number is consistent with length of fields
          in schema), it is ok as long as rows have correct length
        - field has nonempty value when it is obligatory
        - float and int values can be correctly casted
        
        Arguments:
        value -- value in the field
        row_nr -- number of the row
        field_nr -- number of the field in the row
        exp_values -- list of expected values, implicitly it is empty(if there
                      are no rules)
        """
        if exp_values != []:
            if value not in exp_values:
                self.data_errors.append('ROW nr %d, field nr %d(%s): value is %s, expected value from list: %s' %
                                        (row_nr, field_nr, value, exp_values, self.fields_descr[field_nr]['label']))
            return
        
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
    
    def get_expected_values(self, row, field_nr):
        """Uses list of rules to check, if the row accepts any rules.
        Returns list of expected values for field nr field_nr in the row.
        
        Arguments:
        row -- row of data
        field_nr -- number of field that is checked
        """
        expected_values = []
        for rule in self.rules:
            if rule.conditions_met(row):
                expected_values.extend(rule.get_expected_values(field_nr))
        return expected_values
    
    
class Rule:
    
    """Class describing rules(exceptions to schema) that might appear in data.
    Each rule has conditions and values. They form is the same and following:
    {
        (int)field_nr: [ list of values ],
        ...
    }
    Rule is accepted when for each field_nr, value number field_nr in row is
    in that list. Then expected values of fields of the row are in the values
    dict[field_nr], e.g.
    conds = {
        1: ['abc', 'def'],
        3: ['qwe']
    }
    values = {
        2: ['', 'zxc'],
        4: ['']
    }
    If row[1] is 'abc' or 'def' and row[3] == 'qwe',
    then row[2] should be in '' or 'zxc' and row[4] == ''.
    """
    
    def __init__(self, conditions, values):
        """Initiates rule with conditions and expected values.
        
        Arguments:
        conditions -- conditions needed to accept this Rule 
        values -- expected values of fields in row
        """
        self.conditions = conditions
        self.values = values
    
    def conditions_met(self, row):
        """Returns True if this Rule can be accepted by the given row,
        False if not.
        
        Arguments:
        row -- row to check 
        """
        for field, field_values in self.conditions.iteritems():
            row_value = row[field]
            if row_value not in field_values:
                return False
        return True
    
    def get_expected_values(self, field_nr):
        """Returns list of expected values for the field of number field_nr."""
        try:
            return self.values[field_nr]
        except KeyError:
            return []
    