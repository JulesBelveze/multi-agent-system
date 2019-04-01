System Requirements:
	- Python 3.7
	- Java 11.0.2

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
