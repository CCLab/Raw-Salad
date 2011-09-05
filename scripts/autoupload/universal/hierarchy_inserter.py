'''
Created on 25-08-2011
'''

class HierarchyInserter:
    
    """Inserts hierarchy from the given collection. Uses hierarchy described in
    object of the following form:
    {
        "columns": [list of columns creating hierarchy],
        "field_name": name of column that will be inserted to substitute
                      hierarchy columns,
        "type_column" number of column which value represents name of data row
                      and will be moved to new field(its name is field_name)
    }
    Data passed to HierarchyInserter should be correct, otherwise created
    data will contain bugs.
    """
    
    def __init__(self, csv_data, hierarchy_def, add_id=False):
        """Initiates object.
        
        Arguments:
        csv_data -- data that needs hierarchy inserting
        hierarchy_def -- object representing hierarchy in data
        add_id -- if new column with id should be prepended for each row
        """
        self.csv_data = csv_data
        self.hierarchy_fields = hierarchy_def['columns']
        self.hierarchy_field_label = hierarchy_def['field_name']
        self.modified_rows = []
        self.delete_order = sorted(self.hierarchy_fields, reverse=True)
        type_column_nr = hierarchy_def['type_column']
        for col_nr in self.delete_order:
            if col_nr < type_column_nr:
                type_column_nr -= 1
        self.type_column_nr = type_column_nr
        self.hierarchy_obj = HierarchyNode(0)
        self.add_id = add_id
        self.bad_hierarchy_log = []
        
    def insert_hierarchy(self):
        """Process of inserting hierarchy is as follows:
        - for header: remove hierarchy fields and type column, prepend field_name
        - for row: create rows representing hierarchy(if not created yet) and
                   remove hierarchy fields and type column, prepend value of type
                   column
        Additionally id of rows can be inserted(and then id field is inserted
        in header).
        Firstly, changes header, then for each row gets its hierarchy, if
        it is new hierarchy, adds new rows representing this hierarchy,
        in the end clears hierarchy from the row. 
        """
        self.bad_hierarchy_log = []
        header = self.csv_data.get_header()
        for nr in self.delete_order:
            del header[nr]
        del header[self.type_column_nr]
        header.insert(0, self.hierarchy_field_label)
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
        Removes hierarchy fields from the row, moves name representing row
        (field described by type column in schema) to the beginning of the row.
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
         
        hierarchy_field_name = cleaned_row[self.type_column_nr]
         
        for nr in self.delete_order:
            del cleaned_row[nr]
        del cleaned_row[self.type_column_nr]
        
        cleaned_row.insert(0, hierarchy_field_name)
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
        will be have only one field not empty: name(plus id if created).
        
        Arguments:
        new_hierarchy -- list representing hierarchy in row in data 
        row_len -- length of that row, needed create correct hierarchy row
        """
        hierarchy_rows = []
        partial_hierarchy = []
        act_hierarchy_obj = self.hierarchy_obj
        for field in new_hierarchy:
            partial_hierarchy.append(field)
            child = act_hierarchy_obj.get_child(field)
            # if this row represents new hierarchy
            if child is None:
                new_id = act_hierarchy_obj.get_new_child_id()
                child = HierarchyNode(new_id)
                act_hierarchy_obj.add_child(child, field)
                new_row = ['' for _ in range(row_len)]
                if self.add_id:
                    new_row[0] = self.get_full_id(partial_hierarchy)
                    new_row[1] = field
                else:
                    new_row[0] = field
                    
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
    

class HierarchyNode:
    
    """Helper class used to remember ids of hierarchy elements."""
    
    def __init__(self, id):
        """Initiates object.
        
        Arguments:
        id -- id of this node
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