import os, sys

from flask import Flask, render_template, request, jsonify
import numpy as np

from bs4 import BeautifulSoup



# another option would be installing it with pip
# when using in heroku
# sys.path.append("/molybdenum")
# when using locally
#import lmpm
#import lmpm.unirep as unirep
sys.path.append("/")
from molybdenum import MolybdenumModel

app = Flask(__name__)

defaults = {
    'default_spec_conc' : 10,
    'default_spec_fixed' : False,
    'default_reac_revers' : False,
}


# initialize empty molybdenum model
mb_model = MolybdenumModel()

# # initialize a dictionary that will keep all model information
# model_data = model_builder.init_model()
conn_data = {'nodes':[], 'edges':[]}

@app.route("/")
def home():
    # initialize a dictionary that will keep all model information
    # since it is not passed out does not have any effect defining here
    # model_data = model_builder.init_model()
    # print(model_data)
    return render_template("home.html")


#background process triggered when graph has been updated
@app.route('/updated_graph', methods=["GET","POST"])
def updated_graph():
    # conn_data = {'nodes':[],'edges':[]}
    # global conn_data
    if (request.is_json) and (request.method == "POST"):
        data_json = request.get_json()
        conn_data = data_json
    else:
        # got request from javascript that runs everytime screen is touched
        pass
    
    # update model information with updated connection data
    mb_model.update_from_graph(conn_data)
    # pass model dictionary representation to update the form
    model_data = mb_model.todict()
    return render_template("model_form.html", model_data=model_data)

#background process triggered when form has been updated
@app.route('/updated_form', methods=["GET","POST"])
def updated_form():
    # get form as immutablemultidict
    form_data = request.form
    # convert it to a list of tuples (name, value) for each element
    form_lists = (list(form_data.lists()))
    # update background model
    try:
        mb_model.update_from_form(form_lists)
    except Exception as e:
        return jsonify(message=str(e)),500

    model_data = mb_model.todict()
    return render_template("model_form.html", model_data=model_data)


#background process triggered to update model representations
@app.route('/update_representation', methods=["GET","POST"])
def update_representation():

    # TODO: Maybe make it so that the user can edit the model
    # The best way to edit the model would be add the writeup of simpleSBML, which makes it very easy, more than others!
    # get model parameter form as immutablemultidict
    # form_data = request.form
    # convert it to a list of tuples (name, value) for each element
    # form_lists = (list(form_data.lists()))
    # update background model
    # try:
        # mb_model.update_from_form(form_lists)
    # except Exception as e:
        # return jsonify(message=str(e)),500
    try:
        antimony_rep = mb_model.toAntimony()
        sbml_rep = mb_model.toSBMLstr()
        molybdenum_rep = mb_model.todict()
        # if compilation of model was successful set success status
        status = 'success'
        error_message = '' # empty error message
        # and keep model representations
        model_reps = (antimony_rep, sbml_rep, molybdenum_rep)
    except Exception as e:
        # if there was a compilation error (because model is not ok)
        status = 'error'
        # keep error message and pass it
        error_message = str(e)
        # fill model representations with an error note
        error_note='Model compilation failed, check errors'
        model_reps = (error_note, error_note, error_note)
        # this generates error in console. We handle error, we don't want error in console
        # return jsonify(message=str(e)),500

    return render_template("form_representation.html", model_reps=model_reps), error_message, status


#background process triggered to update model representations
@app.route('/run_model', methods=["GET","POST"])
def run_model():
    # get simulation parameters as immutablemultidict
    form_data = request.form
    # convert it to a list of tuples (name, value) for each element
    form_lists = (list(form_data.lists()))
    # TODO: check that end is > start, or let antimony raise error if this is the case
    # update background model
    try:
        mb_model.update_sim_params(form_lists)
    except Exception as e:
        return jsonify(message=str(e)),500
    te_model = mb_model.run()
    te_plot_img = mb_model.get_plot_as_htmlimage(te_model)
    # use beautifulsoup to add the class="img-fluid" to the image to make it responsive with bootstrap
    soup = BeautifulSoup(te_plot_img, 'html.parser')
    soup.find("img")['class'] = "img-fluid"
    return str(soup)



# #background process happening without any refreshing
# @app.route('/background_process_test', methods=["GET","POST"])
# def background_process_test():
#     global conn_data
#     print('inside backgrounda nd model is\n', mb_model.todict())
#     if (request.is_json) and (request.method == "POST"):
#         print("Graphical connection request")
#         data_json = request.get_json()
#         conn_data = data_json
#         print(conn_data)
#     else:
#         # got request from javascript that runs everytime screen is touched
#         print("Form update request")

