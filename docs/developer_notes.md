## Nodes and commands useful to develop the app

To display in heroku:
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
cd .../app/
flask run
```

Run in docker: uncomment debug mode

```
docker build -t telmb_web .
docker run -d -it -p 5000:5000 --name telmb_image telmb_web

docker exec -ti telmb_image pip freeze

docker run -d -it -p 5000:5000 --mount type=bind,source="$(pwd)"/app,target=/app --name telmb_imagemnt telmb_web

#Alternative to mount both modules and run interactively

docker run -t -p 5000:5000 -v "$(pwd)"/app:/app -v "$(pwd)"/molybdenum:/molybdenum --name telmb_imagemnt telmb_web

#note: changes to files do not update immediately, so you have to cancel the run and re-run the same command
#still, having mounts is helpful because if not, tiny changes would require building the image again
```

For testing:

Had to install pip `install coveralls`

```
# go to main folder that has subfolders with /app, /molybdenum, /docs... this folder is also called molybdenum if you downloaded from github
....path.../molybdenum$ coverage run -m unittest discover
```