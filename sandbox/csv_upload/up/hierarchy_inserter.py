# -*- coding: utf-8 -*-

'''
Created on 25-08-2011
'''

from data_wrapper import CsvFile, CsvData
import string

DEBUG_HI = False

class HierarchyInserter:
    
    """Inserts hierarchy from the given collection. Uses hierarchy described in
    object of the following form:
    {
        "columns": [list of columns creating hierarchy],
        "field_type_label": name of column(that will be inserted), representing
                            type of row(position in hierarchy),
        "field_name_label": name of column(that will be inserted), representing
                            name of row,
        "field_parent_label": name of column(that will be inserted), representing
                            id of parent,
        "field_level_label": name of column(that will be inserted), representing
                            level of row
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
        print '************************************************'
        print 'hierarchy_def = ', hierarchy_def
        print 'columns = ', columns
        self.hierarchy_fields = [column_descr['index'] for column_descr in hierarchy_def['columns']]
        self.name_label = hierarchy_def['field_name_label']
        print 'h_c_l = ', self.csv_data.get_header()
        print 'h_f = ', self.hierarchy_fields
        self.hierarchy_columns_labels = [self.csv_data.get_header()[i] for i in self.hierarchy_fields]
        print 'self.hierarchy_columns_labels', self.hierarchy_columns_labels

        self.changeable_types = [column_descr['change_type'] for column_descr in hierarchy_def['columns']]
        self.type_label = hierarchy_def['field_type_label']
        self.parent_label = hierarchy_def['field_parent_label']
        self.level_label = hierarchy_def['field_level_label']
        self.id_label = 'ID' #  it should not be parameterized
        self.additional_fields = 5
        self.modified_rows = []
        self.summable = hierarchy_def['summable']
        self.columns = columns[:]
        self.delete_order = []
        for field_nr in self.hierarchy_fields:
            self.delete_order.append(field_nr)
            self.delete_order.append(field_nr + 1)

        self.delete_order = sorted(self.delete_order, reverse=True)
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

        header.insert(0, self.id_label)
        header.insert(1, self.type_label)
        header.insert(2, self.name_label)
        header.insert(3, self.parent_label)
        header.insert(4, self.level_label)

        self.modified_rows = [header]
        
        row = self.csv_data.get_next_row(row_type='list')
        if row is None:
            print 'Only header in csv data. No data rows were changed'
            return
        
        print '///////////////////////////////////////////////////////////////'
        row_len = len(header)
        old_hierarchy = []
        new_hierarchy = []
        i = 0
        while row is not None:
            i += 1
            try:
                new_hierarchy = self.get_hierarchy(row)
                hierarchy_values = self.get_hierarchy_values(row)
            except HierarchyError as e:
                if DEBUG_HI:
                    print "!!!!!!!!!!!!!!!!!!!!!! Error"
                log = ('row nr %d, ' % i) + e.log
                self.bad_hierarchy_log.append(log)
            else:
                new_hierarchy = new_hierarchy[:-1]
                if DEBUG_HI:
                    print 'For row: ', row
                    print 'new hierarchy is:', new_hierarchy
                    print 'hierarchy_values:', hierarchy_values
                if new_hierarchy != old_hierarchy:
                    new_hierarchy_rows = self.create_hierarchy_rows(new_hierarchy,
                                             hierarchy_values, row_len)
                    if DEBUG_HI:
                        print 'new_hierarchy_rows:', new_hierarchy_rows
                    self.modified_rows.extend(new_hierarchy_rows)
                
                cleaned_row = self.clean_row(row, new_hierarchy, hierarchy_values)
                if DEBUG_HI:
                    print 'cleaned_row:', cleaned_row
                self.modified_rows.append(cleaned_row)
            
            old_hierarchy = new_hierarchy
            row = self.csv_data.get_next_row(row_type='list')
            
        self.fill_summable_values()
        self.modify_columns_description()
                
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
    
    def clean_row(self, row, hierarchy, hierarchy_values):
        """Adds id of this row to hierarchy object.
        Removes hierarchy fields from the row, moves its type and name(fields
        described by name and type column in schema) to the beginning of it.
        Adds rows's id if add_id parameter was set to True on constructing
        this object.
        
        Arguments:
        row -- row to clean
        hierarchy -- hierarchy in the row
        hierarchy_values -- list of values connected with hierarchy fields
        """
        cleaned_row = row[:]
        node = self.get_hierarchy_node(hierarchy)
         
        row_type = self.hierarchy_columns_labels[-1]
        if hierarchy_values[-1] != '':
            row_type += ' ' + hierarchy_values[-1]
            next_id = self.clean_row_nr(hierarchy_values[-1])
        else:
            next_id = node.get_new_child_id()

        row_node = HierarchyNode(next_id)
        node.add_child(row_node, next_id)
        row_name = cleaned_row[ self.hierarchy_fields[-1] ]
        hierarchy_val = hierarchy_values[-1]
         
        for nr in self.delete_order:
            del cleaned_row[nr]
        
        row_hierarchy = hierarchy + [next_id]
        full_id = self.get_full_id(row_hierarchy)
        if DEBUG_HI:
            print '***********************'
            print 'row_hierarchy=', row_hierarchy
            print 'full_id=', full_id
            print '***********************'
        level = string.lowercase[ full_id.count('-') ]
        if level == 'a':
            parent_id = None
        else:
            parent_id = full_id.rsplit('-', 1)[0]

        cleaned_row.insert(0, full_id)
        cleaned_row.insert(1, row_type)
        cleaned_row.insert(2, row_name)
        cleaned_row.insert(3, parent_id)
        cleaned_row.insert(4, level)
        
        return cleaned_row
    
    def get_hierarchy(self, row):
        """Returns list representing hierarchy in the row.
        
        Arguments:
        row -- data row
        """
        hierarchy = []
        for nr in self.hierarchy_fields:
            hierarchy.append(row[nr])
        return hierarchy

    def get_hierarchy_values(self, row):
        """Returns list representing values assigned to hierarchy levels in the row.
        
        Arguments:
        row -- data row
        """
        hierarchy_values = []
        for nr in self.hierarchy_fields:
            hierarchy_values.append(row[nr + 1])
        return hierarchy_values    
    
    def create_hierarchy_rows(self, new_hierarchy, hierarchy_values, row_len):
        """Returns rows list of hierarchy rows that should be put inside
        data to show new_hierarchy. If hierarchy rows have been added for
        new_hierarchy already, empty list will be returned. Hierarchy rows
        will be have not empty: id(if created), type, name and summable fields.
        
        Arguments:
        new_hierarchy -- list representing hierarchy in row in data 
        hierarchy_values -- list representing values assigned to specified
                            elements of hierarchy(like funcion '3')
        row_len -- length of that row, needed create correct hierarchy row
        """
        hierarchy_rows = []
        partial_hierarchy = []
        act_hierarchy_obj = self.hierarchy_obj
        for i, field in enumerate(new_hierarchy):
            if field == '':
                continue
            partial_hierarchy.append(field)
            child = act_hierarchy_obj.get_child(field)
            # if this row represents new hierarchy
            if child is None:
                if hierarchy_values[i] == '':
                    new_id = act_hierarchy_obj.get_new_child_id()
                else:
                    new_id = self.clean_row_nr(hierarchy_values[i])
                if DEBUG_HI:
                    print '---------------'
                    print 'new_id=', new_id
                    print '---------------'
                child = HierarchyNode(new_id)
                act_hierarchy_obj.add_child(child, field)
                new_row = ['' for _ in range(row_len)]
                new_row[0] = self.get_full_id(partial_hierarchy)
                new_row[1] = self.hierarchy_columns_labels[i]
                if hierarchy_values[i] != '':
                    new_row[1] += ' ' + hierarchy_values[i]
                new_row[2] = field

                level = string.lowercase[ new_row[0].count('-') ]
                if level == 'a':
                    parent_id = None
                else:
                    parent_id = new_row[0].rsplit('-', 1)[0]
                new_row[3] = parent_id
                new_row[4] = level

                hierarchy_rows.append(new_row)
            
            act_hierarchy_obj = child

        return hierarchy_rows
    
    def get_hierarchy_node(self, hierarchy):
        """Returns HierarchyNode representing hierarchy. If there was not
        created node representing this hierarchy, None is returned.
        
        Arguments:
        hierarchy - hierarchy list
        """
        node = self.hierarchy_obj
        for field in hierarchy:
            if field == '':
                continue
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
            if field == '':
                continue
            if not node.has_child(field):
                raise HierarchyError('Cannot create full id for hierarchy %s' % hierarchy)
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
            summable_cols[i] += self.additional_fields

        summable_cols_types = [self.columns[i]['type'] for i in self.summable]
        
        rows_dict = {}
        i = -1
        for row in self.modified_rows:
            i += 1
            if DEBUG_HI:
                print 'i:', i, 'row:', row
                print 'summable_cols:', summable_cols
            # omitting header
            if i == 0:
                continue
            id = row[0]
            rows_dict[id] = row
            parent_id = self.get_parent_id(id)
            while parent_id:
                parent_row = rows_dict[parent_id]
                j = 0
                if DEBUG_HI:
                    print 'j', j
                for col_nr in summable_cols:
                    value = row[col_nr]
                    type = summable_cols_types[j]
                    if parent_row[col_nr] == '':
                        parent_row[col_nr] = 0
                    if value == '':
                        continue
                    if type == 'number':
                        try:
                            value = int(value)
                        except:
                            value = float(value)
                        if parent_row[col_nr] == '':
                            parent_row[col_nr] = value
                        else:
                            if DEBUG_HI:
                                print 'parent_row[col_nr]', parent_row[col_nr], '|| value =', value
                            parent_row[col_nr] += value
                    j += 1
                parent_id = self.get_parent_id(parent_id)

    def modify_columns_description(self):
        """Modifies columns description that was passed during object creation, so that
        it reflects new form of data.
        """
        for index in self.delete_order:
            del self.columns[index]
        
        id_column_description = self.create_column_description(unicode(self.id_label), u'idef_sort', False)
        type_column_description = self.create_column_description(unicode(self.type_label), u'type', True)
        name_column_description = self.create_column_description(unicode(self.name_label), u'name', True)
        parent_column_description = self.create_column_description(unicode(self.parent_label), u'parent_sort', False)
        level_column_description = self.create_column_description(unicode(self.level_label), u'level', False)
        
        self.columns.insert(0, id_column_description)
        self.columns.insert(1, type_column_description)
        self.columns.insert(2, name_column_description)
        self.columns.insert(3, parent_column_description)
        self.columns.insert(4, level_column_description)
    
    def create_column_description(self, label, key, basic):
        """Creates standard column description that will be inserted to meta data description
        because of hierarchy transformation.
        
        Arguments:
        label -- label of new column
        key -- key of new column
        basic -- is column basic
        """
        return {
           u'format': u'@',
           u'label': label,
           u'obligatory': True,
           u'processable': True,
           u'key': key,
           u'basic': basic,
           u'checkable': False,
           u'type': u'string'
        }

    def get_columns_description(self):
        """Returns description of columns in data. Columns description changes
        after inserting hierarchy in rows.
        """
        return self.columns
    
    def get_parent_id(self, id):
        """Returns id of parent of row with given id. If this row has
        no parent, None is returned.
        
        Parameters:
        id -- id of child
        """
        if id.count('-') == 0:
            return None
        return id.rsplit('-', 1)[0]

    def clean_row_nr(self, type_nr):
        """Returns last part of type_nr with special characters removed
        ('/', '-', '.')

        Parameters:
        type_nr -- number of type in hierarchy on specified level
        """
        new_nr = type_nr
        new_nr = new_nr.split('/')[-1]
        new_nr = new_nr.split('-')[-1]
        new_nr = new_nr.split('.')[-1]

        return new_nr


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


class HierarchyValidator:

    """Class validating hierarchy, makes sure that irregular hierarchy with 
    holes inside will not cause bad id generation, if it happens, then validator
    will alert about such situtation
    """

    def __init__(self):
        """ Inititates object, remembered hierarchy is empty."""
        self.hierarchy_dict = {}

    def add_hierarchy(self, hierarchy, full_id):
        """Tries to add id to collection of previous ids. If such an id was
        generated earlier and holes do not match, then we have a conflict.

        Arguments:
        hierarchy -- contatins hierarchy of actual object
        full_id -- id of that object
        """
        hierarchy_holes = self.find_holes(hierarchy)
        if full_id in self.hierarchy_dict:
            return self.check_hierarchy(self.hierarchy_dict[full_id], hierarchy_holes)
        else:
            self.hierarchy_dict[full_id] = hierarchy_holes
            return True

    def check_hierarchy(self, first_hierarchy, second_hierarchy):
        """Checks if holes in both hierarchies do match

        Arguments:
        first_hierarchy, second_hierarchy -- hierarchies to check
        """
        return True

    def find_holes(self, hierarchy):
        """Returns list with indexes of empty hierarchy values.

        Arguments:
        hierarchy -- hierarchy to be checked
        """

        return []
