import sys
import io
import os

def sim_load_lvl(level_name):
	abs_path = os.path.dirname(__file__)
	rel_path = "../levels/" + level_name + ".lvl"
	file_path = os.path.abspath(os.path.join(abs_path,rel_path))
	
	if os.path.isfile(file_path):
		return open(file_path, 'r', encoding="utf8")
	
	return None

def dump_to_file(dump_var, quit = False):
	abs_path = os.path.dirname(__file__)
	rel_path = "../logs/level_load_dump.txt" 
	file_path = os.path.abspath(os.path.join(abs_path,rel_path))

	f = open(file_path, 'w')
	for line in dump_var:
		f.write(line)
	
	f.close()
	if quit:
		sys.exit(0)