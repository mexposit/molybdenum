import unittest

import sys

sys.path.append("../")
sys.path.append("molybdenum/")

import simplesbml
from molybdenum import MolybdenumModel


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
model.addReaction(reactants=['E', 'S'], products=['ES'], expression='kon * E * S - koff * ES', rxn_id='veq');
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

    ##################################
    ## Test in and output functions ##
    ##################################
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
        self.assertEqual(
            mbmodel.tosimpleSbmlWriteup(), self.example_simpleSbmlWriteup
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


if __name__ == "__main__":
    unittest.main()
