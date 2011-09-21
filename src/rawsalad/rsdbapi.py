# -*- coding: utf-8 -*-
"""
project: Raw Salad
function: classes representing the API to data and meta-data
requirements: mongod, conf file (see conf_filename)
"""

from time import time
from ConfigParser import ConfigParser
import pymongo
import re

meta_src= "md_budg_scheme"
state_counter= "md_sta_cnt"
nav_schema= "ms_nav"
conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/rawsdata.conf"

class Response:
    """
    response object
    returns dict with http response and description
    """
    def __init__(self):
        self.code= 0 # Response class is optimistic
        self.response_dict= {
            '0': {
                'httpresp': 200,
                'descr': 'OK'
                },
            '10': {
                'httpresp': 404,
                'descr': 'ERROR: No such data!'
                },
            '20': {
                'httpresp': 404,
                'descr': 'ERROR: No such meta-data!'
                },
            '30': {
                'httpresp': 400,
                'descr': 'ERROR: Bad request!'
                },
            '31': {
                'httpresp': 400,
                'descr': 'ERROR: Scope +TO+ is applicable to the codes on the same level!'
                },
            '32': {
                'httpresp': 400,
                'descr': 'ERROR: Wrong sequence in the scope +TO+!'
                },
            '33': {
                'httpresp': 400,
                'descr': 'ERROR: Scope +TO+ should include only 2 elements!'
                },
            '34': {
                'httpresp': 400,
                'descr': 'ERROR: Syntax error in scope definition!',
                },
            '35': {
                'httpresp': 400,
                'descr': 'ERROR: Format not specified!'
                },
            '36': {
                'httpresp': 400,
                'descr': 'ERROR: Search string not given!'
                },
            '37': {
                'httpresp': 404,
                'descr': 'ERROR: No such collection(s)!'
                },
            '40': {
                'httpresp': 404,
                'descr': 'ERROR: No data for specified state id!'
                },
            '41': {
                'httpresp': 500,
                'descr': 'ERROR: Cannot insert state data into the db!'
                },
            '42': {
                'httpresp': 400,
                'descr': 'ERROR: Wrong state id!'
                }
            }

    def __del__(self):
        pass

    def get_response(self, code):
        self.code= code
        self.http_resp= self.response_dict[str(code)]['httpresp']
        self.descr= self.response_dict[str(code)]['descr']
        return self.response_dict[str(code)]

class DBconnect:
    def __init__(self, db_type):
        if db_type == 'mongodb':
            self.fill_connection(db_type)
            self.connect= pymongo.Connection(self.host, self.port)
            dbase= self.connect[self.database]
            dbase.authenticate(self.username, self.password)
        elif db_type == 'postgresql':
            dbase= None # not yet realized

        self.dbconnect= dbase

    def __del__(self):
        pass

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
            self.host= 'cecyf.megivps.pl'
            self.port= 8000
            self.database= 'rawsdoc00'
            self.username= 'readonly'
            self.password= ''

