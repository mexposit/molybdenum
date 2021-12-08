# Functional specifications

## Background

Tellurium lets users define a model, simulate it and visualize the results in a few lines of code, which makes it attractive to naive users. At the same time, it offers a set of functionalities within the same framework that are interesting to more advanced users. Nonetheless, building models in Antimony lacks the visual representation that can be extremely helpful for simple models with many interconnected species and that other tools like MATLAB’s Simbiology offer.
I am planning to build a model construction tool based on a drag-and-drop interface that outputs models in Antimony format. The drag and drop interface should allow users to add species to the model, reactions, and connect them. These components should be easy to rename and reconnect / rearrange as appropriate. Additionally, the platform would allow the user to run the models directly in a tellurium back end and analyze its results in the same place. The visual interface should allow the user to visualize the underlying python code used to run the tellurium back-end and even modify it as appropriate.

## User profile

### New tellurium users
 - Who: users who have never modeled systems before and look for a user-friendly way to get started. 
 - Prior knowledge: users may be learning or already know computational systems biology but do not necessarily have any programming experience.  
 - Looking for: a setup that does not require local installation (this package could be deployed online), lets them build models interactively with a visual interface, is simple enough to build, run and analyze a model but offers the possibility to perform more advanced analysis as they keep learning about computational systems biology.
### Initialized tellurium users
 - Who: users who have some experience with the tellurium package and have used it in a programming environment.
 - Prior knowledge: users have at least basic knowledge of python programming and experience with the tellurium package.
 - Looking for: an easier and clearer way to build models as input for tellurium, a way to show these models in a public demonstration (class setting or a conference workshop, for instance), or a way to build and visualize the models and make sure the connections between components agree with what they expected. In a later time, users may be able to import models directly from Biobanks or copy-pasting antimony models and visualize them in this platform.

## Use cases

### Build antimony models via a drag-and-drop GUI

 - Objective: create an antimony model by dragging and dropping species, reactions and connecting them. The antimony model is a string that can be copy-pasted in the programming environment or downloaded as a text file.
 - Expected interactions: the drag-and-drop interface provides enough flexibility to allow the user to start by first entering the reagents and reactions in a canvas and then connecting them or start connecting a few components and adding more complexity as needed. An alternative to the drag-and-drop option is entering the components in the list definition that accompanies the canvas. In this case, users enter new components but then they should take care to position these components in a proper position in the canvas. Characterizing the components can be done once all the elements are present in the canvas/list or during its construction. Species can be given a name, an initial concentration, and a trigger to indicate if the concentration is continuous. Reactions can be given a name, a rate law, and parameters to characterize it. Finally, there is a “compile model in antimony” button that generates an antimony model string. The user can copy-paste this string into their favorite way of using tellurium and use it as input. Support for events may come at a later time.

### Simulate models via the tellurium back-end

 - Objective: simulate and analyze models defined via de drag-and-drop GUI
 - Expected interactions: users start by defining models in the drag-and-drop GUI as described above. Instead of copy-pasting the resulting antimony model into another platform, users also have the option to run the simulations via the website. After defining the model species, reactions and parameters, users define simulation parameters (time to simulate and number of events). This information is passed to tellurium internally to run the model. If there is any error, the error message from tellurium is displayed in the main page. If the model runs successfully, output plots are displayed in the main page. In a later version of the package, it may be possible to adjust the species to visualize in this plot or specify what to plot. In an even later version of the package, it should be possible to view the code run internally by tellurium and modify it in the website to get specific results, which would be of interest to advanced tellurium users.

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
