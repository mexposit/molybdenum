# Molybdenum model builder

[![Coverage Status](https://coveralls.io/repos/github/mexposit/molybdenum/badge.svg)](https://coveralls.io/github/mexposit/molybdenum)
[![Coverage Status](https://coveralls.io/repos/github/mexposit/molybdenum/badge.svg)](https://coveralls.io/github/mexposit/molybdenum)


For heroku:
 1. Create new app
 2. Set app so that it gets updated from github repository
 3. Select automatic updates.
 4. but at this point heroku tries to build a python app, this is a problem!
 5. Go to the terminal and do heroku login
 6. Then go to the github repository in the computer, once inside run
 7. heroku stack:set container -a telmb
 8. Now commit and push. Heroku now will understand it is a docker container app and will make use of heroku.yml.
 9. Information obtained from: https://stackoverflow.com/a/60159901


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

For testing:

Had to install pip `install coveralls`

```
....path...telmb$ coverage run -m unittest discover
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
