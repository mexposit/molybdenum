# Component specifications

## Components

### Model builder canvas GUI
 - Inputs: user specifies species, reactions and connections between them by positioning these elements in the canvas. The format of these elements will be determined by the JS library used in the canvas.
 - Outputs: Internally processes the HTML attributes that represent each of the components and creates a JSON list to represent them (see details in model translator).

### Model builder list editor
 - Inputs: updated dynamically with the species and reactions displayed in the canvas 
 - Outputs: represents these components in a table format, where the attributes of the components can be edited. Those attributes are also reflected in the canvas. The underlying JSON changes to get these attributes in real time.

### Model translator
 - Inputs: gets the JSON representation of the model. For species, JSON contains the name, concentration and a boolean indicating if it is kept fixed or not. For reactions, JSON contains the reagent names, rate law and reaction constants.
 - Outputs: an antimony representation of the model, indicating the reactions with reagents, products and their rate law, and parameters of the model. Ideally, in real time, but initially runs when compiling the model to antimony.

### Simulation parameters editor
 - Inputs: user defined simulation parameters in an html form
 - Outputs: simulation parameters in a python dictionary so that they can be passed as arguments to the tellurium simulation function.

### Simulation runner
 - Inputs: user triggers running the simulation by pressing a “run” button
 - Outputs: tellurium runs the simulation thus populating a results dataframe with the species concentration over time. Running the model also triggers the display of the default species plot. The result dataframe can be downloaded in csv format.

### Result visualization
 - Inputs: user specifies the species to visualize and axis ranges.
 - Outputs: a figure displaying the concentrations over time. Could be done dynamically if the figure is generated with d3.js, but initially will be done with matplotlib figures.


## Interactions

### From GUI model to antimony

The user begins by adding components (species and reactions) via the model builder canvas GUI or list editor. This is accomplished with a click. Each new component prompts the user for a name, but also provides one by default. Since the GUI and the form representation are interconnected, changes in one reflect in the other in real time. Adding components adds more entries in the underlying JSON representation of the model. Javascript is used to parse the connections of the model in JSON format and transfer it to python. There, a function is used to compare the JSON connectivity information from the GUI and update the underlying JSON model representation if appropriate. At the same time, the user can connect species and reactions (species cannot be connected to other species directy) by tracing paths between the nodes. This changes the reagents and products of each reaction. At any time, the user can edit the name of these components as well as their parameters. These updates are done with Javascript and python through JSON files. Parameters like the concentration of each species or the kinetics of each reaction are filled in in a form below the GUI. The information in the form is also parsed in real-time and used to update the underlying JSON model representation. Still need to decide if it is best to initialize parameters like concentrations with defaults or better not to initialize them to make sure the user enters and defines all parameters. At any point of this process, the user can decide to compile the model in antimony and this will trigger the model translator (maybe in a later implementation this will happen in real time). The model translator will parse the information from the model JSON representation and build an antimony string representing the defined model. This representation will be an output in a drop-down of the main HTML page. Additionally, the user can download a file of this model which can be helpful to load in tellurium in another environment.

### Simulating models defined graphically

Starting from the process defined above, the user may decide to run the defined tellurium model in the web platform. For this, the user starts defining simulation parameters in the simulation parameters editor. These parameters are parsed by flask upon model submission. Then, it presses a “run” button that triggers the simulation runner. The simulation runner uses the antimony model representation and model parameters to run the model in tellurium. This populates a results dataframe that is made available from python to HTML and can be downloaded from the main page as CSV. Additionally, the website shows how species concentration changes over time with the default from tellurium, and maybe a later implementation allows the user defining what species to represent through a form.


## Testing

### Model builder canvas GUI

Since the input is a series of HTML elements, it is difficult to test the correct behavior using an automated test. However, the underlying JSON representation is checked using a python script to incorporate new elements (species/reagents) or update the name of the nodes changed in the representation. For this, I am going to test each of this functions with sample inputs and contrast expected vs. received results, and provide some input errors and see if the function raises errors as expected.

### Model builder list editor

Similar to the previous one, I can try doing a smoke test because thinking of an actual test is overly complex.

### Model translator

For testing, provide a test JSON input and check if the produced antimony model matches with the expected result for that JSON file. This test can be deployed with continuous integration.

### Simulation parameters editor

This function will parse some results from an HTML form and get them in a dictionary that can be passed to the model runner. It can be tested by simulating the HTML form and checking if output matches the expected ones.

### Simulation runner

For testing, provide a sample model and parameters and check if the results are close to the expected ones.

### Result visualization

Since the output is visual, the safest way to test is just a smoke test to guarantee that an output plot is produced.


## Preliminary project plan

1. Determine which JS library to use for the drag-and-drop interface. Currently leaning towards the JSPlumb library, but still deciding between v2 and v5 (v2 is older but more complete than v5). Finally decided to go for D3.js library, as the documentation for the other libraries was not as thoroughly as for D3.js and I couldn’t even get a minimal example to work. Also, D3.js provides more flexibility and control.
2. Build a simple interface in HTML+JS with the chosen library to drag-and-drop species and reactions.
3. Keep model characteristics in real time in JSON format that is easy to parse in the python back-end.
4. Integrate this interface with a flask back-end and receive the JSON representation of the model.
5. Use the flask back-end to dynamically generate a form that lets users specify parameters not easily defined in the graph: species concentration and reaction kinetic properties.
6. Parse the data in the form and store it in real time in the JSON file that represents the model.
7. Build an antimony model from the JSON file.
8. Display this antimony model in the main page so that it can be copy-pasted.
9. Add a list option to display the list of objects in the model canvas and allow editing of these components via the list.
10. Add options to specify model simulations in the main page and get them in the python back-end.
11. Add an option to run the model that simulates the model in the back-end.
12. Get the plot generated by tellurium and display it in the main page.
13. Time allowing, the next characteristics in order of priority would be:
        - Let users define which species to represent in the plot
        - Let users view the tellurium code run in the background
        - Introduce support for events
        - Let users edit the tellurium code directly to tailor the simulation results (it would be then as a tellurium background)
        - Let users save or load models in this interface. Saving is easy when running the app in a local mode but becomes too difficult online (users would need to create an account, etc…). Loading models from antimony or external repos is complex because it requires an intelligent way to display the model components graphically.