#         # print("{} is {}".format(data_req, type(data_req)))
#         # print("{} is {}".format(data_json, type(data_json)))
#         # data_json2 = json.loads(request.get_json(silent=True, force=True))
#         # print("{} is {}".format(data_json2, type(data_json2)))
#         # print (request.json.keys())

#     # 1. Update underlying dictionary with new connection (use auxiliary function)
#     # 2. Build the form with updated values
#     # (somewhere different, not here, script that runs when form is updated)... update underlying dictionary. 
    
#     # json_data = request.get_json(force=True, silent=True)
#     # a_value = json_data["name"]
#     # print("Hello", data_req)

#     # actually I think this may be more simple: https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page/40964086
#     # if I go for this option I guess I need to figure out how to get the data from the form dinamically to update antimony model dinamically, whereas the other option should be able to do it. Maybe chedk https://www.youtube.com/watch?v=Lzj13QhRhzQ

#     # steps for next day:
#     # figure out if use option above or below
#     # then, create the shared dictonary having all the attributes we need for antimony model, basically see the one above as an example
#     # then, write function to update this dictionary with the json data that we received creating new nodes and connections as appropiate
#     # pass this dictionary to javascript again (or use the other form) to build the form, and keep infromation automatically into the dictionary.
    
#     # run a function that looks at the connection graphs and updates the underlying
#     # dictionary containing all the information with new nodes, connections or others...
#     #then return the dictionary to javascript as a json so that
#     #the other javascript script creates the form, keeping the default values that are stored in dictionary
#     #that other javascript file will call another python function like this one that will keep parsing values
#     # and generating the antimony model in real tim
#     # model_dict = model_builder.init_model()

#     # global model_data
#     # only run it if model has been initialized
#     # if len(conn_data.keys()) != 0:
#         # model_data = model_builder.update_model_connect(model_data, conn_data, defaults)
#     # print(conn_data, model_data)
#     mb_model.update_from_graph(conn_data)
#     model_data = mb_model.todict()
#     return render_template("model_form.html", model_data=model_data)
#     # print ("Hello")
#     # return ("nothing")

@app.route("/predict", methods=["POST"])
def load_seqs():
    """
    This function loads the sequences on the form of the home page and
    generates predictions with the model, passing them to the results page.
    """
    seqs = request.form["seqs"]
    specie = request.form["species"]
    localization = request.form["location"]
    add_feats = request.form.get("add_feat") != None

    try:
        prediction = lmpm.predict_location(
            seqs, specie, localization, add_feats, pred_all=True
        )
    except Exception as e:
        return render_template("input_error.html", error=e)

    return render_template(
        "results.html",
        seqs=seqs,
        pred=prediction,
        prev_species=specie,
        prev_loc=localization,
        prev_add_feats=add_feats,
        tables=[
            prediction.all_predictions.to_html(classes="data", header="true")
        ],
    )


@app.route("/improve", methods=["POST"])
def mutate():
    """
    This function takes the sequences and options from the form in the results
    page and used them to improve the original sequence.
    """
    seqs = request.form["seqs"]
    specie = request.form["species"]
    localization = request.form["location"]
    add_feats = (
        request.form.get("add_feat") != None
    )  # if it is checeked is not empty so get True
    positions = request.form["positions"]

    try:
        mutated_scores, initial_score = lmpm.optimize_sequence(
            seqs,
            specie,
            localization,
            include_dg=add_feats,
            positions=positions,
        )
        plot_f = lmpm.improve_sec.plot_optimization(
            mutated_scores, initial_score, plot_inplace=False, dpi=300
        )
        mut_table = lmpm.top_mutations(mutated_scores, initial_score, 15)
        # help from https://gitlab.com/snippets/1924163 and
        # https://stackoverflow.com/questions/50728328/python-how-to-show-
        # matplotlib-in-flask
        pngImage = io.BytesIO()
        FigureCanvas(plot_f).print_png(pngImage)
        # Encode PNG image to base64 string
        b64plot = str("data:image/png;base64,") + str(
            base64.b64encode(pngImage.getvalue()).decode("utf8")
        )
    except Exception as e:
        return render_template("input_error.html", error=e)

    return render_template(
        "improve.html",
        seqs=seqs,
        specie=specie,
        loc=localization,
        add_feats=add_feats,
        plot=b64plot,
        tables=[mut_table.to_html(classes="data", header="true")],
    )


@app.route("/guide")
def get_guide():
    return render_template("guide.html")


@app.route("/about")
def get_about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    # use this when running in the website (heroku) or as local web app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # instead, comment lines above and uncomment below  if you run it as
    # flask app to debug (specifying port explicity is important for debugging)
    # app.run(debug=True,host='0.0.0.0',port=5000)