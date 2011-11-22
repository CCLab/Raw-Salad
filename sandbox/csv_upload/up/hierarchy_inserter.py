# -*- coding: utf-8 -*-

'''
Created on 25-08-2011
'''

from data_wrapper import CsvFile, CsvData

class HierarchyInserter:
    
    """Inserts hierarchy from the given collection. Uses hierarchy described in
    object of the following form:
    {
        "columns": [list of columns creating hierarchy],
        "field_type_label": name of column(that will be inserted), representing
                            type of row(position in hierarchy),
        "field_name_label": name of column(that will be inserted), representing
                            name of row,
        "name_column": number of column which value represents name of data row
                       and will be moved to new field(its name is field_name_label),
        "lowest_type": name that will be inserted to the type column in rows
                       that are in the lowest position in hierarchy
        "summable": [list of columns that should be summed after creating hierarchy]
    }
    Data passed to HierarchyInserter should be correct, otherwise created
    data will contain bugs.
    """
    
    def __init__(self, file_name, hierarchy_def, columns, teryt_data=None):
        """Initiates object.
        
        Arguments:
        file_name -- name of file with data that needs hierarchy inserting
        hierarchy_def -- object representing hierarchy in data
        columns -- description of columns
        teryt_data -- data from file with TERYT codes, can be used to generate id
        """
        csv_file = CsvFile(file_name, delim=';', quote='"')
        self.csv_data = CsvData(csv_file)
        print 'hierarchy_def = ', hierarchy_def
        print 'columns = ', columns
        # TODO:TODO TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: TODO: done here i have
        self.hierarchy_fields = hierarchy_def['columns']
        self.hierarchy_field_label = hierarchy_def['field_name_label']
        self.hierarchy_columns_labels = [self.csv_data.get_header()[i] for i in self.hierarchy_fields]
        self.type_label = hierarchy_def['field_type_label']
        self.modified_rows = []
        self.summable = hierarchy_def['summable']
        self.columns = columns[:]
        self.delete_order = sorted(self.hierarchy_fields + [self.name_column_nr], reverse=True)
        self.hierarchy_obj = HierarchyNode(0)
        self.use_teryt = False
        if teryt_data:
            self.use_teryt = True
            self.teryt_id_generator = TerytIdGenerator(teryt_data)
        self.bad_hierarchy_log = []
        
    def insert_hierarchy(self):
        """Process of inserting hierarchy is as follows:
        - for header: remove hierarchy fields and type column,
                      prepend field_type_label, field_name_label
        - for row: create rows representing hierarchy(if not created yet) and
                   remove hierarchy fields and type column, prepend type of row
                   (lowest_type) and value of name column
        Additionally id of rows can be inserted(and then id field is inserted
        in header).
        Firstly, changes header, then for each row gets its hierarchy, if
        it is new hierarchy, adds new rows representing this hierarchy,
        in the end clears hierarchy from the row.
        After that, if id were generated, fills summable columns
        in added hierarchy rows.
        """
        self.bad_hierarchy_log = []
        header = self.csv_data.get_header()
        for nr in self.delete_order:
            del header[nr]
        header.insert(0, self.type_label)
        header.insert(1, self.hierarchy_field_label)
        if self.add_id:
            header.insert(0, 'id')
        self.modified_rows = [header]
        
        row = self.csv_data.get_next_row(row_type='list')
        if row is None:
            print 'Only header in csv data. No data rows were changed'
            return
        
        row_len = len(header)
        old_hierarchy = []
        new_hierarchy = []
        i = 1
        while row is not None:
            i += 1
            if i == 10:
                pass
            try:
                new_hierarchy = self.get_hierarchy(row)
            except HierarchyError as e:
                log = ('row nr %d, ' % i) + e.log
                self.bad_hierarchy_log.append(log)
            else:
                if new_hierarchy != old_hierarchy:
                    new_hierarchy_rows = self.create_hierarchy_rows(new_hierarchy,
                                             row_len)
                    self.modified_rows.extend(new_hierarchy_rows)
                
                self.modified_rows.append(self.clean_row(row, new_hierarchy))
            
            old_hierarchy = new_hierarchy
            row = self.csv_data.get_next_row(row_type='list')
            
        if self.add_id:
            self.fill_summable_values()
                
    def all_rows_correct(self):
        """Returns True if no errors were found, otherwise False."""
        return self.bad_hierarchy_log == []
            
    def get_modified_rows(self):
        """Returns list of modified rows if no errors were found, otherwise
        empty list.
        """
        if self.all_rows_correct():
            return self.modified_rows
        else:
            return []
    
    def get_hierarchy_errors_log(self):
        """Returns string containing errors separated by new line."""
        return '\n'.join(self.bad_hierarchy_log)
    
    def clean_row(self, row, hierarchy):
        """Adds id of this row to hierarchy object.
        Removes hierarchy fields from the row, moves its type and name(fields
        described by name and type column in schema) to the beginning of it.
        Adds rows's id if add_id parameter was set to True on constructing
        this object.
        
        Arguments:
        row -- row to clean
        hierarchy -- hierarchy in the row
        """
        cleaned_row = row[:]
        node = self.get_hierarchy_node(hierarchy)
        next_id = node.get_new_child_id()
        row_node = HierarchyNode(next_id)
        node.add_child(row_node, next_id)
         
        hierarchy_field_name = cleaned_row[self.name_column_nr]
         
        for nr in self.delete_order:
            del cleaned_row[nr]
        
        cleaned_row.insert(0, self.lowest_type)
        cleaned_row.insert(1, hierarchy_field_name)
        if self.add_id:
            row_hierarchy = hierarchy + [next_id]
            full_id = self.get_full_id(row_hierarchy)
            cleaned_row.insert(0, full_id)
        
        return cleaned_row
    
    def get_hierarchy(self, row):
        """Returns list representing hierarchy in the row.
        
        Arguments:
        row -- data row
        """
        hierarchy = []
        for nr in self.hierarchy_fields:
            if row[nr] == '':
                break
            hierarchy.append(row[nr])
        return hierarchy
    
    def create_hierarchy_rows(self, new_hierarchy, row_len):
        """Returns rows list of hierarchy rows that should be put inside
        data to show new_hierarchy. If hierarchy rows have been added for
        new_hierarchy already, empty list will be returned. Hierarchy rows
        will be have not empty: id(if created), type, name and summable fields.
        
        Arguments:
        new_hierarchy -- list representing hierarchy in row in data 
        row_len -- length of that row, needed create correct hierarchy row
        """
        hierarchy_rows = []
        partial_hierarchy = []
        act_hierarchy_obj = self.hierarchy_obj
        i = 0
        for field in new_hierarchy:
            partial_hierarchy.append(field)
            child = act_hierarchy_obj.get_child(field)
            # if this row represents new hierarchy
            if child is None:
                if self.use_teryt:
                    new_id = self.teryt_id_generator.get_teryt_id(partial_hierarchy)
                    if new_id is None:
                        self.teryt_id_generator.add_teryt_unit(partial_hierarchy)
                        new_id = self.teryt_id_generator.get_teryt_id(partial_hierarchy)
                else:
                    new_id = act_hierarchy_obj.get_new_child_id()
                child = HierarchyNode(new_id)
                act_hierarchy_obj.add_child(child, field)
                new_row = ['' for _ in range(row_len)]
                if self.add_id:
                    new_row[0] = self.get_full_id(partial_hierarchy)
                    new_row[1] = self.hierarchy_columns_labels[i]
                    new_row[2] = field
                else:
                    new_row[0] = self.hierarchy_columns_labels[i]
                    new_row[1] = field
                    
                hierarchy_rows.append(new_row)
            
            act_hierarchy_obj = child
            i += 1
        return hierarchy_rows
    
    def get_hierarchy_node(self, hierarchy):
        """Returns HierarchyNode representing hierarchy. If there was not
        created node representing this hierarchy, None is returned.
        
        Arguments:
        hierarchy - hierarchy list
        """
        node = self.hierarchy_obj
        for field in hierarchy:
            if not node.has_child(field):
                return None
            node = node.get_child(field)
        return node
    
    def get_full_id(self, hierarchy):
        """Returns id for row with specified hierarchy. If there is no node
        representing such a hierarchy, HierarchyError is thrown.
        
        Arguments:
        hierarchy -- hierarchy list 
        """
        id_list = []
        node = self.hierarchy_obj
        for field in hierarchy:
            if not node.has_child(field):
                raise HierarchyError('Can not create full id for hierarchy %s' % hierarchy)
            node = node.get_child(field)
            id_list.append( str(node.get_id()) )
        
        return '-'.join(id_list)
    
    def fill_summable_values(self):
        """Fills summable columns in added hierarchy rows."""
        summable_cols = self.summable[:]
        for i in range(len(summable_cols)):
            for col_nr in self.delete_order:
                if col_nr < summable_cols[i]:
                    summable_cols[i] -= 1
            
            if self.add_id:
                summable_cols[i] += 3
            else:
                summable_cols[i] += 2                
        summable_cols_types = [self.fields[i]['type'] for i in self.summable]
        
        rows_dict = {}
        i = -1
        for row in self.modified_rows:
            i += 1
            # omitting header
            if i == 0:
                continue
            id = row[0]
            rows_dict[id] = row
            parent_id = self.get_parent_id(id)
            while parent_id:
                parent_row = rows_dict[parent_id]
                j = 0
                for col_nr in summable_cols:
                    value = row[col_nr]
                    type = summable_cols_types[j]
                    if parent_row[col_nr] == '':
                        parent_row[col_nr] = 0
                    if value == '':
                        continue
                    if type == 'int':
                        parent_row[col_nr] += int(value)
                    elif type == 'float' and value != '':
                        commas_in_field = value.count(',')
                        dots_in_field = value.count('.')
                        if commas_in_field > 0:
                            if dots_in_field > 0:
                                parent_row[col_nr] += float( value.replace(',', '', commas_in_field) )
                        else:
                            value = value.replace(',', '', commas_in_field - 1)
                            parent_row[col_nr] += float( value.replace(',', '.') )

                    j += 1
                parent_id = self.get_parent_id(parent_id)
                
    
    def get_parent_id(self, id):
        """Returns id of parent of row with given id. If this row has
        no parent, None is returned.
        
        Parameters:
        id -- id of child
        """
        if id.count('-') == 0:
            return None
        return id.rsplit('-', 1)[0]
            

