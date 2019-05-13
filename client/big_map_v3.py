import numpy as np
import random


class big_map():
#Backwards Induction Gradient Decent Map (Big Map)
#Dest_map: level with destination and location.
	def __init__(self):
		self.grid = []
		val_grid = []
		
	def setup(self, dest_map, dest):
		self.dest = dest
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
			if self.dest in self.grid[i]: 
				v = i
				h = self.grid[i].index(self.dest)
				break
			i += 1
		self.val_grid[v][h] = 1000
		return v,h 

	def smooth_grid(self,value_grid):
		self.value_grid = value_grid
		cur_list = []
		avg_cur = 0
		for (x,y), value in np.ndenumerate(self.value_grid):
			if self.value_grid[x][y] >= 1 and self.value_grid[x][y] != 1000:
				cur_list = []
				avg_cur = 0
				if self.value_grid[x-1][y]>1:
					cur_list.append(self.value_grid[x-1][y])
				if self.value_grid[x+1][y]>1:
					cur_list.append(self.value_grid[x+1][y])
				if self.value_grid[x][y-1]>1:
					cur_list.append(self.value_grid[x][y-1])
				if self.value_grid[x][y+1]>1:
					cur_list.append(self.value_grid[x][y+1])
				if len(cur_list) > 2:
					avg_cur = sum(cur_list)/len(cur_list)
					self.value_grid[x][y] = avg_cur*0.998
				else:
					self.value_grid[x][y] = self.value_grid[x][y]*0.991
				self.val_grid = self.value_grid


	# Surrounding cells
	def calc_cells(self,v,h,verbose=False):
		u = v - 1
		d = v + 1
		l = h - 1
		r = h + 1
		dh,vr,vl,uh = False,False,False,False
		dh_vicinity,vr_vicinity,vl_vicinity,uh_vicinity = [],[],[],[]
		
		if self.grid[u][h] != '+' and self.grid[u][h] != self.dest:	
			#Calculate Empty North Cell (NC)
			if self.val_grid[u-1][h] >= 1:# Cell North of NC
				uh_vicinity.append(self.val_grid[u-1][h])
			if self.val_grid[u+1][h] >= 1:# Cell South of NC
				uh_vicinity.append(self.val_grid[u+1][h])
			if self.val_grid[u][h+1] >= 1:# Cell East of NC
				uh_vicinity.append(self.val_grid[u][h+1])
			if self.val_grid[u][h-1] >= 1:# Cell West of NC
				uh_vicinity.append(self.val_grid[u][h-1])
			uh_avg = sum(uh_vicinity)/len(uh_vicinity)
			if len(uh_vicinity) > 1:
				self.val_grid[u][h] = uh_avg * 0.99
			else:
				self.val_grid[u][h] = self.val_grid[v][h] * 0.99
			self.grid[u][h] = '#'
			if verbose == True: print("up", u, h)
			uh = True

		if self.grid[v][r] == ' ':
			#Calculate Empty East Cell (EC)
			if self.val_grid[v-1][r] >= 1:# Cell North of EC
				vr_vicinity.append(self.val_grid[v-1][r])
			if self.val_grid[v+1][r] >= 1:# Cell South of EC
				vr_vicinity.append(self.val_grid[v+1][r])
			if self.val_grid[v][r+1] >= 1:# Cell East of EC
				vr_vicinity.append(self.val_grid[v][r+1])
			if self.val_grid[v][r-1] >= 1:# Cell West of EC
				vr_vicinity.append(self.val_grid[v][r-1])
			vr_avg = sum(vr_vicinity)/len(vr_vicinity)
			if len(vr_vicinity) > 1:
				self.val_grid[v][r] = vr_avg * 0.99
			else:
				self.val_grid[v][r] = self.val_grid[v][h] * 0.99
			self.grid[v][r] = '#'
			if verbose == True: print("right", v, r)
			vr = True

		if self.grid[d][h] == ' ':
			#Calculate Empty South Cell (SC)
			if self.val_grid[d-1][h] >= 1:# Cell North of SC
				dh_vicinity.append(self.val_grid[d-1][h])
			if self.val_grid[d+1][h] >= 1:# Cell South of SC
				dh_vicinity.append(self.val_grid[d+1][h])
			if self.val_grid[d][h+1] >= 1:# Cell East of SC
				dh_vicinity.append(self.val_grid[d][h+1])
			if self.val_grid[d][h-1] >= 1:# Cell West of SC
				dh_vicinity.append(self.val_grid[d][h-1])
			dh_avg = sum(dh_vicinity)/len(dh_vicinity)
			if len(dh_vicinity) > 1:
				self.val_grid[d][h] = dh_avg * 0.99
			else:
				self.val_grid[d][h] = self.val_grid[v][h] * 0.99
			self.grid[d][h] = '#'
			if verbose == True: print("down", d, h)
			dh = True

		if self.grid[v][l] == ' ':
			#Calculate Empty WEST Cell (WC)
			if self.val_grid[v-1][l] >= 1:# Cell North of WC
				vl_vicinity.append(self.val_grid[v-1][l])
			if self.val_grid[v+1][l] >= 1:# Cell South of WC
				vl_vicinity.append(self.val_grid[v+1][l])
			if self.val_grid[v][l+1] >= 1:# Cell East of WC
				vl_vicinity.append(self.val_grid[v][l+1])
			if self.val_grid[v][l-1] >= 1:# Cell West of WC
				vl_vicinity.append(self.val_grid[v][l-1])
			vl_avg = sum(vl_vicinity)/len(vl_vicinity)
			if len(vl_vicinity) > 1:
				self.val_grid[v][l] = vl_avg * 0.99
			else:
				self.val_grid[v][l] = self.val_grid[v][h] * 0.99
			self.grid[v][l] = '#'
			if verbose == True: print("left", v, l)
			vl = True
		if verbose == True: print('up:',uh,'Down:',dh, 'left:',vl,'Right:',vr)
		if uh == True and vr == True:
			if uh == True: self.calc_cells(u,h,verbose);uh = False
			if vr == True: self.calc_cells(v,r,verbose);vr = False
			if dh == True: self.calc_cells(d,h,verbose);dh = False
			if vl == True: self.calc_cells(v,l,verbose);vl = False
		elif uh == True and vl == True:
			if uh == True: self.calc_cells(u,h,verbose);uh = False
			if vl == True: self.calc_cells(v,l,verbose);vl = False
			if vr == True: self.calc_cells(v,r,verbose);vr = False
			if dh == True: self.calc_cells(d,h,verbose);dh = False
		elif dh == True and vl == True:
			if dh == True: self.calc_cells(d,h,verbose);dh = False
			if vl == True: self.calc_cells(v,l,verbose);vl = False
			if uh == True: self.calc_cells(u,h,verbose);uh = False
			if vr == True: self.calc_cells(v,r,verbose);vr = False
		elif dh == True and vr == True:
			if dh == True: self.calc_cells(d,h,verbose);dh = False
			if vr == True: self.calc_cells(v,r,verbose);vr = False
			if vl == True: self.calc_cells(v,l,verbose);vl = False
			if uh == True: self.calc_cells(u,h,verbose);uh = False
		else:
			if dh == True: self.calc_cells(d,h,verbose);dh = False
			if vr == True: self.calc_cells(v,r,verbose);vr = False
			if vl == True: self.calc_cells(v,l,verbose);vl = False
			if uh == True: self.calc_cells(u,h,verbose);uh = False
		

	def map_dump(self):		
		self.smooth_grid(self.val_grid)
		print(self.val_grid)
		
		#for line in self.grid:
		#	print(line)