class Navtree:
    """ Navigator tree """
    def __init__(self, **parms):
        """
        **parms are:
        - fields_aux - {} specified keys from the structure
        - query_aux - {} additional query conditions
        """
        self.fields= parms.pop("fields_aux", {}) # before match against metadata
        self.query= parms.pop("query_aux", {}) # before update from metadata
        self.response= Response().get_response(0) # Navtree class is optimistic

    def __del__(self):
        pass

    def get_nav_full(self, datasrc):
        out= []

        self.request= 'navigator'

        nav_fields= {'_id':0} # _id is never returned
        nav_fields.update(self.fields)

        query= {} # query conditions
        query.update(self.query) # additional query, depends on the call
        
        cursor_data= datasrc[nav_schema].find(query, nav_fields)
        if cursor_data is not None:
            self.response= Response().get_response(0)
            for row in cursor_data:
                out.append(row)
        else: # error
            self.response= Response().get_response(10)

        return out

    def get_dataset(self, datasrc):
        out= []
        self.request= 'dataset'

        cursor_data= datasrc[nav_schema].find({}, { '_id':0, 'perspectives':0 })
        if cursor_data.count() > 0:
            self.response= Response().get_response(0) # no error
            for row in cursor_data:
                out.append(row)
        else:
            self.response= Response().get_response(10)

        return out

    def get_view(self, datasrc, dataset_idef):
        out= []
        self.request= 'view'

        nav_fields= {
            '_id':0,
            'perspectives.idef':1,
            'perspectives.name':1,
            'perspectives.description':1,
            'perspectives.long_description':1
            }
        query= { 'idef': int(dataset_idef) }
        cursor_data= datasrc[nav_schema].find_one(query, nav_fields)
        if cursor_data is not None:
            self.response= Response().get_response(0)
            out= cursor_data['perspectives']
        else: # error
            self.response= Response().get_response(10)

        return out

    def get_issue(self, datasrc, dataset_idef, view_idef):
        out= []
        self.request= 'issue'

        nav_fields= { '_id':0, 'perspectives.issues':1 }
        query={
            'idef': int(dataset_idef),
            'perspectives': { '$elemMatch': { 'idef': int(view_idef) } }
            }
        cursor_data= datasrc[nav_schema].find_one(query, nav_fields)
        if cursor_data is not None:
            self.response= Response().get_response(0)
            out= cursor_data['perspectives'][int(view_idef)]['issues']
        else: # error
            self.response= Response().get_response(10)

        return out

    def get_count(self, datasrc, dataset_idef= None, view_idef= None):
        count= 0

        if dataset_idef is None and view_idef is None: # datasets count
            element_list= self.get_dataset(datasrc)
        elif dataset_idef is not None and view_idef is None: # views count
            element_list= self.get_view(datasrc, dataset_idef)
        else: # issues count
            element_list= self.get_issue(datasrc, dataset_idef, view_idef)        
            
        if self.response['httpresp'] == 200:
            count= len(element_list)
        else:
            self.response= Response().get_response(20)

        return count

class Collection:
    """
    extraction of the imformation from the db
    params: dataset, view, issue
    additional params: query, user defined list of fields
    """
    def __init__(self, **parms):
        """
        **parms are URL params:
        - fields - [] or None (fields to return)
        - query - {} or None (query to db before defined in meta-data)
        """
        self.raw_usrdef_fields= parms.pop("fields", []) # before match against metadata
        self.request_fields= {}
        if len(self.raw_usrdef_fields) > 0:
            self.set_fields(self.raw_usrdef_fields) # for queries
        self.raw_query= parms.pop("query", {}) # before update from metadata
        self.warning= None # non-critical errors and typos
        self.response= Response().get_response(0) # Collection class is optimistic
        self.count= 0

    def __del__(self):
        pass

    def set_query(self, query):
        if query is not None:
            self.raw_query= query

    def set_fields(self, field_list= None):
        if field_list is not None:
            self.request_fields= { k:1 for k in field_list }
        else:
            self.request_fields= { }

    def get_metadata(self, datasrc, dataset_id, view_id, issue):
        metadata= {}
        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= Response().get_response(20)
            self.request= "unknown"
        else:
            self.response= Response().get_response(0)
            self.request= metadata_complete['name']

            count_query= metadata_complete['query'] # used for counting

            # define useless keys
            useless_keys= ['ns', 'aux', 'batchsize', 'sort', 'query', 'explorable', 'name', 'dataset', 'idef', 'issue']

            if len(self.raw_query) != 0: # the query is on the specific elements
                useless_keys.append('max_level') # so, max_level is also useless
                count_query.update(self.raw_query)

            # but before delete useless keys - counting children of a given parent
            count= self.get_count(datasrc, metadata_complete['ns'], count_query)
            if count == 0:
                self.response= Response().get_response(10)
            else:
                metadata_complete['count']= count

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
                metadata= metadata_complete

        return metadata

    def get_complete_metadata(self, ds_id, ps_id, iss, dbase, use_fields= False):
        field_dict= { '_id' : 0 }
        if use_fields: # return only the fields specified in self.request_fields
            field_dict.update(self.request_fields)
        self.metadata_complete= dbase[meta_src].find_one(
            { 'dataset': ds_id, 'idef' : ps_id, 'issue': iss },
            field_dict
            )
        return self.metadata_complete

    def get_data(self, datasrc, dataset_id, view_id, issue):
        data= []
        elm_count= 0

        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= Response().get_response(20)
            self.request= "unknown"
        else:
            self.response= Response().get_response(0)
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

            if cursor_data.count() > 0:
                elm_count= cursor_data.count()
                for row in cursor_data:
                    data.append(row)
            else:
                self.response= Response().get_response(10)

        self.count= elm_count
        return data


    def get_tree(self, datasrc, dataset_id, view_id, issue):
        tree= []

        metadata_complete= self.get_complete_metadata(
            int(dataset_id), int(view_id), str(issue), datasrc
            )

        if metadata_complete is None: # no such source
            self.response= Response().get_response(20)
            self.request= "unknown"
        else:
            self.response= Response().get_response(0)
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
                    else: # error
                        self.response= Response().get_response(10)
                else: # means we deal with URL like /a/X/b/ or /a/X/b/Y/c - which is nonesense for a tree
                    self.response= Response().get_response(30)

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

        if len(self.request_fields) > 0:
            fields_dict.update(self.request_fields)

            field_names_complete= [] # reverse check
            for fl in meta_data['columns']:
                field_names_complete.append(fl['key'])

            aux_fields= [k for k,v in meta_data['aux'].iteritems()]
            self.fill_warning( field_names_complete + aux_fields ) # fill self.warning

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
            self.warning= "There is no such column as '%s' in meta-data!" % warning_list[0]
        elif len(warning_list) > 1:
            self.warning= "There are no such columns as ['%s'] in meta-data!" % "', '".join(warning_list)