class HierarchyNode:
    
    """Helper class used to remember ids of hierarchy elements."""
    
    def __init__(self, id):
        """Initiates object.
        
        Arguments:
        id -- id of this node(integer)
        """
        self.id = id
        self.children = {}
        self.last_child_id = 0
    
    def add_child(self, node, key):
        """Adds a child node to the list of children of this node. Inserts
        it under specified key.
        
        Arguments:
        node -- child node
        key -- id connected with child node
        """
        self.children[key] = node
        self.last_child_id += 1
        
    def get_child(self, key):
        """Returns child node with given id. If there is no node with this
        id, None is returned.
        
        Arguments:
        key -- id connected with child node
        """
        if self.has_child(key):
            return self.children[key]
        return None
        
    def has_child(self, key):
        """Returns True, if there is node connected with value key,
        otherwise False.
        
        Arguments:
        key -- id connected with child node
        """
        return key in self.children
        
    def get_new_child_id(self):
        """Returns id of next child."""
        return self.last_child_id + 1
        
    def get_id(self):
        """Returns id of this node."""
        return self.id

        
class HierarchyError(Exception):
    
    """Class representing errors which happen during processing
    hierarchy in data.
    """
    
    def __init__(self, log):
        """Initiates object.
        
        Arguments:
        log -- error log
        """
        self.log = log
        
    def __str__(self):
        """Returns string representation of error."""
        return repr(self.log)
    

