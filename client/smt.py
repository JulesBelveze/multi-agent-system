import sys
import io

def sim_load_lvl(client_level):
	if client_level.endswith('.lvl'):
		url = "../levels/" + client_level 
	else:
		url = "../levels/" + client_level + ".lvl"
		content = open(url, 'r', encoding='utf8')
	return content



'''
Dumps to file but cause all sorts of errors. CAREFUL
def dump_to_file(dump_var, quit=False):
    dump = ''
    f = open("Logs/debug_1.txt", "a")
    while dump_var:
    	dump = dump_var.readline()
    	f.write(dump)
    f.close()
    if quit == True:
    	sys.exit()
    return
'''