class State:
    """
    the class saves to and restores from mongo
    the current state of open datasheets
    """
    def __init__(self):
        self.response= Response().get_response(0) # CollectionState class is optimistic
        
    def __del__(self):
        pass

    def get_state(self, state_id, datasrc):
        """ extracts user view (string) from the db """
        data= ''
        success= True

        if state_id == 0 or state_id is None:
            self.response= Response().get_response(42) # no data
            success= False

        if success:
            state_coll_name= ''
            try:
                state_coll_name=  "_".join(["sd", "%07d" % state_id])
            except:
                success= False
                self.response= Response().get_response(42) # wrong state id

        if success:
            state_dict= datasrc[state_coll_name].find_one() # state is always a single object
            if state_dict is not None:
                data= state_dict['content']
            else:
                self.response= Response().get_response(40) # no state data

        return data

    def save_state(self, state_object, datasrc):
        """
        saves state compiled by a user
        into the db collection sd_0000xxxx
        returns xxxx (id for permalink)
        """
        state_id= 0 # generate state id
        state_id_dict= datasrc[state_counter].find_one( {'curr_state_id': True } )
        if state_id_dict is None: # not yet created
            state_id, state_id_inc= 0, 1
            state_id_dict= {
                "curr_state_id":True,
                "curr_id": state_id,
                "increment": state_id_inc
                }

        if state_object is not None: # save object to the db
            state_id= int(state_id_dict['curr_id']) + state_id_dict['increment']
            state_collection_name= "_".join(["sd", "%07d" % state_id]) # sd - state data
            success= True
            try:
                datasrc[state_collection_name].insert({ 'content': state_object })
            except Exception as e:
                print e
                success= False

            if success: # incrementing state counter & saving it into the db
                state_id_dict['curr_id']= state_id
                datasrc[state_counter].save(state_id_dict)
            else:
                self.response= Response().get_response(41) # can't insert into the db
        else:
            self.response= Response().get_response(40) # bad request - data is empty

        return state_id


