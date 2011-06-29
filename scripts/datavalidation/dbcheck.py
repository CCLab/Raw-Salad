import urllib2
import json


class DataReceiver:
    """ Downloads data from server using Public API """
    
    def __init__(self):
        """ Sets base url """
        self.base_url = 'http://cecyf.megivps.pl/api/json/'
        
    def construct_url(self, dataset_id=-1, view_id=-1, issue_id=-1):
        """ Constructs different kinds of urls depending on given arguments """
        url = self.base_url + 'dataset/'
        if dataset_id >= 0:
            url += str(dataset_id) + '/view/'
            if view_id >= 0:
                url += str(view_id) + '/issue/'
                if issue_id >= 0:
                    url += str(issue_id) + '/'
                    
        return url
    
    def fetch(self, url):
        """ Downloads data from server from specified url """
        urldata = urllib2.urlopen(url)
        return urldata.read()
        
    def get_datasets(self):
        """ Downloads data about datasets """
        datasets_url = self.construct_url()
        str_result = self.fetch(datasets_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_views(self, dataset_id):
        """ Downloads data about views in dataset specified by id """
        views_url = self.construct_url(dataset_id)
        str_result = self.fetch(views_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_issues(self, dataset_id, view_id):
        """ Downloads data about issues in view specified by its id and dataset's id """
        issue_url = self.construct_url(dataset_id, view_id)
        str_result = self.fetch(issue_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_collection(self, dataset_id, view_id, issue_id):
        """ Downloads data from collection specified by dataset, view and issue """
        collection_url = self.construct_url(dataset_id, view_id, issue_id)
        str_result = self.fetch(collection_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_collection_tree(self, dataset_id, view_id, issue_id):
        """ Downloads data in tree form from collection specified by dataset, view and issue """
        collection_tree_url = self.construct_url(dataset_id, view_id, issue_id) + 'tree/'
        str_result = self.fetch(collection_tree_url)
        json_result = json.loads(str_result)
        return json_result['tree']
        
    def get_collection_meta(self, dataset_id, view_id, issue_id):
        """ Downloads metadata about collection specified by dataset, view and issue """
        collection_meta_url = self.construct_url(dataset_id, view_id, issue_id) + 'meta/'
        str_result = self.fetch(collection_meta_url)
        json_result = json.loads(str_result)
        return json_result['metadata']


class Logger:
    """ Logs messages """
    
    def __init__(self, filename):
        """ Opens logfile """
        self.file = open(filename, 'w')
        
    def log(self, message):
        """ Logs messages to logfile """
        self.file.write(message + '\n')
        
    def close(self):
        """ Closes logfile """
        self.file.close()


class Validator:
    """ Checks correctness of downloaded numerical data """
    def __init__(self, names, dataset_id, view_id, issue_id, logger):
        self.logger = logger
        self.names = names
        self.dataset_id = dataset_id
        self.view_id = view_id
        self.issue_id = issue_id
        self.bad_idefs = []
        
    def collect_values(self, subtree):
        """ Collects values from subtree and constructs a list containing them """
        values = {}
        for name in self.names:
            values[name] = subtree[name]
            
        return values
        
    def sum_values(self, values_list):
        """ Sums values from list of lists of values and returns list with summed values """
        summed_values = {}
        #init summed_values
        for key in values_list[0].keys():
            summed_values[key] = 0
        
        for values in values_list:
            for key, value in values.items():
                if value == None:
                    value = 0
                    
                summed_values[key] += value
                
        return summed_values
        
    def values_equal(self, first_list, second_list):
        """ Compares values from lists """
        equal = True
        for key in first_list.keys():
            if first_list[key] != second_list[key]:
                equal = False
                break
        
        return equal
    
    def compare_lists(self, first_list, second_list):
        """
        Compares values from lists and if there are differences, appends
        names of attributes with differences and their values
        """
        equal = True
        bad_values_names = []
        for key in first_list.keys():
            if first_list[key] != second_list[key]:
                equal = False
                cmp_err = key, first_list[key], second_list[key]
                bad_values_names.append(cmp_err)
        
        return {'result': equal, 'names': bad_values_names}
        
    def check_tree(self, data):
        """ Checks correctness of data in all subtrees """
        for subtree in data:
            subtree_values = self.collect_values(subtree)
            self.check_subtree(subtree, subtree_values)
            
        self.print_results()
        
    def check_subtree(self, subtree, subtree_root_values):
        """ Recursevily compares data in root of subtree and summed values of its children """
        if subtree['leaf']:
            return
        
        values_list = []        
        for child in subtree['children']:
            try:
                child_values = self.collect_values(child)
            except:
                self.logger.log('CRITICAL ERROR in data in row with id = ' + child['idef'] +
                                ': unable to read attributes\' values correctly')
            values_list.append(child_values)
            self.check_subtree(child, child_values)
                    
        try:
            summed_values = self.sum_values(values_list)
            compare_result = self.compare_lists(subtree_root_values, summed_values)
        except:
            self.logger.log('CRITICAL ERROR in data in row with id = ' + subtree['idef'] +
                            ': unable to sum values correctly')
            return
            
        is_equal = compare_result['result']
        if is_equal == False:
            self.bad_idefs.append({'id': subtree['idef'], 'names': compare_result['names']})
        
    def print_results(self):
        """ Saves results to a file using logger """
        if len(self.bad_idefs) == 0:
            self.logger.log('No errors in dataset = ' + str(self.dataset_id) + ', view = ' + str(self.view_id) + ', issue = ' + str(self.issue_id))
        else:
            for bad_idef in self.bad_idefs:
                self.logger.log('Error in: dataset = ' + str(self.dataset_id) + ', view = ' + str(self.view_id) + ', issue = ' + str(self.issue_id) + ', id = ' + str(bad_idef['id']) + ' on positions:')
                for err_info in bad_idef['names']:
                    self.logger.log(err_info[0] + ': ' + str(err_info[1]) + ' vs ' + str(err_info[2]))    
        

def init_names():
    """ Creates dict containg names of attributes that should be checked """
    names = {}
    names['(0, 0, 2011)'] = ['dot_sub', 'swiad_fiz', 'wyd_jednostek',
                             'wyd_majatk', 'wyd_dlug', 'sw_eu', 'wspolfin_eu',
                             'v_total', 'v_nation', 'v_eu']
    names['(0, 1, 2011)'] = ['v_total', 'v_eu', 'v_nation']
    names['(0, 1, 2012)'] = ['v_total', 'v_nation', 'v_eu']
    names['(0, 2, 2011)'] = ['v_total', 'v_nation', 'v_eu']
    names['(0, 2, 2012)'] = ['v_total', 'v_nation', 'v_eu']
    names['(1, 0, 2011)'] = [] # no data
    names['(1, 1, 2011)'] = [] # no data
    names['(2, 0, 2011)'] = ['val_2011', 'val_2012', 'val_2013']
    names['(2, 1, 2011)'] = ['frst_popr', 'plan_nast']
    names['(2, 2, 2011)'] = ['val_2011', 'val_2012', 'val_2013'] # data with errors
    names['(2, 3, 2011)'] = ['frst_popr', 'plan_nast']
    names['(3, 0, 2011)'] = ['centrala', 'dolnoslaskie','kujawskopomorskie',
                             'lubelski', 'lubuski', 'lodzki', 'malopolski',
                             'mazowiecki', 'opolski', 'podkarpacki',
                             'podlaski', 'pomorski', 'slaski', 'swietokrzyski',
                             'warminskomazurski', 'wielkopolski',
                             'zachodniopomorski', 'osrodki_wojewodzkie', 'ogolem']
    names['(3, 1, 2011)'] = ['val']
    names['(4, 0, 2011)'] = [] # no data
    
    return names


def construct_collections_map():
    """ Constructs tuples containing available dataset_ids, view_ids and issues """
    collections = []
    """
    data_receiver = DataReceiver()
    datasets = data_receiver.get_datasets()
    for dataset in datasets:
        views = data_receiver.get_views(dataset['idef'])
        for view in views:
            issues = data_receiver.get_issues(dataset['idef'], view['idef'])
            for issue in issues:
                t = dataset['idef'], view['idef'], int(issue)
                collections.append(t)
    """
    collections = [(0, 0, 2011), (0, 1, 2011), (0, 1, 2012), (0, 2, 2011),
                   (0, 2, 2012), (1, 0, 2011), (1, 1, 2011), (2, 0, 2011),
                   (2, 1, 2011), (2, 2, 2011), (2, 3, 2011), (3, 0, 2011),
                   (3, 1, 2011), (4, 0, 2011)]
    return collections


if __name__ == "__main__":
    
    logger = Logger('errors.log')
    data_receiver = DataReceiver()
    names = init_names()
    cmap = construct_collections_map()
    
    for t in cmap:
        logger.log('---------------------------------------------------------')
        if t[0] == 1 or t[0] == 4:
            logger.log('NO DATA FOR ' + str(t))
            continue
            
        logger.log('CHECK ' + str(t))
        val = Validator(names[str(t)], t[0], t[1], t[2], logger)
        collection_tree = data_receiver.get_collection_tree(t[0], t[1], t[2])
        val.check_tree(collection_tree)
    
    logger.close()
