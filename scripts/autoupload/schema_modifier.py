# -*- coding: utf-8 -*-

'''
Created on 30-08-2011
'''

import simplejson as json
from django.template.defaultfilters import slugify
from string import ascii_lowercase


def remove_diacritics(name):
    """Returns name without diacritics and inserted latin letters.
    
    Arguments:
    name -- word to have diacritics removed
    """
    return name.replace(u'ą', 'a').replace(u'ć', 'c').replace(u'ę', 'e').replace(u'ł', 'l')\
               .replace(u'ń', 'n').replace(u'ó', 'o').replace(u'ś', 's').replace(u'ź', 'z')\
               .replace(u'ż', 'z').replace(u'Ą', 'A').replace(u'Ć', 'C').replace(u'Ę', 'E')\
               .replace(u'Ł', 'L').replace(u'Ń', 'N').replace(u'Ó', 'O').replace(u'Ś', 'S')\
               .replace(u'Ź', 'Z').replace(u'Ż', 'Z')

    
"""
Description of input and output schemas used by SchemaModifier
is in the end of this file.
"""

class SchemaModifier:
    
    """Class used to create schema files that will be used to upload data
    to db. Bases on schema files describing data fields and hierarchy.
    """
    def __init__(self, json_schema, json_hierarchy):
        """Initiates object.
        
        Arguments:
        json_schema -- dict describing fields of collection
        json_hierarchy -- dict describing hierarchy in collection
        """
        self.schema = json_schema
        self.hierarchy = json_hierarchy
        self.out_schema = None
        self.out_coll = None
        
    def modify_schema(self, add_id=False):
        """Creates schema describing names of fields and their types.
        Modified schema will not contain description of hierarchy columns
        and type column. One hierarchy column will be inserted and if add_id
        is True, then also id column will be described in schema.
        
        Arguments:
        add_id -- specifies if id column is generated and therefore should
                  be described
        """
        fields = self.schema["fields"][:]
        self.out_schema = {}
        alias = self.out_schema["alias"] = {}
        type = self.out_schema["type"] = {}
        
        self.remove_hierarchy_fields(fields)
        
        field_nr = 0
        if add_id:
            alias[str(field_nr)] = "idef"
            type["idef"] = "string"
            field_nr += 1
        alias[str(field_nr)] = "type"
        type["type"] = "string"
        field_nr += 1
        
        for field in fields:
            #name = slugify(field["label"])
            name = slugify(remove_diacritics(field["label"]))
            #base = slugify(field["label"])
            base = slugify(remove_diacritics(field["label"]))
            i = 1
            while name in type:
                i += 1
                name = base + str(i) 
            alias[str(field_nr)] = name
            type[name] = field["type"]
            field_nr += 1
        
    def modify_coll_descr(self, params_dict, add_id=False):
        """Creates schema describing collection.
        
        Arguments:
        params_dict -- dict with parameters needed to create description of
                       collection
        add_id -- specifies if id column is generated and therefore should
                  be described
        """
        explorable = ''
        if self.out_schema['alias']['0'] == 'idef':
            explorable = self.out_schema['alias']['1']
        else:
            explorable = self.out_schema['alias']['0']
        perspective = self.schema['dataset_name'] + ' ' + self.schema['perspective_name'] +\
                      ' ' + self.schema['issue']
        max_level = len(self.hierarchy['columns'])
        self.out_coll = {
            "name": slugify(remove_diacritics(perspective)),
            "perspective": perspective,
            "ns": params_dict['ns'],
            "dataset": params_dict['dataset'],
            "idef": params_dict['perspective'],
            "issue": self.schema['issue'],
            "explorable": explorable,
            "max_level": ascii_lowercase[max_level],
            "batchsize": None,
            "columns": self.prepare_columns_descr(add_id, explorable),
            "aux": {"leaf": 1, "parent": 1, "idef": 1},
            "query": {},
            "sort": {
                "0": {"idef_sort": 1},
                "1": {"parent_sort": 1},
                "2": {"level": 1}
            }
        }
    
    def save(self, schema_name, coll_descr_name):
        """Saves schemas in files and closes those files.
        
        Arguments:
        schema_name -- name of a file that will have modified schema describing
                       names of fields and their types
        coll_descr_name -- name of a file that will have collection description
        """
        json_schema = json.dumps(self.out_schema, encoding='utf-8', sort_keys=True, indent=4)
        json_coll_descr = json.dumps(self.out_coll, encoding='utf-8', sort_keys=True, indent=4)
        
        schema_file = open(schema_name, 'wb')
        schema_file.write(json_schema)
        schema_file.close()
        
        coll_descr_file = open(coll_descr_name, 'wb')
        coll_descr_file.write(json_coll_descr)
        coll_descr_file.close()
    
    def get_new_schema(self):
        """Returns modified schema describing fields."""
        return self.out_schema
    
    def get_coll_descr(self):
        """Returns modified schema describing collection."""
        return self.out_coll
        
    def remove_hierarchy_fields(self, fields):
        """Removes hierarchy fields from list of fields.
        
        Arguments:
        fields -- list of fields before inserting hierarchy
        """
        to_remove = sorted(self.hierarchy['columns'] + [self.hierarchy['type_column']], reverse=True)
        for nr in to_remove:
            del fields[nr]
    
    def prepare_columns_descr(self, add_id, explorable_name):
        """Returns list describing columns in collection.
        
        Arguments:
        add_id -- specifies if id was generated
        explorable_name -- name of field that represents explorable column
                           (hierarchy column)
        """
        columns = []
        # those columns should be generated for all collections
        columns.append(self.create_column("idef_sort", "ID", "string", basic=False))
        columns.append(self.create_column("parent_sort", "Rodzic", "string", basic=False))
        columns.append(self.create_column("level", "Poziom", "string", basic=False))
        
        fields = self.schema["fields"][:]
        self.remove_hierarchy_fields(fields)
        hierarchy_label = self.hierarchy['field_name']
        columns.append(self.create_column("type", hierarchy_label, "string", basic=True))
        
        previous_names = []
        for field in fields:
            key = slugify(remove_diacritics(field["label"]))
            key_base = slugify(remove_diacritics(field["label"]))
            i = 1
            while key in previous_names:
                i += 1
                key = key_base + str(i)
            previous_names.append(key)
            label = field['label']
            type = field['type']
            basic = 'basic' in field and field['basic']
            column = self.create_column(key, label, type, basic)
            columns.append(column)
        
        return columns
    
    def create_column(self, key, label, type, basic=True):
        """Creates object describing column, adds processable key = True.
        
        Arguments:
        key -- key value(internal representation of column)
        label -- label(name of column in header)
        type -- type of value("string", "int" or "float")
        basic -- bool value
        """
        column = {
            "key": key,
            "label": label,
            "type": type,
            "processable": True
        }
        if type in ["int", "float"]:
            column["checkable"] = True
        if basic:
            column["basic"] = True
        return column


"""
Expected form of schema describing data fields:
    {
        "fields": [
            {
                "name":
                "type":
                "label":
                (optional)"basic":
            }
        ]
    }
    Expected form of hierarchy:
    {
        "rows": [list of hierarchy columns]
        "type_column": number of column which value represents name of data row
                       and will be moved to new field(its name is field_name)
        "field_name": name of column that will be inserted to substitute
                      hierarchy columns
    }
    
    SchemaModifier creates modified schema and collection description.
    Form of modified schema:
    {
        "alias": {
            "0": field_0_name,
            ...
        },
        "type": {
            "field_0_name": field_0_type("string", "int" or "float"),
            ...
        }
    }
    Form of collection description:
    {
        "aux":
        "batchsize":
        "columns": [
            {
                "key": string,
                "label": string,
                "type": "string", "int" or "float",
                "processable": bool,
                (optional)"checkable": bool
            },
            ...
        ],
        "dataset": int,
        "explorable": string,
        "idef": int,
        "issue": string,
        "max_level": string,
        "name": string,
        "ns": string,
        "perspective": string,
        "query" dict,
        "sort": dict
    }
"""