class Search:
    """
    the class searches through data in mongo
    """
    def __init__(self):
        self.set_query( None )
        self.set_scope( None )
        self.strict= False
        self.found= {} # results in short form
        self.response= Response().get_response(0) # Search class is optimistic

    def __del__(self):
        self.found= None

    def set_query(self, query):
        self.qrystr= query

    def set_scope(self, scope):
        self.scope= scope

    def set_lookup(self, lookup):
        self.lookup= lookup
        if lookup is None:
            self.lookup= []

    def switch_strict(self, strict):
        if strict:
            self.strict= True

    def do_search(self, regx, dbconn, collect):
        """
        TO-DO:
        - search with automatic substitution of specific polish letters
          (lowercase & uppercase): user can enter 'lodz', but the search
          should find 'Łódż' as well
        - search with flexible processing of prefixes and suffixes
          (see str.endswith and startswith)
        - search in 'info' keys (???)
        """
        
        ns_list= [] # list of results
        error_list= []
        found_num= 0 # number of records found
        exclude_fields= ['idef', 'idef_sort', 'parent', 'parent_sort', 'level'] # not all fields are searchable!

        for sc in self.scope: # fill the list of collections
            sc_list= sc.split('-')
            dataset, idef, issue= int(sc_list[0]), int(sc_list[1]), str(sc_list[2])
            collect.set_fields( ["perspective", "ns", "columns"] )
            metadata= collect.get_complete_metadata(dataset, idef, issue, dbconn)
            if metadata is None:
                error_list.append('collection not found %s' % sc)
            else:
                curr_coll_dict= {
                    'perspective': metadata['perspective'],
                    'dataset': dataset,
                    'view': idef,
                    'issue': issue,
                    'data': []
                    }

                collect.set_fields(None) # presumed to search through all fields
                for fld in metadata['columns']:
                    if 'processable' in fld:

                        check_str= fld['type'] == 'string'
                        if len(self.lookup) > 0:
                            check_valid= fld['key'] in self.lookup
                        else:
                            check_valid= fld['key'] not in exclude_fields

                        if fld['processable'] and check_str and check_valid:
                            search_query= { fld['key']: regx }
                            collect.set_query(search_query)

                            # actual query to the db
                            found= collect.get_data(dbconn, dataset, idef, issue)

                            for found_elt in found:
                                # control of what is already found
                                if sc not in self.found:
                                    self.found[sc]= []
                                if found_elt['idef'] not in self.found[sc]:
                                    self.found[sc].append(found_elt['idef'])
                                
                                    curr_coll_dict['data'].append({
                                        'key': fld['key'],
                                        'text': found_elt[str(fld['key'])],
                                        'idef': found_elt['idef'],
                                        'parent': found_elt['parent']
                                        })
                                    found_num += 1

                if len(curr_coll_dict['data']) > 0:
                    ns_list.append(curr_coll_dict)

        out_dict= { 'records_found': found_num, 'result': ns_list }
        if len(error_list) > 0:
            out_dict['errors']= error_list
        
        return out_dict


    def build_regexp(self, searchline, strict):
        """ construct regexp for search """
        if strict:
            # version 1 - have problems
            # searchline= "^%(lookupstr)s([^a-z][^A-Z][^0-9]|\s)|([^a-z][^A-Z][^0-9]|\s)%(lookupstr)s([^a-z][^A-Z][^0-9]|\s)|([^a-z][^A-Z][^0-9]|\s)%(lookupstr)s$" % { "lookupstr": searchline }
            # version 2
            searchline= r"^%(lookupstr)s(\s)+|^%(lookupstr)s$|\s+%(lookupstr)s\s+|\s+%(lookupstr)s$" % { "lookupstr": searchline }
        return searchline

    def search_data(self, datasrc, qrystr, scope, strict, lookup= None):
        self.set_query(qrystr)
        self.set_scope(scope)
        self.switch_strict(strict)
        self.set_lookup(lookup)

        regxsearch= self.build_regexp( self.qrystr, self.strict )
        regx= re.compile(regxsearch, re.IGNORECASE)

        coll= Collection()
        out= { }
        total_rec= 0

        self.found= {}

        # 1st pass
        tl1= time() # starting to search
        result_1= self.do_search(regx, datasrc, coll)
        total_rec += result_1['records_found']
        tlap1= time()-tl1 # 1st pass finished
        result_1.update( { "search_time": "%0.6f" % tlap1 } )
        out['strict']= result_1

        # 2nd pass
        second_pass_list= []
        if not self.strict: # second pass makes sense
            result_2= { 'records_found': 0 } # blank dict for 2nd pass
            tl2= time() # starting to search

            second_pass_list= self.qrystr.split(' ')
            if len(second_pass_list) > 1: # 2nd pass makes sense only if search str consists of >1 words

                for wrd in second_pass_list:
                    lookup= self.build_regexp(wrd, True) # we look for separate words using strict
                    regx= re.compile(lookup, re.IGNORECASE)
                    result_2_curr= self.do_search(regx, datasrc, coll)

                    if result_2_curr['records_found'] > 0:
                        result_2['result']= result_2_curr['result']
                        result_2['records_found'] += result_2_curr['records_found']

                    total_rec += result_2_curr['records_found']

            tlap2= time()-tl2 # 2nd pass finished
            result_2.update( { "search_time": "%0.6f" % tlap2 } )

            out['loose']= result_2

        tlap= time()-tl1
        out.update( {
            'search_time_total': "%0.6f" % tlap,
            'records_found_total': total_rec
            } )

        return out
