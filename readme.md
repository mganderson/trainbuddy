TrainBuddy -  A conversational agent for Slack that helps you get train times
-------
TrainBuddy is a Slack bot that uses API.ai to parse natural language user input and uses the webhook in this repository to fulfill user requests. TrainBuddy responds to inquiries about NJ Transit train times and allows users to save, update and delete account preferences (e.g., favorite stations).

![Two in one - Bot and webapp](/readme_images/readme1.png?raw=true "Two in one - Bot and webapp")

The webhook and companion webapp are built using the Ferris framework (http://ferrisframework.org/) for Python and the Google App Engine.   The Google App Engine's Datastore is used to store/query NJ Transit's General Transit Feed Specification data.

A simple webapp built to demonstrate the reusability of the webhook's code can be found at [http://trainbuddyis322.appspot.com/](http://trainbuddyis322.appspot.com/).

![How it works](/readme_images/readme2.png?raw=true "How it works")

Watch [the demonstration on YouTube](https://www.youtube.com/watch?v=1dA4shmMLR4) or check out the [presentation slide deck](https://docs.google.com/presentation/d/12xVI911ZNIlVRIf7hsaQflDCBAEOhUEZ_SCYsa8LLjk/edit?usp=sharing).

![Stack and implementation](/readme_images/readme3.png?raw=true "Stack and implementation")

**NOTE!** This project is not actively updated with current NJ Transit GTFS data and is for demonstration only.

Questions/comments? Reach me at:

    mga25@njit.edu
 
Licenses
-------

Third-party libraries that are in the packages directory have varying licenses. Please check the license file that is included within each package.

 * Ferris: Apache License, v2
 * WTForms: BSD
 * ProtoPigeon: Apache License v2
 * PyTZ: MIT
 * GData Client Library: Apache License v2
 * Google API Python Client Library: Apache License v2
 * OAuth2 Client: Apache License v2
