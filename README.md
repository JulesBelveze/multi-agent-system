<h1> Project description</h1>

<p>The project is partly inspired by the developments in mobile robots for hospital use. Hospitals tend to have a very high number of transportation tasks to be carried out: transportation of beds, medicine, blood samples, medical equipment, food, garbage, mail, etc. Letting robots carry out these transportation tasks can save significantly on hospital staff resources.</p>
<p> The goal of this programming project is to implement a simplified simulation of how a multi-robot system at any hosptial might work. It is essentially a toy version of a real multi-robot system for transportation tasks. Some of the challenges in this project are shared with the challenges of creating a real, physical multi-robot system, but of course there would be many more challenges in creating a physical system. </p>


<h1> Getting started </h1>




<h3>System Requirements</h3>
<br>	- Python 3.7 
<br>	- Java 11.0.2
	
<h3> Running the project </h3>

Parameters:
 	<br>	- [Req] Server.jar 	
 	<br>	- [Req] levelname.lvl 	 
 	<br>	- [Req] client.py[opt] search type
 	<br>	- [opt] -g 				Graphical Interface
 	<br>	- [opt] -t 				Time in milli seconds  


Example command execution: 
```
java -jar server.jar -l levels/SAExample.lvl -c "python client/client.py -rl_simple" -g 150 -t 300
```

<h2> TODO </h2>
<li> Conflict resolution</li>
<li>Agent cooperation </li>
