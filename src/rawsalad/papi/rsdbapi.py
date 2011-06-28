# -*- coding: utf-8 -*-
"""
project: Raw Salad
function: classes representing the API to data and meta-data
requirements: mongod, conf file (see conf_filename)
"""

from ConfigParser import ConfigParser
import pymongo

meta_src= "md_budg_scheme"
nav_schema= "ms_nav"
conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/media/rawsdata.conf"

error_code= {
    '10': 'ERROR: No such data!',
    '20': 'ERROR: No such meta-data!',
    '30': 'ERROR: Wrong request!',
    '31': 'ERROR: Scope +TO+ is applicable to the same level!',
    '32': 'ERROR: Wrong sequence in the scope +TO+!',
    '33': 'ERROR: Scope +TO+ should include only 2 elements!',
    '34': 'ERROR: Syntax error in scope definition!'
    }

#-----------------------------
class DBconnect(object):
    def __init__(self, db_type):
        if db_type == 'mongodb':
            self.fill_connection(db_type)
            connect= pymongo.Connection(self.host, self.port)
            dbase= connect[self.database]
            dbase.authenticate(self.username, self.password)
        elif db_type == 'postgresql':
            dbase= None # not yet realized

        self.dbconnect= dbase


    def fill_connection(self, db_type):
        cfg= ConfigParser({ 'basedir': conf_filename })
        cfg.read(conf_filename)

        try: # to read from conf file first
            self.host= cfg.get(db_type,'host')
            self.port= cfg.getint(db_type,'port')
            self.database= cfg.get(db_type,'database')
            self.username= cfg.get(db_type,'username')            
            pssw= cfg.get(db_type,'password')
            if pssw is not None:
                self.password= pssw
            else:
                self.password= '' # must be instance of basestring
        except: # it's unavailable, filling defaults then
            self.host= 'localhost'
            self.port= 27017
            self.database= 'rawsdoc00'
            self.username= 'readonly'
            self.password= ''



