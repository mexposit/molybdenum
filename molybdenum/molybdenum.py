import re, copy, io, base64
import warnings
import json

import pandas as pd
import simplesbml
import tellurium as te

class MolybdenumModel(object):
    def __init__(self):
        self.species = dict()
        self.reactions = dict()
        self.params = dict()
        self.node_to_id = dict()
        self.sim_params = dict()
        # not implemented yet
        # self.events = dict()   

    def create_ids(self):
        """
        Assigns arbitrary node ids based on species and reactions of a molybdenum model
        
        Inputs
        mb_model: nested dictionary in molybdenum format with species and reactions defined, at least
        
        Outputs
        node_to_id: dictionary with:
            keys: integers corresponding to node ids
            values: corresponding ids in the molybdenum model
        """    

        node_to_id = dict()
        mb_ids = list(self.species.keys()) + list(self.reactions.keys())
        
        for node_id, mb_id in enumerate(mb_ids, 1):
            node_to_id[node_id] = mb_id

        self.node_to_id = node_to_id

        return None

    def loadm(self, molybdenum_model):
        """
        Note this is not an update, erases everything that was there previously
        
        TODO: what if an specie starts with $ symbol, should we turn Fixed=True automatically? I would say, yes! and raise error if Fixed was explicitly false but $ is in name, this would cause confusion
        """
        

        if type(molybdenum_model) != dict:
            raise ValueError(f'Molybdenum model must be entered as a dictionary, but got {type(molybdenum_model)}')
        
        
        # copy is important or next steps would be modifying initial dictionary
        # deepcopy is required because there are recursive lists/dictionaries and .copy() does not copy them
        mbmod = copy.deepcopy(molybdenum_model)

        if 'species' not in mbmod.keys():
            raise ValueError(f'Molybdenum model must have a "species" key')
        elif 'reactions' not in mbmod.keys():
            raise ValueError(f'Molybdenum model must have a "reactions" key')
        elif 'params' not in mbmod.keys():
            raise ValueError(f'Molybdenum model must have a "params" key')
        else:
            pass
        
        if type(mbmod['species']) != dict:
            raise ValueError(f'Molybdenum model must have a "species" key with a dictionary value, but got {type(mbmod["species"])}')
        
        if type(mbmod['reactions']) != dict:
            raise ValueError(f'Molybdenum model must have a "reactions" key with a dictionary value, but got {type(mbmod["species"])}')
        
        if type(mbmod['params']) != dict:
            raise ValueError(f'Molybdenum model must have a "params" key with a dictionary value, but got {type(mbmod["species"])}')
        
        # check that all ids (keys within species, reactions and params) are unique
        ids_list = list(mbmod['species'].keys()) + list(mbmod['reactions'].keys()) + list(mbmod['params'].keys())
        
        if len(set(ids_list)) != len(ids_list):
            raise ValueError(f'Not all ids in molybdenum model are unique')

        # assign necessary keys
        self.species = mbmod['species']
        self.reactions = mbmod['reactions']
        self.params = mbmod['params']

        # some keys are optional
        if 'node_to_id' in mbmod.keys():
            self.node_to_id = mbmod['node_to_id']
        else:
            # if not there, create it from ids in the model
            self.create_ids()
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
        In Json, things are double quoted and false is in lowercase
        """
        json_rep = json.dumps(self.todict())
        return json_rep

    def get_modifier_names(self, reac_id):
        """
        Inputs a reaction id, searches for the expression in the reaction
        and identifies modifiers: species that are in the expression but not as reactant or product
        """
        # define mathematical characters to split the expression into
        math_chars = '[+\-*/\[\]\(\)\s,;^]'
        
        # get expression, reagents and products
        reac_expr = self.reactions[reac_id]['expression']
        reac_reag = self.reactions[reac_id]['reagents']
        reac_prod = self.reactions[reac_id]['products']

        # get species names
        spec_names = [spec['name'] for spec in self.species.values()]

        # keep track of modifiers for this reaction as list of species names
        modifiers = []
        # split expression by math characters, giving a list of parameters and species
        vals = re.split(math_chars, reac_expr)
        # iterate by each parameter
        for val in set(vals):
            # if it is neither a reagent nor a product but yes a specie, it is a modifier
            if (val not in reac_reag) and (val not in reac_prod) and (val in spec_names):
                modifiers.append(val)

        return modifiers

    
    def tosimpleSbml(self):
        """Need to write this up now"""
        # initialize a model
        simpSbml_rep = simplesbml.SbmlModel()
        
        # will keep each species added in a dictionary to use as modifiers later
        # if required
        spec_dict = {}
        # add species
        for spec in self.species.values():
            # if species is fixed, add $ sign to its name (if not there already) so that
            # simpleSbml understands it is boundary / fixed
            if spec['fixed'] and spec['name'][0] != '$':
                spec_name = '$' + spec['name']
            else:
                spec_name = spec['name']
            # component support in the future
            spec_dict[spec_name] = simpSbml_rep.addSpecies(species_id = spec_name, amt = spec['amt'])#, comp='c1')
        
        # add reactions
        for reac_id, reac in self.reactions.items():
            # keep reaction in variable in case we need to add modifiers to it
            reac_simpsbml = simpSbml_rep.addReaction(reactants=reac['reagents'],
                                     products=reac['products'],
                                     expression=reac['expression'],
                                     rxn_id=reac['name'])
            # get names of modifier species
            modifier_list = self.get_modifier_names(reac_id)
            for modifier_name in modifier_list:
                # add the addSpecies object by searching by species name in dictionary
                reac_simpsbml.addModifier(spec_dict[modifier_name])

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
        sbml_rep = self.toSBMLstr()
        sbml_writeup = simplesbml.simplesbml.writeCodeFromString(sbml_rep)
        return sbml_writeup

    def toAntimony(self):
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
        if (str(fixed) != 'False') and (str(fixed) != 'True'):
            # do not accept other values that could be parsed by bool() like
            # integers or None
            raise TypeError('Boolean values must be specified only by True or False')
        if (type(name) != str) and (type(name) != int):
            # pretty much everything can be converted to string in python
            # make sure that a string or integer is actually passed
            raise TypeError('Name must be a string or integer')
        try:
            if str(name)[0] == '$':
                fixed=True
            new_spec = {'name': str(name),
                       'amt': float(amt),
                       'fixed': bool(fixed)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for specie')
            
        return new_spec
     
    def init_reac(self, name, reagents=[], products=[], expression='undefined'):
        if (type(name) != str) and (type(name) != int):
            # pretty much everything can be converted to string in python
            # make sure that a string or integer is actually passed
            raise TypeError('Name must be a string or integer')
        if (type(expression) != str):
            # pretty much everything can be converted to string in python
            # make sure that a string or integer is actually passed
            raise TypeError('Name must be a string or integer')
        try:
            new_reac = {'name': str(name),
                        'reagents': list(reagents),
                        'products': list(products),
                        'expression': str(expression)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for reaction')
            
        return new_reac
    
    def init_param(self, name, val=0.0):
        if (type(name) != str) and (type(name) != int):
            # pretty much everything can be converted to string in python
            # make sure that a string or integer is actually passed
            raise TypeError('Name must be a string or integer')
        try:
            new_param = {'name': str(name),
                        'val': float(val)}
        except:
            raise TypeError('Some of the inputs do not agree with required types for parameter')
            
        return new_param

    #TODO: this one does not use self, should go outside of class?
    def update_expr(self, expr, old_name, new_name):
        """Changes the name of a parameter used in a reaction expression

        Args:
            expr: reaction expression as a string, ex. '2*A + B* kon / I'
            old_name: parameter or species name in the expression to be changed
            new_name: name to change old_name to

        Returns:
            updated_expression: expression with old_name replaced by new_name
                deletes all spacing between parameters, not relevant

        Notes:
            if old_name is not found in the expression, the expression is still processed
            but nothing changes
        """
        # surrounding it with parenthesis keeps the element that triggers splitting
        math_chars = '([+\-*\[\]\(\)\s,;^])'
        # split into math symbols
        split_exp = re.split(math_chars, expr)
        # replace name and merge back into string
        updated_expression = ''.join([new_name if name==old_name else name for name in split_exp])
        return updated_expression
    
    def update_name_byid(self, node_id, element_name):
        """Updates one speces or reaction name based on its node id

        Args:
            node_id: integer indicating the node id of the element to change name of
            element_name: new name to assign to the species or reaction with selected node_id

        Returns:
            updates the name in the model, so nothing is returned

        Notes:
            if changing a species name, it also updates its name in the expressions of reaction that use it
            but if changing species name, it does not update reagents/products in the reactions that use it
            does not work to rename parameters because they are not in kept track in the node_to_id dictionary
        """
        try:
            mb_id = self.node_to_id[node_id]
        except:
            raise ValueError(f'Could not find {node_id} in node_to_id relations')
            
        if mb_id in self.species.keys():
            # get previous species name
            prev_name = self.species[mb_id]['name']
            # check if name has changed
            if prev_name != element_name:
                # if yes, update the expressions in reactions
                for reac_info in self.reactions.values():
                    reac_info['expression'] = self.update_expr(reac_info['expression'], prev_name, element_name)
            else:
                pass
            # finally, update name to new one
            self.species[mb_id]['name'] = element_name
        elif mb_id in self.reactions.keys():
            self.reactions[mb_id]['name'] = element_name
        else:
            raise ValueError(f'Did not find id {node_id} in model')
            
        return None
    
    def add_connection(self, source, target):
        """Adds connection between source and target

        Args:
            source: node_id of the species or reaction where connection starts
            target: node_id of the species or reaction where connection ends

        Returns:
            updates the model directly.
            if source is a species, adds its name to reagents of target reaction.
            if source is a reaction, adds target species name to source reaction products.
        
        Raises:
            warning if both source and target are a species or a reaction
            ValueError if node id of source or target is not in node_to_id

        Notes:
            raising a warning means it ignores all connections between species or
            between reactions, but does not raise an error in response to them
        """
        try:
            source_id = self.node_to_id[source]
        except:
            raise ValueError(f'Could not find node_id with id {source}')
        
        try:
            target_id = self.node_to_id[target]
        except:
            raise ValueError(f'Could not find node_id with id {target}')
            
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

    def is_float(self, element):
        """Checks if an element can be converted to float
        
        Args:
            element: string, integer or float, or any other element
            
        Returns:
            True if element can be converted to float, False otherwise
        
        Note:
            does not consider True/False boolean values as being possible to 
            convert them to a float number (in python, float(True) == 1)
        """
        if type(element) == str or type(element) == int or type(element) == float:
            try:
                float(element)
                return True
            except ValueError:
                return False
        else:
            return False
    
    def get_reac_params(self):
        """Get parameters used in reaction expressions

        Args:
            model defined in self, uses reaction 'expression' attribute
                and species 'name' attribute
        
        Returns:
            param_list: list of strings defining the parameters used in all the
                reactions of the model.
                
        Notes:
            does not include any number, operator or species names in the list
            defining parameters
            Example input for two reactions: '(kon*E*S-koff*ES)', '2*E+ kcat+koff'
            Example output: param_list=['kon','koff','kcat']
        """
        # define mathematical characters to split the expression into
        math_chars = '[+\-*/\[\]\(\)\s,;^]'
        # initialize parameter list
        param_list = []
        
        for reac in self.reactions.values():
            # split expression by math characters, giving a list of parameters and species
            vals = re.split(math_chars, reac['expression'])
            # adding set here allows using the same parameter multiple times in the reaction
            for val in set(vals):
                if val == '':
                    # sometimes gets empty values if two math operations following or first/last are parenthesis
                    pass
                elif val in [spec['name'] for spec in self.species.values()]:
                    # value is actually a specie, not a parameter
                    pass
                elif self.is_float(val):
                    # value is an integer/float modifying one parameter
                    pass
                else:
                    # only possible alternative is that value is a parameter
                    param_list.append(val)

        return list(set(param_list))

    def update_parameters(self):
        """Creates new parameters, delete no longer used ones
        
        Args:
            checks the model defined in self to get parameters used in reactions
                and parameters defined in the params dictionary
        
        Returns:
            modifies the model in self by:
                adding to the params dictionary parameters that are used in reactions
                    but were not there yet
                removing from the params dictionary parameters not used in reactions
        """
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
            # add the new reaction
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


    def update_from_form(self, form_list):
        for form_input in form_list:
            try:
                info, value = form_input
            except:
                raise ValueError(f'Invalid form input: "{form_input}" should be a two-element tuple')
            # info further divided into component id and assigned attribute
            try:
                comp_id, att = info.split('_')
            except:
                raise ValueError(f'Invalid component or attribute: "{info}" has zero or more than one "_" signs, exactly one required')
            # value should only have one element
            if len(value) != 1:
                raise ValueError(f'Invalid form input: {value} should only be one element')
            value = value[0]
            # find component_id in species, reactions or params, find attribute and assign or raise error
            if comp_id in self.species.keys():
                try:
                    if att == 'amt':
                        self.species[comp_id][att] = float(value)
                    elif att == 'fixed':
                        self.species[comp_id][att] = bool(value)
                    else:
                        raise ValueError(f'Unrecognized attribute {att} in {form_input}')
                except:
                    raise TypeError(f'Attribute {att} in {form_input} does not match with expected type')
            elif comp_id in self.reactions.keys():
                try:
                    if att == 'expression':
                        self.reactions[comp_id][att] = str(value)
                        # update parameters after adding any expression
                        self.update_parameters()
                    else:
                        raise ValueError(f'Unrecognized attribute {att} in {form_input}')
                except:
                    raise TypeError(f'Attribute {att} in {form_input} does not match with expected type')
            elif comp_id in self.params.keys():
                try:
                    if att == 'name':
                        self.params[comp_id][att] = str(value)
                    elif att == 'val':
                        self.params[comp_id][att] = float(value)
                    else:
                        raise ValueError(f'Unrecognized attribute {att} in {form_input}')
                except:
                    raise TypeError(f'Attribute {att} in {form_input} does not match with expected type')
            else:
                # do not raise error. Previous form might contain a parameter that has been deleted and this would not be found in the keys
                pass
        
        return None

    def update_sim_params(self, sim_param):
        """Defines simulation parameters in model from a dictionary

        Args:
            sim_param: data passed in the format of an html form having the 
                attributes "sim_start", "sim_end", and/or "sim_points"
                example:
                    [
                        ('sim_start',['12.']),
                        ('sim_end',['24.']),
                        ('sim_points',['500'])
                    ]

        Returns:
            updates model defining simulation parameters in a dictionary with
            "sim_start", "sim_end" and/or "sim_points" elements
            example: {'sim_start': 12., 'sim_end': 24.,'sim_points': 500}
                
        Raises:
            ValueError if form input is not a tuple with (attr, value) format
            ValueError if form input value is a list with more than one element
            ValueError if sim_start and sim_points are not integers or floats
            ValueError if sim_points is not an integer
            ValueError if attribute is not "sim_start", "sim_end" or "sim_points"
        """
        # get dictionary from form
        form_dict = {}
        for form_input in sim_param:
            try:
                param, value = form_input
            except:
                raise ValueError(f'Invalid form input: "{form_input}" should be a two-element tuple')
            if len(value) != 1:
                raise ValueError(f'Invalid form input: {value} should only be one element')
            value = value[0]
            if (param == 'sim_start') or (param == 'sim_end'):
                try:
                    form_dict[param] = float(value)
                except:
                    raise ValueError(f'Value for "sim_start" and "sim_end" must be integer or float, but got {type(value)} for {param}')
            elif (param == 'sim_points'):
                try:
                    form_dict[param] = int(value)
                except:
                    raise ValueError(f'Value for "sim_points" must be integer, but got {type(value)}')
            else:
                raise ValueError(f'Unrecognized simulation parameter {param}, must be one of "sim_start", "sim_end" or "sim_points"')

        # then set sim_param to that dictionary
        self.sim_params = form_dict.copy()

        return None

    def run(self):
        """Simulates model and get results
        
        Args:
            uses the model representation converted to antimony to simulate it
            with tellurium

        Returns:
            temodel: tellurium model object
            results: NamedArray from tellurium simulation
        """
        temodel = te.loada(self.toAntimony())
        results = temodel.simulate(
            start=self.sim_params['sim_start'],
            end=self.sim_params['sim_end'],
            points=self.sim_params['sim_points']
        )
        return temodel, results

    def te_result_to_df(self, arr):
        """Converts namedarray results to a pandas dataframe

        Args:
            arr: NamedArray resulting from tellurium simulation

        Returns:
            df: pd.DataFrame with names for each species
        """
        columns = [c[1:-1] if c[0] == "[" else c for c in arr.colnames]
        df = pd.DataFrame(arr, columns=columns)
        return df


    def get_plot_as_htmlimage(self, temodel):
        """
        Requires model to be simulated previously
        """
        io_str = io.BytesIO()
        temodel.plot(dpi=300, savefig=io_str, format='jpg')
        io_str.seek(0)
        s = base64.b64encode(io_str.getvalue()).decode("utf-8").replace("\n", "")
        img_str = f'<img align="center" src="data:image/png;base64,{s}">'

        return img_str