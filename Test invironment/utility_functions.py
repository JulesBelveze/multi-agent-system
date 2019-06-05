import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
	
def prep_heatmap(np_array):
	minval = np.min(np_array[np.nonzero(np_array)]-200)
	maxval = np.max(np_array[np.nonzero(np_array)])
	plt.figure(figsize=(15,12))
	sns.heatmap(np_array, linewidths=.1, annot=True, vmin=minval, vmax=maxval, fmt='g')
	plt.show()

def print_csvmap(np_array):
	np.savetxt("dump.csv", np_array, delimiter=",", fmt='%04d')

def load_level(level_dir):
	f=open(level_dir, "r")
	file = f.readlines()
	init_grid = []
	for line in file:
		i = 0
		grid_line = []
		for char in line[:-1]:
			grid_line.append(char)
			i =+ 1
		init_grid.append(grid_line)
	return init_grid

def find_path(val_grid,v,h):	
		###INSERTION###
		#val_grid: big_map discrete state value array
		#h: horizontal location of agent
		#v: vertical location of agent
		###RETURN###
		# Array[[Vertical Postions],[Horizontal Positions],[Rewards]]

		#initial agent location:
		agt_loc_v = v
		agt_loc_h = h
		val_grid = val_grid
		rewards,path_v,path_h = [],[],[]		
		
		#Start values added to arrays
		rewards.append(val_grid[agt_loc_v][agt_loc_h])
		path_v.append(agt_loc_v)
		path_h.append(agt_loc_h)

		while True:
			up 	  = agt_loc_v - 1
			down  = agt_loc_v + 1
			right = agt_loc_h + 1
			left  = agt_loc_h - 1
			options = []
			options.append(val_grid[agt_loc_v][agt_loc_h])
			options.append(val_grid[up][agt_loc_h])
			options.append(val_grid[down][agt_loc_h])
			options.append(val_grid[agt_loc_v][left])
			options.append(val_grid[agt_loc_v][right]) 
			next_loc = options.index(max(options))

			if next_loc == 0:
				rewards.append(val_grid[agt_loc_v][agt_loc_h])
				agt_loc_v = agt_loc_v
				agt_loc_h = agt_loc_h
				path_v.append(agt_loc_v)
				path_h.append(agt_loc_h)
			
			elif next_loc == 1: 
				rewards.append(val_grid[up][agt_loc_h])
				agt_loc_v = up
				agt_loc_h = agt_loc_h
				path_v.append(agt_loc_v)
				path_h.append(agt_loc_h)
			
			elif next_loc == 2: 
				rewards.append(val_grid[down][agt_loc_h])
				agt_loc_v = down
				agt_loc_h = agt_loc_h
				path_v.append(agt_loc_v)
				path_h.append(agt_loc_h)
			
			elif next_loc == 3: 
				rewards.append(val_grid[agt_loc_v][left])
				agt_loc_v = agt_loc_v
				agt_loc_h = left
				path_v.append(agt_loc_v)
				path_h.append(agt_loc_h)
			
			elif next_loc == 4: 
				rewards.append(val_grid[agt_loc_v][right])
				agt_loc_v = agt_loc_v
				agt_loc_h = right
				path_v.append(agt_loc_v)
				path_h.append(agt_loc_h)
			
			if val_grid[agt_loc_v][agt_loc_h] == np.max(val_grid[np.nonzero(val_grid)]): 
				break
		return path_h, path_v, rewards


def draw_path(path, init_level, view=2):
	#GET Grid Size: Assumes first row to be the longest.
	if view == 1:
		grid_w_path = init_level
	elif view == 2:
		col_len = len(init_level)
		grid_wth = len(init_level[1])
		grid_size = col_len * grid_wth
		#SET Val level_grid size
		grid_w_path = np.arange(grid_size).reshape(col_len,grid_wth)
		grid_w_path.fill(00000)

	while True:
		grid_w_path[path[1][0]][path[0][0]] = path[2][0]
		path[0].pop(0)
		path[1].pop(0)
		path[2].pop(0)
		if len(path[0]) == 0:
			break
	return grid_w_path







