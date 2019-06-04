#Standard Libraries
import numpy as np
import copy
import sys; np.set_printoptions(threshold=sys.maxsize)
import collections
import time
from itertools import groupby
from operator import itemgetter
#Custom local Libraries 
sys.path.append('big_map/')
import big_map_v6 as bm
import utility_functions as uf
import detecting as dt
			
### Load level 
file_dir1 = "adjusted_Levels/MA_Corrido_obs.lvl"
init_lvl_c1 = uf.load_level(file_dir1)
init_lvl_c2 = copy.deepcopy(init_lvl_c1)
init_lvl_c3 = copy.deepcopy(init_lvl_c1)
init_lvl_c4 = copy.deepcopy(init_lvl_c1)
init_lvl_c5 = copy.deepcopy(init_lvl_c1)
init_lvl_c6 = copy.deepcopy(init_lvl_c1)
init_lvl_c7 = copy.deepcopy(init_lvl_c1)
init_lvl_c8 = copy.deepcopy(init_lvl_c1)
init_lvl_c9 = copy.deepcopy(init_lvl_c1)
init_lvl_c10= copy.deepcopy(init_lvl_c1)

#agt = "1"
#box = "B"
#connected = dt.has_access(init_lvl_c1,agt,box)



def is_blocking(level,item):
	zip_vic_lvl,zip_vic_idx_h,zip_vic_idx_v = [],[],[]
	blocking = False
	#if item exists in level then it's location is stored
	v_idx = 0
	for row in level:
		h_idx = 0
		for cell in row:
			if cell == item:
				itm_exists = [v_idx,h_idx]
			h_idx = h_idx+1 
		v_idx = v_idx+1 
	if len(itm_exists) == 0:
		return False
	itm_v_idx = itm_exists[0]
	itm_h_idx = itm_exists[1]
	###Defining what is up down left right
	itm_u = itm_v_idx - 1; itm_l = itm_h_idx - 1
	itm_d = itm_v_idx + 1; itm_r = itm_h_idx + 1
	###Getting all surround locations of item 
	#+++ <-Figure 
	#+B+   B is the item... 
	#+++   ...and the +'s are the surrounding elements in list vic_lvl
	vic_lvl = [
		level[itm_u][itm_l],level[itm_u][itm_h_idx],level[itm_u][itm_r],level[itm_v_idx][itm_r],
		level[itm_d][itm_r],level[itm_d][itm_h_idx],level[itm_d][itm_l],level[itm_v_idx][itm_l]]
	vic_idx_h = [[itm_l],[itm_h_idx],[itm_r],[itm_r],[itm_r],[itm_h_idx],[itm_l],[itm_l]]
	vic_idx_v = [[itm_u],[itm_u],[itm_u],[itm_v_idx],[itm_d],[itm_d],[itm_d],[itm_v_idx]]

	vic_lvl_set = set(vic_lvl)	
	#Check if item is surrounded by space: " " 
	if len(vic_lvl_set) == 1 and " " in vic_lvl_set:
		return False
	#Check if item is surrounded by walls: "+"
	if len(vic_lvl_set) == 1 and "+" in vic_lvl_set:
		return False 
	
	#Remove only consequtive dupplicates from lists
	for i, v in enumerate(vic_lvl): 
		if i == 0 or v != vic_lvl[i-1]:
			zip_vic_lvl.append(vic_lvl[i])
			zip_vic_idx_h.append(vic_idx_h[i])
			zip_vic_idx_v.append(vic_idx_v[i])
	vic_size = len(zip_vic_lvl)
	#Remove irrelavant data
	if (vic_size % 2) != 0:	
		zip_vic_lvl.pop(0)
		zip_vic_idx_h.pop(0)
		zip_vic_idx_v.pop(0)
		vic_size = vic_size - 1
	vic_size = vic_size/2
	
	#Checking for these to cases: 
	#+++ !    !
	#+b  ! or ! +b
	#+++ !    !
	if vic_size == 1:return False
	#Remove wall cells from lists
	for i, vic in reversed(list(enumerate(zip_vic_lvl))):
		if vic == "+":zip_vic_idx_h.pop(i);zip_vic_idx_v.pop(i)
	

	print(zip_vic_idx_h)
	print(zip_vic_idx_v)


def map_space(level,space_start_idx):
	box_exists,frontier_v,frontier_h = [],[],[]
	#Check if connected by white space	
	frontier_v = [space_start_idx[0]]
	frontier_h = [space_start_idx[1]]
	i = 0
	while len(frontier_v) != 0:
		i = i + 1
		v_idx = frontier_v[0]
		h_idx = frontier_h[0]
		u = v_idx - 1
		d = v_idx + 1
		l = h_idx - 1
		r = h_idx + 1
		#Check to see if box is there:
		udlr = {level[u][h_idx],level[d][h_idx],level[v_idx][l],level[v_idx][r]}
		if box in udlr:
			return True 
		#Check surrounding cells
		agtsNboxs = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		if level[u][h_idx]!="+" and not level[u][h_idx] in agtsNboxs: level[u][h_idx]=agt; frontier_v.append(u); frontier_h.append(h_idx)
		if level[d][h_idx]!="+" and not level[d][h_idx] in agtsNboxs: level[d][h_idx]=agt; frontier_v.append(d); frontier_h.append(h_idx)
		if level[v_idx][l]!="+" and not level[v_idx][l] in agtsNboxs: level[v_idx][l]=agt; frontier_v.append(v_idx); frontier_h.append(l)
		if level[v_idx][r]!="+" and not level[v_idx][r] in agtsNboxs: level[v_idx][r]=agt; frontier_v.append(v_idx); frontier_h.append(r)
		frontier_v.pop(0)
		frontier_h.pop(0)
	return False


sta3 = time.time()
item = "B"
blocking = is_blocking(init_lvl_c2,item)
end3 = time.time()
print(" Execution Time:", (end3 - sta3))
print("Blocking:", blocking)
##END
















