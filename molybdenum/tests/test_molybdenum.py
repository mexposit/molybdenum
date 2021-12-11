from molybdenum import MolybdenumModel
import simplesbml
import unittest

import sys

import numpy as np
import pandas as pd

sys.path.append("../")
sys.path.append("molybdenum/")


class TestMolybdenumModel(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        # override default __init__ for TestCase so let the parent class
        # take care of this default
        super(TestMolybdenumModel, self).__init__(*args, **kwargs)

        # then define some examples to be used throughout tests
        self.example_species = {
            "spec1": {"name": "E", "amt": 5e-21, "fixed": False},
            "spec2": {"name": "S", "amt": 1e-20, "fixed": False},
            "spec3": {"name": "ES", "amt": 0.0, "fixed": False},
            "spec4": {"name": "P", "amt": 0.0, "fixed": False},
        }
        self.example_react = {
            "reac1": {
                "name": "veq",
                "reagents": ["E", "S"],
                "products": ["ES"],
                "expression": "(kon*E*S-koff*ES)",
            },
            "reac2": {
                "name": "vcat",
                "reagents": ["ES"],
                "products": ["P"],
                "expression": "kcat*ES",
            },
        }
        self.example_param = {
            "param1": {"name": "koff", "val": 0.2},
            "param2": {"name": "kon", "val": 10000000.0},
            "param3": {"name": "kcat", "val": 0.1},
        }
        self.example_sim_param = {
            "sim_start": 0.0,
            "sim_end": 10.0,
            "sim_points": 120,
        }

        self.example_mbmodel = {
            "species": self.example_species,
            "reactions": self.example_react,
            "params": self.example_param,
            "sim_params": self.example_sim_param,
        }

        # manually build node to id representation for this example model
        self.example_node_to_id = {
            1: "spec1",
            2: "spec2",
            3: "spec3",
            4: "spec4",
            5: "reac1",
            6: "reac2",
        }

        # add this to another version of the model
        self.example_mbmodel_wnode = self.example_mbmodel.copy()
        self.example_mbmodel_wnode["node_to_id"] = self.example_node_to_id

        # add expected output representations for the example model
        self.example_json = '{"species": {"spec1": {"name": "E", "amt": 5e-21, "fixed": false}, "spec2": {"name": "S", "amt": 1e-20, "fixed": false}, "spec3": {"name": "ES", "amt": 0.0, "fixed": false}, "spec4": {"name": "P", "amt": 0.0, "fixed": false}}, "reactions": {"reac1": {"name": "veq", "reagents": ["E", "S"], "products": ["ES"], "expression": "(kon*E*S-koff*ES)"}, "reac2": {"name": "vcat", "reagents": ["ES"], "products": ["P"], "expression": "kcat*ES"}}, "params": {"param1": {"name": "koff", "val": 0.2}, "param2": {"name": "kon", "val": 10000000.0}, "param3": {"name": "kcat", "val": 0.1}}, "node_to_id": {"1": "spec1", "2": "spec2", "3": "spec3", "4": "spec4", "5": "reac1", "6": "reac2"}, "sim_params": {"sim_start": 0.0, "sim_end": 10.0, "sim_points": 120}}'

        self.example_simpleSbmlWriteup = """import simplesbml
model = simplesbml.sbmlModel();
model.addSpecies(species_id='E', amt=5e-21);
model.addSpecies(species_id='S', amt=1e-20);
model.addSpecies(species_id='ES', amt=0.0);
model.addSpecies(species_id='P', amt=0.0);
model.addParameter(param_id='koff', val=0.2);
model.addParameter(param_id='kon', val=10000000.0);
model.addParameter(param_id='kcat', val=0.1);
model.addReaction(reactants=['E', 'S'], products=[
                  'ES'], expression='kon * E * S - koff * ES', rxn_id='veq');
model.addReaction(reactants=['ES'], products=['P'], expression='kcat * ES', rxn_id='vcat');"""

        self.example_antimony = """// Created by libAntimony v2.12.0
model *doc0()

  // Compartments and Species:
  compartment c1;
  species E in c1, S in c1, ES in c1, P in c1;

  // Reactions:
  veq: E + S => ES; kon*E*S - koff*ES;
  vcat: ES => P; kcat*ES;

  // Species initializations:
  E = 5e-21/c1;
  E has mole_per_litre;
  S = 1e-20/c1;
  S has mole_per_litre;
  ES = 0;
  ES has mole_per_litre;
  P = 0;
  P has mole_per_litre;

  // Compartment initializations:
  c1 = 1;
  c1 has litre;

  // Variable initializations:
  koff = 0.2;
  koff has per_second;
  kon = 10000000;
  kon has per_second;
  kcat = 0.1;
  kcat has per_second;

  // Other declarations:
  var koff, kon, kcat;
  const c1;

  // Unit definitions:
  unit per_second = 1 / second;
  unit substance = mole;
  unit extent = mole;
  unit time_unit = second;
  unit mole_per_litre = mole / litre;
end
"""
        self.example_graph = {
            "nodes": [
                {
                    "id": 1,
                    "title": "E",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 2,
                    "title": "S",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 3,
                    "title": "ES",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 4,
                    "title": "P",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 5,
                    "title": "veq",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "reactions",
                },
                {
                    "id": 6,
                    "title": "vcat",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "reactions",
                },
            ],
            "edges": [
                {"source": 1, "target": 5},
                {"source": 2, "target": 5},
                {"source": 5, "target": 3},
                {"source": 3, "target": 6},
                {"source": 6, "target": 4},
            ],
        }

        # create an updated version of the model with some changes that can be used
        # to test the update functions
        self.example_updated_mbmodel = {
            "species": {
                # change to fixed and increase concentration to 4e2
                "spec1": {"name": "E", "amt": 4e2, "fixed": True},
                # delete species 2
                # "spec2": {"name": "S", "amt": 1e-20, "fixed": False},
                # not modified
                "spec3": {"name": "ES", "amt": 0.0, "fixed": False},
                # rename from P to Prod
                "spec4": {"name": "Prod", "amt": 0.0, "fixed": False},
                # add species 5
                "spec5": {"name": "I", "amt": 0.0, "fixed": False},
            },
            "reactions": {
                # rename and change products and expression
                "reac1": {
                    "name": "veq",
                    "reagents": ["E","I"],
                    "products": ["ES"],
                    "expression": "(kon*E-koff)",
                },
                # delete reaction
                # "reac2": {
                #     "name": "vcat",
                #     "reagents": ["ES"],
                #     "products": ["P"],
                #     "expression": "kcat*ES",
                # },
                # new reaction, uses updated product name, new parameter
                "reac3": {
                    "name": "vkcat",
                    "reagents": ["ES","I"],
                    "products": ["Prod"],
                    "expression": "kcat*ES+I*kin",
                }
            },
            "params": {
                "param1": {"name": "koff", "val": 0.2},
                # deleted parameter
                # "param2": {"name": "kon", "val": 10000000.0},
                # new parameters 
                "param2": {"name": "kin", "val": 10000000.0},
                "param3": {"name": "kcat", "val": 10000000.0},
                # change value
                "param4": {"name": "kon", "val": 0.1}
            },
            "sim_params": {
                "sim_start": 0.0,
                # "sim_end": 10.0,
                # updated end
                "sim_end": 15.0,
                "sim_points": 120,
            }
        }


        self.example_updated_graph = {
            "nodes": [
                {
                    "id": 1,
                    "title": "E",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                # deleted species 2
                # {
                #     "id": 2,
                #     "title": "S",
                #     "x": 0.0,
                #     "y": 0.0,
                #     "nodeClass": "species",
                # },
                {
                    "id": 3,
                    "title": "ES",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 4,
                    "title": "Prod",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                {
                    "id": 5,
                    "title": "veq",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "reactions",
                },
                # delete reaction
                # {
                #     "id": 6,
                #     "title": "vcat",
                #     "x": 0.0,
                #     "y": 0.0,
                #     "nodeClass": "reactions",
                # },
                # added new species
                {
                    "id": 7,
                    "title": "I",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "species",
                },
                # new reaction, uses updated product name, new parameter
                {
                    "id": 8,
                    "title": "vkcat",
                    "x": 0.0,
                    "y": 0.0,
                    "nodeClass": "reactions",
                }
            ],
            "edges": [
                {"source": 1, "target": 5},
                # new connections because of new expression
                {"source": 7, "target": 5},
                # {"source": 2, "target": 5},
                {"source": 5, "target": 3},
                # {"source": 3, "target": 6},
                # {"source": 6, "target": 4},
                # new nodes
                {"source": 3, "target": 8},
                {"source": 7, "target": 8},
                {"source": 8, "target": 4}
            ],
        }

    ##################################
    ###    Test class functions    ###
    ##################################

    def test_create_ids(self):
        # assign example species and reactions to model
        mbmodel = MolybdenumModel()
        # assign species and reactions
        mbmodel.species = self.example_species
        mbmodel.reactions = self.example_react
        # create node_to_ids
        mbmodel.create_ids()
        # check if it matches with the example one
        self.assertEqual(mbmodel.node_to_id, self.example_node_to_id)

    def test_loadm(self):
        mbmodel = MolybdenumModel()
        # load example model
        mbmodel.loadm(self.example_mbmodel)
        # test if all values were assigned correctly
        self.assertEqual(mbmodel.species, self.example_species)
        self.assertEqual(mbmodel.reactions, self.example_react)
        self.assertEqual(mbmodel.params, self.example_param)
        self.assertEqual(mbmodel.sim_params, self.example_sim_param)
        self.assertEqual(mbmodel.node_to_id, self.example_node_to_id)
        # test when passing a model without simparams but still get dictionary
        mbmodel2 = MolybdenumModel()
        example_model_nosim = self.example_mbmodel.copy()
        example_model_nosim.pop("sim_params")
        mbmodel2.loadm(example_model_nosim)
        self.assertEqual(type(mbmodel2.sim_params), dict)
        # test when passing model with already initialized node_to_id
        mbmodel3 = MolybdenumModel()
        mbmodel3.loadm(self.example_mbmodel_wnode)
        self.assertEqual(mbmodel3.node_to_id, self.example_node_to_id)
        # try passing a model that is not a dictionary
        mbmodel_fail = MolybdenumModel()
        with self.assertRaises(ValueError):
            mbmodel_fail.loadm(["A", "B", "C", "D"])
        # try passing models without required keys
        mbmodel_fail = MolybdenumModel()
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail.pop("species")
            mbmodel_fail.loadm(example_model_fail)
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail.pop("reactions")
            mbmodel_fail.loadm(example_model_fail)
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail.pop("params")
            mbmodel_fail.loadm(example_model_fail)
        # pass incorrect kind of values for that keys
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail["species"] = ["A", "B", "C"]
            mbmodel_fail.loadm(example_model_fail)
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail["reactions"] = (1, 2, 3, 4, 5)
            mbmodel_fail.loadm(example_model_fail)
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            example_model_fail["params"] = "abcdefg"
            mbmodel_fail.loadm(example_model_fail)
        # test with a model with repeated ids
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            # get a new set of parameters where one of ids is repeated with specs
            example_model_fail["params"] = {
                "spec1": {"name": "koff", "val": 0.2},
                "param2": {"name": "kon", "val": 10000000.0},
            }
            mbmodel_fail.loadm(example_model_fail)

    def test_todict(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertEqual(mbmodel.todict(), self.example_mbmodel_wnode)

    def test_tojson(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertEqual(mbmodel.tojson(), self.example_json)

    def test_tosimpleSbml(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertIsInstance(
            mbmodel.tosimpleSbml(), simplesbml.simplesbml.SbmlModel
        )
        # try passing in a model where a species name is preceeded by $
        # and check that output of the model appears as fixed
        mod_model = self.example_mbmodel.copy()
        mod_model["species"] = {
            "spec1": {"name": "$E", "amt": 5e-21, "fixed": False},
            "spec2": {"name": "S", "amt": 1e-20, "fixed": False},
            "spec3": {"name": "ES", "amt": 0.0, "fixed": False},
            "spec4": {"name": "P", "amt": 0.0, "fixed": False},
        }
        mbmodel.loadm(mod_model)
        # model should have one boundary condition if this is the case
        self.assertIn('boundaryCondition="true"', str(mbmodel.tosimpleSbml()))

        # try passing in a model where a species name is NOT preceeded by $
        # but fixed is set to true, sbml should get it
        mod_model = self.example_mbmodel.copy()
        mod_model["species"] = {
            "spec1": {"name": "E", "amt": 5e-21, "fixed": True},
            "spec2": {"name": "S", "amt": 1e-20, "fixed": False},
            "spec3": {"name": "ES", "amt": 0.0, "fixed": False},
            "spec4": {"name": "P", "amt": 0.0, "fixed": False},
        }
        mbmodel.loadm(mod_model)
        # model should have one boundary condition if this is the case
        self.assertIn('boundaryCondition="true"', str(mbmodel.tosimpleSbml()))

    def test_toSBMLstr(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertIn("<?xml", mbmodel.toSBMLstr())
        self.assertIn("<sbml", mbmodel.toSBMLstr())
        self.assertIn("</sbml>", mbmodel.toSBMLstr())

    def test_tosimpleSbmlWriteup(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # we delete \n and spaces to avoid formatting causing issues
        self.assertEqual(
            str(mbmodel.tosimpleSbmlWriteup()).replace('\n','').replace(' ',''),
            self.example_simpleSbmlWriteup.replace('\n','').replace(' ','')
        )

    def test_toAntimony(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertEqual(mbmodel.toAntimony(), self.example_antimony)

    def test_toGraph(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        self.assertEqual(mbmodel.toGraph(), self.example_graph)
        # check error if node_to_id contains an id that is not defined
        with self.assertRaises(ValueError):
            example_model_fail = self.example_mbmodel.copy()
            # get a new set of parameters where one of ids is repeated with specs
            example_model_fail["node_to_id"] = {
                1: "spec1",
                2: "undefinednode",
                3: "spec3",
                4: "spec4",
                5: "reac1",
                6: "reac2",
            }
            mbmodel.loadm(example_model_fail)
            # this should raise the error
            mbmodel.toGraph()

    def test_check_nodes(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # check new graph with previous model
        new_spec, del_spec = mbmodel.check_nodes(self.example_updated_graph)
        # make sure thos values match with expected representation
        self.assertEqual(new_spec, {'species': [7], 'reactions': [8]})
        self.assertEqual(del_spec, {'species': [2], 'reactions': [6]})
        
    def test_get_new_id(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # check if new ids are +1 of the ones in actual model
        self.assertEqual(mbmodel.get_new_id('species'), 'spec5')
        self.assertEqual(mbmodel.get_new_id('reactions'), 'reac3')
        self.assertEqual(mbmodel.get_new_id('params'), 'param4')

    def test_init_spec(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        new_spec = mbmodel.init_spec('A',100, False)
        self.assertEqual(new_spec['name'], 'A')
        self.assertEqual(new_spec['amt'], 100)
        self.assertEqual(new_spec['fixed'], False)
        # if new species name starts with $, should get fixed=True even if
        # false is passed and also check if passing float amount of amt is ok
        new_spec = mbmodel.init_spec('$Abcd',0.002, False)
        self.assertEqual(new_spec['name'], '$Abcd')
        self.assertEqual(new_spec['amt'], 0.002)
        self.assertEqual(new_spec['fixed'], True)
        # try species with integer as name
        new_spec = mbmodel.init_spec(42,0.002, False)
        self.assertEqual(new_spec['name'], '42')
        # check if function raises TypeError if any component has incorrect type
        with self.assertRaises(TypeError):
            mbmodel.init_spec({'str':'fail','aliens':42},2e3, False)

        with self.assertRaises(TypeError):
            mbmodel.init_spec('A','Incorrect', False)

        with self.assertRaises(TypeError):
            mbmodel.init_spec('$A',2e3, 2332)
        
    def test_init_reac(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        new_reac = mbmodel.init_reac('R3',['ES','S'], ['I'], 'ES+kon*S')
        self.assertEqual(new_reac['name'], 'R3')
        self.assertEqual(new_reac['reagents'], ['ES','S'])
        self.assertEqual(new_reac['products'], ['I'])
        self.assertEqual(new_reac['expression'], 'ES+kon*S')
        # try reaction with integer as name
        new_reac = mbmodel.init_reac(4,['ES','S'], ['I'], 'ES+kon*S')
        self.assertEqual(new_reac['name'], '4')
        # try passing incorrect types
        with self.assertRaises(TypeError):
            mbmodel.init_reac({'str':'fail','aliens':42},['ES','S'], ['I'], 'ES+kon*S')
        with self.assertRaises(TypeError):
            mbmodel.init_reac('R3',34, ['I'], 'ES+kon*S')
        with self.assertRaises(TypeError):
            mbmodel.init_reac('R3',['ES','S'], 42, 'ES+kon*S')
        with self.assertRaises(TypeError):
            mbmodel.init_reac('R3',['ES','S'], ['I'], ['str','aliens',42])

    def test_init_param(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        new_reac = mbmodel.init_param('R3',23)
        self.assertEqual(new_reac['name'], 'R3')
        self.assertEqual(new_reac['val'], 23)
        # try reaction with integer as name
        new_reac = mbmodel.init_param(42,23)
        self.assertEqual(new_reac['name'], '42')
        # try passing incorrect types
        with self.assertRaises(TypeError):
            mbmodel.init_param(['not','correct'],23)
        with self.assertRaises(TypeError):
            mbmodel.init_param('R3','stringvalue')

    def test_update_expr(self):
        updated_expr = MolybdenumModel().update_expr('A*kon + C*2', 'A', 'B')
        # do not look at spacing, which could change or not
        self.assertEqual(updated_expr.replace(' ',''), 'B*kon+C*2')
        updated_expr = MolybdenumModel().update_expr('A*kon + C*2', 'kon', 'koff')
        self.assertEqual(updated_expr.replace(' ',''), 'A*koff+C*2')

    def test_update_name_byid(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # change node ID number 2, which corresponds to spec2 and is named S to Subs
        mbmodel.update_name_byid(2, 'Subs')
        self.assertEqual(mbmodel.species[mbmodel.node_to_id[2]]['name'], 'Subs')
        # check if it also has updated the reaction where this is used
        self.assertEqual(mbmodel.reactions['reac1']['expression'], '(kon*E*Subs-koff*ES)')
        # this is not in charge of updating reagents and products, since they are re-built every time there is a change
        # self.assertEqual(mbmodel.reactions['reac1']['reagents'], ['E','Subs'])

        # now try checking a reaction
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # change node ID number 5, which corresponds to reac1 and is named veq to EQ
        mbmodel.update_name_byid(5, 'EQ')
        self.assertEqual(mbmodel.reactions[mbmodel.node_to_id[5]]['name'], 'EQ')
        
        # try passing a node_id not in the representation and get error
        with self.assertRaises(ValueError):
            mbmodel.update_name_byid(25, 'Subs')

    def test_add_connection(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # add species P as reagent of reac1
        mbmodel.add_connection(4,5)
        self.assertEqual(mbmodel.reactions[mbmodel.node_to_id[5]]['reagents'], ['E','S','P'])
        # add species S as product of reac2
        mbmodel.add_connection(6,2)
        self.assertEqual(mbmodel.reactions[mbmodel.node_to_id[6]]['products'], ['P','S'])
        # check if we get a warning if tracing connection between two species
        with self.assertWarns(Warning):
            mbmodel.add_connection(1,2)
        # check if we get a warning if tracing connection between two reactions
        with self.assertWarns(Warning):
            mbmodel.add_connection(5,6)
        # check if we get ValueError if tracing connection with an element that is not there
        with self.assertRaises(ValueError):
            mbmodel.add_connection(1,200)
        # check if we get a warning if tracing connection with an element that is not there
        with self.assertRaises(ValueError):
            mbmodel.add_connection(200,2)


    def test_is_float(self):
        self.assertEqual(MolybdenumModel().is_float(1), True)
        self.assertEqual(MolybdenumModel().is_float(1.2), True)
        self.assertEqual(MolybdenumModel().is_float(-1.3), True)
        self.assertEqual(MolybdenumModel().is_float(2e-4), True)
        self.assertEqual(MolybdenumModel().is_float('1'), True)
        self.assertEqual(MolybdenumModel().is_float('1.3'), True)
        self.assertEqual(MolybdenumModel().is_float('ABCD'), False)
        self.assertEqual(MolybdenumModel().is_float(['123']), False)
        self.assertEqual(MolybdenumModel().is_float(['123','132']), False)
        self.assertEqual(MolybdenumModel().is_float({'12':34.5}), False)
        self.assertEqual(MolybdenumModel().is_float(True), False)

    def test_get_reac_params(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # need to compare sorted lists as the set operation in the function
        # sometimes returns parameters in a different order
        self.assertEqual(sorted(mbmodel.get_reac_params()), sorted(['kcat', 'kon', 'koff']))
        
        # test with a model where one parameter is used in multiple reactions
        mbmodel.reactions = {
            "reac1": {
                "name": "veq",
                "reagents": ["E", "S"],
                "products": ["ES"],
                "expression": "(kon*E*S-koff*ES*kcat)"
            },
            "reac2": {
                "name": "vcat",
                "reagents": ["ES"],
                "products": ["P"],
                "expression": "kcat*ES"
            },
        }
        # check that this parameter is only output once
        self.assertEqual(sorted(mbmodel.get_reac_params()), sorted(['kcat', 'kon', 'koff']))

    def test_update_parameters(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        # make sure it does not alter the parameters defined in correct example model
        mbmodel.update_parameters()
        self.assertEqual(mbmodel.params, self.example_param)
        # try adding one parameter and deleting another one in multiple reactions
        mbmodel.reactions = {
            "reac1": {
                "name": "veq",
                "reagents": ["E", "S"],
                "products": ["ES"],
                # "expression": "(kon*E*S-koff*ES*kcat)"
                "expression": "(kon*E*S^h-ES*kcat)"
            },
            "reac2": {
                "name": "vcat",
                "reagents": ["ES"],
                "products": ["P"],
                "expression": "kcat*ES+const"
            },
        }
        # make sure incorporates new parameters and delete unused ones
        mbmodel.update_parameters()
        param_names = [par['name'] for par in mbmodel.params.values()]
        self.assertEqual(sorted(param_names), sorted(['kon', 'kcat', 'const', 'h']))

    def test_update_from_graph(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        mbmodel.update_from_graph(self.example_updated_graph)
        # check if model updated from graph matches with manually curated update
        # we don't check all parameters because there are some that do not change
        self.assertEqual(mbmodel.species.keys(),
            self.example_updated_mbmodel['species'].keys())
        self.assertEqual(mbmodel.reactions.keys(),
            self.example_updated_mbmodel['reactions'].keys())
        self.assertEqual(mbmodel.reactions['reac1']['reagents'],
            self.example_updated_mbmodel['reactions']['reac1']['reagents'])
        self.assertEqual(mbmodel.reactions['reac3']['products'],
            self.example_updated_mbmodel['reactions']['reac3']['products'])

        return None

    def test_update_from_form(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        form_info = [
                        ('spec1_amt',['12.']),
                        ('spec1_fixed',['True']),
                        ('reac1_expression',['2*E+koff*S']),
                        ('param3_val',['500']),
                        ('param3_name',['kinh'])
                    ]
        # check if all parameters that can be updated in a form get proper updates
        mbmodel.update_from_form(form_info)
        self.assertEqual(mbmodel.species['spec1']['amt'], 12)
        self.assertEqual(mbmodel.species['spec1']['fixed'], True)
        self.assertEqual(mbmodel.reactions['reac1']['expression'], '2*E+koff*S')
        self.assertEqual(mbmodel.params['param3']['val'], 500)
        self.assertEqual(mbmodel.params['param3']['name'], 'kinh')

        # check for failure modes
        with self.assertRaises(ValueError):
            mbmodel.update_from_form([("not a tupe")])
        with self.assertRaises(ValueError):
            mbmodel.update_from_form([("invalidnamenoattribute",["2"])])
        with self.assertRaises(ValueError):
            mbmodel.update_from_form([("spec1_amt",["25","13"])])
        # with self.assertRaises(ValueError):
        #     mbmodel.update_from_form([("spec1_unvalidatt",["25"])])
        # with self.assertRaises(TypeError):
        #     mbmodel.update_from_form([("spec1_amt",["invalidtype"])])
        # with self.assertRaises(TypeError):
        #     mbmodel.update_from_form([("reac1_unvalidatt",["25"])])
        # with self.assertRaises(TypeError):
        #     mbmodel.update_from_form([("reac1_expression",[{"error":"err"}])])
        # with self.assertRaises(TypeError):
        #     mbmodel.update_from_form([("param1_unvalidatt",["25"])])
        # with self.assertRaises(TypeError):
        #     mbmodel.update_from_form([("param1_val",{"error":"err"})])

        return None

    def test_update_sim_params(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        correct_form_sim_params = [
            ('sim_start',['12.']),
            ('sim_end',['24.']),
            ('sim_points',['500'])
        ]
        mbmodel.update_sim_params(correct_form_sim_params)
        self.assertEqual(mbmodel.sim_params,
        {'sim_start': 12., 'sim_end': 24.,'sim_points': 500})
        # test multiple failure modes with invalid inputs
        with self.assertRaises(ValueError):
            mbmodel.update_sim_params([
                ('sim_start'),
                ('sim_end',['24.']),
                ('sim_points',['500'])
            ])

        with self.assertRaises(ValueError):
            mbmodel.update_sim_params([
                ('sim_start',['12.','12.2']),
                ('sim_end',['24.']),
                ('sim_points',['500'])
            ])

        with self.assertRaises(ValueError):
            mbmodel.update_sim_params([
                ('sim_start','abcd'),
                ('sim_end',['ddg']),
                ('sim_points',['500'])
            ])

        with self.assertRaises(ValueError):
            mbmodel.update_sim_params([
                ('sim_start','12.'),
                ('sim_end',['24.']),
                ('sim_points',['500.34'])
            ])

        with self.assertRaises(ValueError):
            mbmodel.update_sim_params([
                ('sim_start','12.'),
                ('sim_end',['24.']),
                ('sim_steps',['300'])
            ])


    def test_run(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        temod, results = mbmodel.run()
        # try using one of telluriums methods and check if output is valid
        self.assertEqual(temod.getFloatingSpeciesIds(), ['E', 'S', 'ES', 'P'])
        # could also use other values but since it is numeric it is more complex
        # temod.getRatesOfChange()
        # temod.getFloatingSpeciesConcentrations()
        # check if obtained results have expected dimensions
        self.assertEqual(results.shape, (120, 5))

    def test_te_result_to_df(self):
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        _, results = mbmodel.run()
        df = mbmodel.te_result_to_df(results)
        self.assertEqual(list(df.columns), ['time', 'E', 'S', 'ES', 'P'])
        self.assertEqual(list(df.shape), [120, 5])

    def test_get_plot_as_htmlimage(self):
        # check if beggining of image representing plot beggins with expected value
        mbmodel = MolybdenumModel()
        mbmodel.loadm(self.example_mbmodel)
        temod, _ = mbmodel.run()
        expected_image_start = '<img align="center" src="data:image/png;base64,i\
VBORw0KGgoAAAANSUhEUgAABg4AAARMCAYAAABBImjmAAAAOXRFWHRTb2Z0d2FyZQBNY\
XRwbG90bGliIHZlcnNpb24zLj'
        self.assertEqual(mbmodel.get_plot_as_htmlimage(temod)[:len(expected_image_start)],expected_image_start)     
        return None


if __name__ == "__main__":
    unittest.main()
