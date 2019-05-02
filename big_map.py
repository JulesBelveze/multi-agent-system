import numpy as np
import sys

class big_map():
#Backwards Induction Gradient Decent Map (Big Map)
#Dest_map: level with destination and location.
	def __init__(self):
		self.grid = []
		val_grid = []

	def setup(self, dest_map, dest):
	#Read map to grid(array)
		for line in dest_map:
			i = 0
			grid_line = []
			for char in line[:-1]:
				grid_line.append(char)
				i =+ 1
			self.grid.append(grid_line)
		#GET Grid Size: Assumes first row to be the longest.
		col_len = len(self.grid)
		grid_wth = len(self.grid[1])
		grid_size = col_len * grid_wth
		#SET Val grid size
		self.val_grid = np.arange(grid_size).reshape(col_len,grid_wth)
		self.val_grid.fill(0000)
	#Description: Finds grid destination coordinates and preps val_grid
	#dest: [str] of destination. Fx. 'A'
	#Return: v = vertical index, h = horizontal index
		i,v,h = 0,0,0
		while True:
			if dest in self.grid[i]: 
				v = i
				h = self.grid[i].index(dest)
				break
			i += 1
		self.val_grid[v][h] = 1000
		return v,h 

	# Surrounding cells
	def calc_cells(self,v,h,verbose=False):
		u = v - 1
		d = v + 1
		l = h - 1
		r = h + 1
		uh = False 
		dh = False
		vr = False
		vl = False

		if self.val_grid[v][h] != 0:
			if self.grid[u][h] == ' ':	
				self.val_grid[u][h] = self.val_grid[v][h] * 0.999
				self.grid[u][h] = '#'
				if verbose == True: print("up", u, h)
				uh = True
			if self.grid[d][h] == ' ':
				self.val_grid[d][h] = self.val_grid[v][h] * 0.999
				self.grid[d][h] = '#'
				if verbose == True: print("down", d, h)
				dh = True
			if self.grid[v][r] == ' ':
				self.val_grid[v][r] = self.val_grid[v][h] * 0.999
				self.grid[v][r] = '#'
				if verbose == True: print("right", v, r)
				vr = True
			if self.grid[v][l] == ' ':
				self.val_grid[v][l] = self.val_grid[v][h] * 0.999
				self.grid[v][l] = '#'
				if verbose == True: print("left", v, l)
				vl = True
			if verbose == True: print('up:',uh,'Down:',dh, 'left:',vl,'Right:',vr)
			if uh == True: 
				self.calc_cells(u,h,verbose)
				uh = False
			if dh == True:
				self.calc_cells(d,h,verbose)
				dh = False
			if vr == True:
				self.calc_cells(v,r,verbose)
				vr = False
			if vl == True:
				self.calc_cells(v,l,verbose)
				vl = False

	def map_dump(self):
		print(self.val_grid)
		for line in self.grid:
			print(line)