#-----------------------------
class Collection(object):

    def __init__(self, **parms):
        """
        **parms are URL params:
        - fields - [] or None (fields to return)
        - query - {} or None (query to db before defined in meta-data)
        """
        self.raw_usrdef_fields= parms.pop("fields", []) # before match against metadata
        self.raw_query= parms.pop("query", {}) # before update from metadata
        self.warning= None # non-critical errors and typos
        self.response= 'OK' # Collection class is optimistic
        self.count= 0

    def get_metadata(self, datasrc, dataset_id, view_id, issue):
        self.metadata= {}

        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= error_code['20']
            self.request= "unknown"
        else:
            self.response= "OK"
            self.request= metadata_complete['name']

            count_query= metadata_complete['query'] # used for counting

            # define useless keys
            useless_keys= ['ns', 'aux', 'batchsize', 'sort', 'query', 'explorable', 'name', 'dataset', 'idef', 'issue']

            if len(self.raw_query) != 0: # the query is on the specific elements
                useless_keys.append('max_level') # so, max_level is also useless
                count_query.update(self.raw_query)

            # but before delete useless keys - counting children of a given parent
            metadata_complete['count']= self.get_count(datasrc, metadata_complete['ns'], count_query)

            for curr in useless_keys: # now delete useless keys
                if curr in metadata_complete:
                    del metadata_complete[curr]

            field_list_complete= metadata_complete.pop('columns')
            field_list= []
            field_names_complete= []
            if len(self.raw_usrdef_fields) > 0: # describe only user defined columns
                for fld in field_list_complete:
                    field_names_complete.append(fld['key']) # for future check
                    if fld['key'] in self.raw_usrdef_fields:
                        field_list.append(fld)
                self.fill_warning(field_names_complete) # fill self.warning
            else:
                field_list= field_list_complete # substitute 'columns' for 'fields'

            metadata_complete['fields']= field_list # to match the name of URL parameter

        self.metadata= metadata_complete
        return metadata_complete


    def get_data(self, datasrc, dataset_id, view_id, issue):
        data= []

        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= error_code['20']
            self.request= "unknown"
        else:
            self.response= "OK"
            self.request= metadata_complete['name']

            conn_coll= metadata_complete['ns'] # collection name

            cursor_fields= self.get_fields(metadata_complete) # full columns list
            cursor_sort= self.get_sort_list(metadata_complete) # list of sort columns

            try: # batch size
                cursor_batchsize= metadata_complete['batchsize']
            except:
                cursor_batchsize= 'default'

            cursor_query= metadata_complete['query'] # initial query
            if len(self.raw_query) != 0:
                cursor_query.update(self.raw_query) # additional query build on the path argument

            # EXTRACT data (rows)
            if cursor_batchsize in ['default', None]:
                cursor_data= datasrc[conn_coll].find(cursor_query, cursor_fields, sort=cursor_sort)
            else:
                cursor_data= datasrc[conn_coll].find(cursor_query, cursor_fields, sort=cursor_sort).batch_size(cursor_batchsize)
            elm_count= cursor_data.count()

            for row in cursor_data:
                data.append(row)

        self.data= data
        self.count= elm_count
        return data


    def get_tree(self, datasrc, dataset_id, view_id, issue):
        tree= []

        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= error_code['20']
            self.request= "unknown"
        else:
            self.response= "OK"
            self.request= metadata_complete['name']

            conn_coll= metadata_complete['ns'] # collection name

            cursor_fields= self.get_fields(metadata_complete) # full columns list
            cursor_sort= self.get_sort_list(metadata_complete) # list of sort columns

            cursor_query= metadata_complete['query'] # initial query
            clean_query= cursor_query.copy() # saving initial query for iteration
            if len(self.raw_query) == 0: # no additional query, extract the whole collection in a form of a tree
                cursor_query.update({ 'level': 'a' })
                cursor_data= datasrc[conn_coll].find(cursor_query, cursor_fields, sort=cursor_sort)
                for curr_root in cursor_data:
                    if 'idef' in clean_query: del clean_query['idef'] # clean the clean_query before it starts working
                    if 'parent' in clean_query: del clean_query['parent']
                    curr_branch= self.build_tree(datasrc[conn_coll], clean_query, cursor_fields, cursor_sort, curr_root['idef'])
                    tree.append(curr_branch)
            else:
                if 'idef' in self.raw_query: # root element
                    result_tree= self.build_tree(datasrc[conn_coll], cursor_query, cursor_fields, cursor_sort, self.raw_query['idef'])
                    if result_tree is not None:
                        tree.append(result_tree)
                    else:
                        self.response= error_code['10']
                else: # means we deal with URL like /a/X/b/ or /a/X/b/Y/c - which is nonesense for a tree
                    self.response= error_code['30']

        self.tree= tree
        return tree


    def build_tree(self, cl, query, columns, sortby, root):
        out= {}

        query['idef']= root

        root_elt= cl.find_one(query, columns, sort=sortby)
        if root_elt is not None:
            if not root_elt['leaf']: # there are children
                if 'idef' in query: del query['idef'] # don't need this anymore
                self._get_children_recurse(root_elt, cl, query, columns, sortby)
            else: # no children, just leave root_elt as it is
                pass
            out.update(root_elt)
        else: # error - no such data!
            out= None
        
        return out

    def _get_children_recurse(self, parent, coll, curr_query, columns, srt):
        if not parent['leaf']:
            parent['children']= []
            curr_query['parent']= parent['idef']
            crs= coll.find(curr_query, columns, sort=srt)
            if crs.count() > 0:
                for elm in crs:
                    parent['children'].append(elm)
                    self._get_children_recurse(elm, coll, curr_query, columns, srt)


    def get_count(self, datasrc, collection, count_query= {}):
        self.count= datasrc[collection].find(count_query).count()
        return self.count


    def get_fields(self, meta_data):
        fields_dict= {'_id':0} # _id is never returned
        fields_dict.update(meta_data['aux']) # list of fields to be returned in any case

        if len(self.raw_usrdef_fields) > 0:
            for fl in self.raw_usrdef_fields: # list of user defined fields to be returned
                fields_dict[fl]= 1

            field_names_complete= [] # reverse check
            for fl in meta_data['columns']:
                field_names_complete.append(fl['key'])
            self.fill_warning(field_names_complete) # fill self.warning

        else:
            md_fields= meta_data['columns'] # list of main columns to be returned
            for fld in md_fields:
                fields_dict[fld['key']]= 1
                
        return fields_dict


    def get_sort_list(self, meta_data):
        sort_list= []
        try:
            cond_sort= meta_data['sort']
        except:
            cond_sort= None

        if cond_sort is not None:
            srt= [int(k) for k, v in cond_sort.iteritems()]
            srt.sort()
            for sort_key in srt:
                sort_list.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

        return sort_list


    def get_complete_metadata(self, ds_id, ps_id, iss, dbase):
        md_complete= dbase[meta_src].find_one(
            { 'dataset': ds_id, 'idef' : ps_id, 'issue': iss },
            { '_id' : 0 }
            )
        return md_complete


    def fill_warning(self, field_names_list):
        """
        check if there are user defined fields
        that are not listed in metadata
        """
        warning_list= [] 
        for fld in self.raw_usrdef_fields:
            if fld not in field_names_list:
                warning_list.append( fld )
        if len(warning_list) == 0:
            pass
        elif len(warning_list) == 1:
            self.warning= "Column '%s' is not listed in the meta-data!" % warning_list[0]
        elif len(warning_list) > 1:
            self.warning= "Columns ['%s'] are not listed in the meta-data!" % "', '".join(warning_list)