class TerytIdGenerator:
    
    """Class creating TERYT codes."""
    
    def __init__(self, data):
        """Initiates this object using data from file with TERYT codes.
        
        Arguments:
        data -- csv data of file with TERYT codes
        """
        self.codes = {}
        self.errors = []
        row = data.get_next_row()
        while row:
            type = row['Nazwa typu jednostki']
            name = unicode(row['Nazwa']).lower()
            full_code = row['TERYT']
            woj_code = full_code[:2]
            pow_code = full_code[2:4]
            gm_code = full_code[4:6]
            
            if self.is_type_ignored(type):
                row = data.get_next_row()
                continue
            
            if self.is_wojewodztwo(type):
                self.codes[name] = {'id': woj_code, 'name': name, 'powiats': {}}
                last_woj = self.codes[name]
                last_woj_code = woj_code
            elif self.is_powiat(type):
                new_pow_dict = {'id': pow_code, 'name': name, 'gminas': {}}
                if woj_code == last_woj_code:
                    last_woj['powiats'][name] = new_pow_dict
                else:
                    woj = self.get_teryt_object(woj_code)
                    if woj is None:
                        self.errors.append('Error: unknown województwo, code=%s' % woj_code)
                        print 'Error: unknown województwo, code=', woj_code
                        row = data.get_next_row()
                        continue
                    woj['powiats'][name] = new_pow_dict
                last_pow = new_pow_dict
                last_pow_code = pow_code
            elif self.is_gmina(type):
                new_gm_dict = {'id': gm_code, 'name': name}
                if woj_code == last_woj_code and pow_code == last_pow_code:
                    # handle situation when there is "AAA" - gmina miejska and "AAA" - gmina wiejska
                    # it becomes: "AAA - miasto" - gmina miejska and "AAA" - gmina wiejska 
                    if name in last_pow['gminas']:
                        miasto_gm_name = name + ' - miasto'
                        last_pow['gminas'][miasto_gm_name] = last_pow['gminas'][name]
                        last_pow['gminas'][miasto_gm_name]['name'] = miasto_gm_name
                        last_pow['gminas'][name] = new_gm_dict
                    else:
                        last_pow['gminas'][name] = new_gm_dict
                else:
                    pow = self.get_teryt_object(woj_code, pow_code)
                    if pow is None:
                        self.errors.append('Error: unknown powiat, code=%s' % pow_code)
                        print 'Error: unknown powiat, code=', pow_code
                        row = data.get_next_row()
                        continue
                    # handle situation when there is "AAA" - gmina miejska and "AAA" - gmina wiejska
                    # it becomes: "AAA - miasto" - gmina miejska and "AAA" - gmina wiejska 
                    if name in pow['gminas']:
                        miasto_gm_name = name + ' - miasto'
                        pow['gminas'][miasto_gm_name] = pow['gminas'][name]
                        pow['gminas'][miasto_gm_name]['name'] = miasto_gm_name
                        pow['gminas'][name] = new_gm_dict
                    else:
                        pow['gminas'][name] = new_gm_dict
            else:
                self.errors.append('Error: unknown unit type: %s' % type)
                print 'Error: unknown unit type:', type
        
            row = data.get_next_row()
    
    def is_wojewodztwo(self, type):
        return type == 'województwo'
    
    def is_powiat(self, type):
        return type in ['powiat', 'miasto na prawach powiatu',
                        'miasto stołeczne, na prawach powiatu']
    
    def is_gmina(self, type):
        return type in ['gmina miejska', 'gmina wiejska', 'gmina miejsko-wiejska',
                         'dzielnica', 'delegatura',
                         'gmina miejska, miasto stołeczne']
    
    def is_type_ignored(self, type):
        return type in ['miasto', 'obszar wiejski']
        
    def get_teryt_object(self, woj_code, pow_code=None, gm_code=None):
        """Returns dict representing teritorial unit which code is
        woj_code[ + pow_code[ + gm_code]]. If such a unit cannot be found,
        None is returned.
        
        Arguments:
        woj_code -- code of unit's wojewodztwo
        pow_code -- code of unit's powiat
        gm_code -- code of unit's gmina
        """
        woj_dict = None
        for woj in self.codes:
            if woj['id'] == woj_code:
                woj_dict = woj
                last_dict = woj_dict
                break
        
        if woj_dict is None:
            return None
        
        if pow_code:
            pow_dict = None
            for pow in woj_dict['powiats']:
                if pow['id'] == pow_code:
                    pow_dict = pow
                    last_dict = pow_dict
                    break
                
            if pow_dict is None:
                return None
        
        if gm_code:
            for gm in pow_dict:
                if gm['id'] == gm_code:
                    gm_dict = gm
                    last_dict = gm_dict
                    break
            if gm_dict is None:
                return None
        
        return last_dict
    
    def get_teryt_name(self, code):
        """Returns name of teritorial unit which code is
        woj_code[ + pow_code[ + gm_code]]. If such a unit cannot be found,
        None is returned.
        
        Arguments:
        code -- unit's TERYT code
        """
        woj_code = code[:2]
        if len(code) > 3:
            pow_code = code[2:4]
            if len(code) > 5:
                gm_code = code[4:6]
        teryt_object_dict = self.get_teryt_object(woj_code, pow_code, gm_code)
        try:
            return teryt_object_dict['name']
        except TypeError:
            return None
    
    def get_teryt_id(self, hierarchy):
        """Returns teryt id of teritorial unit represented by hierarchy.
        Letters in hierarchy strings are lowercased and changed so that
        they could be in the same form as they are expected.
        If such a unit can not be found, returns None.
        
        Arguments:
        hierarchy -- list containing name of unit's wojewodztwo,
                     powiat(optionally) and gmina(optionally)
        """
        modified_hierarchy = [unicode(name).lower() for name in hierarchy]
        woj_name = modified_hierarchy[0]
        pow_name, gm_name = None, None
        if len(modified_hierarchy) > 1:
            pow_name = self.correct_powiat_name(modified_hierarchy[1])
        if len(modified_hierarchy) > 2:
            gm_name = self.correct_gmina_name(modified_hierarchy[2])
        
        tmp_obj = self.codes
        try:
            tmp_obj = tmp_obj[woj_name]
        except KeyError:
            return None
        
        if pow_name:
            try:
                tmp_obj = tmp_obj['powiats'][pow_name]
            except KeyError:
                return None
        
        if gm_name:
            try:
                tmp_obj = tmp_obj['gminas'][gm_name]
            except KeyError:
                return None
        
        return tmp_obj['id']
    
    def add_teryt_unit(self, hierarchy):
        """ Add new teritorial unit. If it exists in actual hierarchy,
        nothing will happen. Otherwise, this unit will be placed in hierarchy.
        
        Arguments:
        hierarchy -- hierarchy of new teritorial unit
        """
        modified_hierarchy = [unicode(name).lower() for name in hierarchy]
        if len(modified_hierarchy) > 1:
            modified_hierarchy[1] = self.correct_powiat_name(modified_hierarchy[1])
        if len(modified_hierarchy) > 2:
            modified_hierarchy[2] = self.correct_gmina_name(modified_hierarchy[2])
            
        if self.get_teryt_id(modified_hierarchy):
            return
        
        tmp_obj = self.codes
        i = 0
        for field in modified_hierarchy:
            if field in tmp_obj:
                if i == 0:
                    tmp_obj = tmp_obj[field]['powiats']
                else:
                    tmp_obj = tmp_obj[field]['gminas']
            else:
                if i == 0:
                    id = self.find_highest_id(tmp_obj) + 1
                    tmp_obj[field] = {'id': str(id), 'name': field, 'powiats': {}}
                elif i == 1:
                    id = self.find_highest_id(tmp_obj['powiats']) + 1
                    tmp_obj[field] = {'id': str(id), 'name': field, 'gminas': {}}
                elif i == 2:
                    id = self.find_highest_id(tmp_obj['gminas']) + 1
                    tmp_obj[field] = {'id': str(id), 'name': field}
            i += 1
    
    def find_highest_id(self, objects):
        """Returns highest id of objects in list.
        
        Argument:
        objects -- list of objects that have id value
        """
        highest_id = 0
        for obj in objects:
            id = int(objects[obj]['id'])
            if id > highest_id:
                highest_id = id
        
        return highest_id
    
    def correct_powiat_name(self, full_name):
        """Returns only powiat's name, without 'powiat' part, 'm. st.'
        
        Arguments:
        full_name -- full name of powiat
        """
        
        short_name = full_name
        if 'powiat' in short_name:
            short_name = short_name.lstrip('powiat')
            if short_name[0] == ' ':
                short_name = short_name[1:]
        
        if short_name.startswith('m.'):
            short_name = short_name.lstrip('m.')
            if short_name[0] == ' ':
                short_name = short_name[1:]
        
        if short_name.startswith('st.'):
            short_name = short_name.lstrip('st.')
            if short_name[0] == ' ':
                short_name = short_name[1:]
        
        return short_name
    
    def correct_gmina_name(self, full_name):
        """Returns only gmina's name, without 'm.' part.
        
        Arguments:
        full_name -- full name of gmina
        """
        
        short_name = full_name
        if 'gmina' in short_name:
            short_name = short_name.lstrip('gmina')
            if short_name[0] == ' ':
                short_name = short_name[1:]
                
        if short_name.startswith('m.'):
            short_name = short_name.lstrip('m.')
            if short_name[0] == ' ':
                short_name = short_name[1:]
        
        if short_name.startswith('st.'):
            short_name = short_name.lstrip('st.')
            if short_name[0] == ' ':
                short_name = short_name[1:]
        
        return short_name
