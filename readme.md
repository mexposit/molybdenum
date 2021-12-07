```
# set up environment
conda create -n telmb37 python=3.7.0
pip install --no-cache-dir -compile -r requirements.txt

# for development
pip install jupyterlab


# run for local development
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Run in docker: uncomment debug mode

```
docker build -t telmb_web .
docker run -d -it -p 5000:5000 --name telmb_image telmb_web

docker exec -ti telmb_image pip freeze

docker run -d -it -p 5000:5000 --mount type=bind,source="$(pwd)"/app,target=/app --name telmb_imagemnt telmb_web

Alternative to mount both modules and run interactively

docker run -t -p 5000:5000 -v "$(pwd)"/app:/app -v "$(pwd)"/molybdenum:/molybdenum --name telmb_imagemnt telmb_web
```

Next steps:

 - Functions:
    - graph to mb representation
    - form to mb representation
    - maybe get rid of name and make names become ids?? I kind of like ids but maybe they are unecessary
    
 - implement the module in the web app.
 - fill in the form with species, reactions, parameters... let user change name of species/reactions? I would say no bc we can't update graph! Name could be header of the dropdown/table identifying the specie or reaction. 
 - make it so that if you write reaction expression, new parameters appear where necessary in the form
 - add simulation parameters
 - add button to run and show plot
 - make the text boxes with antimony and simpleSBML models. Let user know they can modify model from there and changes will be reflected in simulation, but the graph will be incorrect (could potentially look how to draw graphs from the connections I have though, and tellurium have a graph representation in fact...)
 - add options to see results, download, antimony model, etc...
