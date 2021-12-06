

def create_ids(mb_model):
    """
    Assigns arbitrary node ids based on species and reactions of a molybdenum model
    
    Inputs
      mb_model: nested dictionary in molybdenum format with species and reactions defined, at least
    
    Outputs
      node_to_id: dictionary with:
         keys: integers corresponding to node ids
         values: corresponding ids in the molybdenum model
    """    
    try:
        type(mb_model['species']) == dict
    except:
        raise ValueError(f'Molybdenum model must have a "species" key with a dictionary value')
    
    try:
        type(mb_model['reactions']) == dict
    except:
        raise ValueError(f'Molybdenum model must have a "reactions" key with a dictionary value')
    
    node_to_id = dict()
    mb_ids = list(mb_model['species'].keys()) + list(mb_model['reactions'].keys())
    
    for node_id, mb_id in enumerate(mb_ids, 1):
        node_to_id[node_id] = mb_id

    return node_to_id


class ModelRepresentation(object):
    def __init__(self):
        self.species = dict()
        self.reactions = dict()
        self.params = dict()
        self.node_to_id = dict()
        self.sim_params = dict()
        # not implemented yet
        # self.events = dict()

    def loadm(self, molybdenum_model):
        """Note this is not an update, erases everything that was there previously
        
        TODO: needs to be more elaborate. What if no concentration is passed as default for species? error or assign one?
        TODO: what if an specie starts with $ symbol, should we turn Fixed=True automatically? I would say, yes! and raise error if Fixed was explicitly false but $ is in name, this would cause confusion
        TODO: perform a check that all ids (keys in dictionaries) are unique for species, params and reactions, if not invalid format
        """
        import copy
        # copy is important or next steps would be modifying initial dictionary
        # deepcopy is required because there are recursive lists/dictionaries and .copy() does not copy them
        mbmod = copy.deepcopy(molybdenum_model)
        self.species = mbmod['species']
        self.reactions = mbmod['reactions']
        self.params = mbmod['params']
        # some are optional
        if 'node_to_id' in mbmod.keys():
            self.node_to_id = mbmod['node_to_id']
        else:
            # if not there, create it from ids in the model
            self.node_to_id = create_ids(mbmod)
        if 'sim_params' in mbmod.keys():
            self.sim_params = mbmod['sim_params']
        else:
            # keep empty, if user tries to use it, will raise error
            self.sim_params = dict()
        return None
    
    def todict(self):
        """
        Get all information in a nested dictionary
        """
        return self.__dict__
        
    def tojson(self):
        """
        In Json things are double quoted and false is in lowercase
        """
        import json
        json_rep = json.dumps(self.todict())
        return json_rep
    
    def tosimpleSbml(self):
        """Need to write this up now"""
        #TODO: is importing inside the function correct?
        import simplesbml
        # initialize a model
        simpSbml_rep = simplesbml.SbmlModel()
        
        # add species
        for spec in self.species.values():
            # if species is fixed, add $ sign to its name (if not there already) so that
            # simpleSbml understands it is boundary / fixed
            if spec['fixed'] and spec['name'][0] != '$':
                spec_name = '$' + spec['name']
            else:
                spec_name = spec['name']
            # component support in the future
            simpSbml_rep.addSpecies(species_id = spec_name, amt = spec['amt'])#, comp='c1')
        
        # add reactions
        for reac in self.reactions.values():
            simpSbml_rep.addReaction(reactants=reac['reagents'],
                                     products=reac['products'],
                                     expression=reac['expression'],
                                     rxn_id=reac['name'])

        # add parameters
        for param in self.params.values():
            simpSbml_rep.addParameter(param_id=param['name'],
                                      val=param['val'],
                                      units='per_second') # unit support not yet

        return simpSbml_rep

    def toSBMLstr(self):
        # gets smbl
        simpSbml_rep = self.tosimpleSbml()
        #toSBML is also a function from simpleSBML models that gets the sbml string, (confusing?)
        sbml_str = simpSbml_rep.toSBML()
        return sbml_str

    def tosimpleSbmlWriteup(self):
        import simplesbml
        sbml_rep = self.toSBMLstr()
        sbml_writeup = simplesbml.simplesbml.writeCodeFromString(sbml_rep)
        return sbml_writeup

    def toAntimony(self):
        import tellurium as te
        r = te.antimonyConverter()
        sbml_str = self.toSBMLstr()
        sb_rep = r.sbmlToAntimony(sbml_str)[1]
        return sb_rep

    def toGraph(self):
        """
        Need to write this one up
        #TODO: for this, new X and Y values should be blank or zero, leave it up for further development
        """      
        # initialize object to keep graph
        graph_rep = {'nodes': [], 'edges': []}
        
        # fill in node information
        for node_id, mb_id in self.node_to_id.items():
            # search for information in species or reactions
            if mb_id in self.species.keys():
                title = self.species[mb_id]['name']
                node_class = 'species'
            elif mb_id in self.reactions.keys():
                title = self.reactions[mb_id]['name']
                node_class = 'reactions'
            else:
                raise ValueError(f'Could not find molybdenum id {mb_id} from node_to_id in species or reactions')

            # keep information
            node_info = {
                'id': node_id,
                'title': title,
                'x': 0.0,
                'y': 0.0,
                'nodeClass': node_class
            }
            graph_rep['nodes'].append(node_info)
            
        # fill in edge information from reactions
        # inverse the information in nodes_to_id
        id_to_nodes = {v: k for k, v in self.node_to_id.items()}
        # relate each species name to its id
        spec_name_to_id = {spec_info['name']: spec_id for spec_id, spec_info in self.species.items()}
        # then iterate by each reaction
        for reac_mb_id, reac in self.reactions.items():
            # first reagents
            for reagent in reac['reagents']:
                # source is the species
                source = id_to_nodes[spec_name_to_id[reagent]]
                # target is the reaction
                target = id_to_nodes[reac_mb_id]
                # keep information
                graph_rep['edges'].append({'source': source,
                                           'target': target})
            # then products
            for product in reac['products']:
                # source is the reaction
                source = id_to_nodes[reac_mb_id]
                # target is the species
                target = id_to_nodes[spec_name_to_id[product]]
                # keep information
                graph_rep['edges'].append({'source': source,
                                           'target': target})

        return graph_rep
    
    def check_nodes(self, graph_rep):
        """
        Checks if there are any new species or reactions
        
        Inputs:
          graph_rep: graphical representation of the model
        
        Outputs:
          nested dictionary indicating new or deleted species or reactions
        """
        graph_rep = graph_rep.copy()
        new_nodes = {'species':[],'reactions':[]}
        del_nodes = {'species':[],'reactions':[]}
        # check which ones are new
        for graph_node in graph_rep['nodes']:
            if graph_node['id'] not in self.node_to_id.keys():
                new_nodes[graph_node['nodeClass']].append(graph_node['id'])
            else:
                pass
        
        # check which ones are no longer there
        # get list of current nodes in graph
        graph_ids = [graph_node['id'] for graph_node in graph_rep['nodes']]
        # get relation of model ids to node ids
        id_to_nodes = {v: k for k, v in self.node_to_id.items()}
        # check if all current nodes in model are there or have been deleted
        for species_id in self.species.keys():
            if id_to_nodes[species_id] not in graph_ids:
                del_nodes['species'].append(id_to_nodes[species_id])
        
        for reaction_id in self.reactions.keys():
            if id_to_nodes[reaction_id] not in graph_ids:
                del_nodes['reactions'].append(id_to_nodes[reaction_id])

        return new_nodes, del_nodes

    def get_new_id(self, comp_class):
        """
        Generates new IDs for species, reactions or parameters
        """
        # define the prefix for each component class
        prefixes = {'species': 'spec',
                    'reactions': 'reac',
                    'params': 'param'}
        try:
            prefix = prefixes[comp_class]
        except:
            raise ValueError(f'Component class must be one of {list(prefixes.keys())}, but got {comp_class}')
        
        ct = 1
        while prefix+str(ct) in self.todict()[comp_class].keys():
            ct += 1
        return prefix+str(ct)
    
    ## TODO: what is the correct place to locate functions that do not use self? in or out the class or in a utils module?
    def init_spec(self, name, amt=10.0, fixed=False):
        if name[0] == '$':
            fixed=True
        try:
            new_spec = {'name': str(name),
                       'amt': float(amt),
                       'fixed': bool(fixed)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for specie')
            
        return new_spec
     
    def init_reac(self, name, reagents=[], products=[], expression=''):
        try:
            new_reac = {'name': str(name),
                        'reagents': list(reagents),
                        'products': list(products),
                        'expression': str(expression)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for reaction')
            
        return new_reac
    
    def init_param(self, name, val=0.0):
        try:
            new_param = {'name': str(name),
                        'val': float(val)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for parameter')
            
        return new_param

    #TODO: this one does not use self, should go outside of class?
    def update_expr(self, expr, old_name, new_name):
        """
        Note that it looks at each element because manipulating a string
        would go wrong with parameter names that are subparts of other parameter names, like E and ES
        """
        import re
        # surrounding it with parenthesis keeps the element that triggers splitting
        math_chars = '([+\-*\[\]\(\)\s,;^])'
        # split into math symbols
        split_exp = re.split(math_chars, expr)
        # replace name and merge back into string
        updated_expression = ''.join([new_name if name==old_name else name for name in split_exp])
        return updated_expression
    
    def update_name_byid(self, node_id, node_name):
        """
        Updates one name based on its id.
        If it is a species name, changes it in the reaction expressions that use it
        Note: does not work for parameters, as they are not in node_to_id
        """
        try:
            mb_id = self.node_to_id[node_id]
        except:
            raise ValueError(f'Could not find {node_id} in node_to_id relations')
            
        if mb_id in self.species.keys():
            # get previous species name
            prev_name = self.species[mb_id]['name']
            # check if name has changed
            if prev_name != node_name:
                # if yes, update the expressions in reactions
                for reac_info in self.reactions.values():
                    reac_info['expression'] = self.update_expr(reac_info['expression'], prev_name, node_name)
            else:
                pass
            # finally, update name to new one
            self.species[mb_id]['name'] = node_name
        elif mb_id in self.reactions.keys():
            self.reactions[mb_id]['name'] = node_name
        else:
            raise ValueError(f'Did not find id {node_id} in model')
            
        return None
    
    def add_connection(self, source, target):
        """
        Adds connection between source and target.
        Raises warning if connection is within components of same type
        Adds as products or reagents depending on which is source or target
        """
        import warnings

        source_id = self.node_to_id[source]
        target_id = self.node_to_id[target]
        # if source is species, target is reaction
        if (source_id in self.species.keys()) and (target_id in self.reactions.keys()):
            # add source species as reagent in the target reaction
            self.reactions[target_id]['reagents'].append(self.species[source_id]['name'])
        elif (target_id in self.species.keys()) and (source_id in self.reactions.keys()):
            # add target species as product in the source reaction
            self.reactions[source_id]['products'].append(self.species[target_id]['name'])
        else:
            # shout warning if the connection does not relate species with reaction
            # this ignores it in terms of affecting the model
            warnings.warn(f'Warning, connection {source, target} is not between a species and a reaction')
        return None
    
    def get_reac_params(self):
        """
        Gets parameters used in reaction expressions.
        Basically splits expressions and excludes elements that are species
        Ex. '(kon*E*S-koff*ES)'
        out: ['kon', 'koff']
        """
        import re
        # define mathematical characters to split the expression into
        math_chars = '[+\-*\[\]\(\)\s,;^]'
        # initialize parameter list
        param_list = []
        
        for reac in self.reactions.values():
            # split expression by math characters, giving a list of parameters and species
            vals = re.split(math_chars, reac['expression'])
            for val in vals:
                if val == '':
                    # sometimes gets empty values if two math operations following or first/last are parenthesis
                    pass
                elif val in [spec['name'] for spec in self.species.values()]:
                    # value is actually a specie, not a parameter
                    pass
                else:
                    # only possible alternative is that value is a parameter
                    param_list.append(val)

        return param_list

    def update_parameters(self):
        """Creates new parameters, delete no longer used ones"""
        # get list of parameters used by reactions
        reac_param = self.get_reac_params()
        # get list of parameters in model
        model_param = [param['name'] for param in self.params.values()]
        
        # list of parameters in reactions not yet in model
        new_param = [param for param in reac_param if param not in model_param]
        # list of parameters in model not used in reactions
        del_param = [param for param in model_param if param not in reac_param]
        
        # add new parameters
        for param_name in new_param:
            new_id = self.get_new_id('params')
            self.params[new_id] = self.init_param(param_name)
        
        # get relation of param name and its id
        param_name_to_id = {par_info['name']: par_id for par_id, par_info in self.params.items()}
        # delete unused parameters
        for param in del_param:
            self.params.pop(param_name_to_id[param])

        return None
    
    def update_from_graph(self, graph_rep_init):
        """
        Update model from a graphical representation
        """
        import copy
        graph_rep = copy.deepcopy(graph_rep_init)
        
        ## TODO: write functions to check that graph_rep format is okay (unique ids, etc..)
        
        # get new/deleted node ids and its type (species or reactions)
        new_nodes, del_nodes = self.check_nodes(graph_rep)
        # for each new species
        for new_node_id in new_nodes['species']:
            # create an id for it in the format 'spec{int}'
            new_id = self.get_new_id('species')
            # get name defined in graph, this is always one element as ids are unique
            name = [node['title'] for node in graph_rep['nodes'] if node['id'] == new_node_id][0]
            # add the new species
            self.species[new_id] = self.init_spec(name)
            # add relation between new node and new id
            self.node_to_id[new_node_id] = new_id
            
        # for each new reaction
        for new_node_id in new_nodes['reactions']:
            # create a name for it in the format 'reac{int}'
            new_id = self.get_new_id('reactions')
            # get name defined in graph, this is always one element as ids are unique
            name = [node['title'] for node in graph_rep['nodes'] if node['id'] == new_node_id][0]
            # add the new species
            self.reactions[new_id] = self.init_reac(name)
            # add relation between new node and new id
            self.node_to_id[new_node_id] = new_id
            
        # for each deleted species
        for del_node_id in del_nodes['species']:
            # delete this specie
            self.species.pop(self.node_to_id[del_node_id])
            # delete its relation in node_to_id
            self.node_to_id.pop(del_node_id)
            
        # for each deleted reaction
        for del_node_id in del_nodes['reactions']:
            # delete this reaction
            self.reactions.pop(self.node_to_id[del_node_id])
            # delete its relation in node_to_id
            self.node_to_id.pop(del_node_id)
            
        # update all names of species and reagents
        for node_info in graph_rep['nodes']:
            node_id = node_info['id']
            node_name = node_info['title']
            # this also updates the species name in reaction expressions
            self.update_name_byid(node_id, node_name)
        
        # update all connectivity in reactions based on edges and nodes
        # first delete all reagents and products information
        for reac in self.reactions.values():
            reac['reagents'] = []
            reac['products'] = []
        # then refill it
        for edge_info in graph_rep['edges']:
            self.add_connection(edge_info['source'], edge_info['target'])
            
        # update parameters
        self.update_parameters()      
        
        return None

