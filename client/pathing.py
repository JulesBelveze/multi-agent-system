import numpy as np
import heapq
import copy
from message import msg_server_comment

class Path():
    def __init__(self):
        self.val_grid = []
        self.level_grid = []

    def calc_route(self, walls, start_index, end_index, state: 'State'):
        lvl_rows = len(walls)
        lvl_cols = len(walls[0])
        # Setup map
        self.level_grid = copy.deepcopy(walls)
        self.level_grid[end_index[0]][end_index[1]] = True
        for key, boxes in state.boxes.items():
            for box in boxes:
                self.level_grid[box[0]][box[1]] = True

        # Expect other agents to be immovable
        for key, agent in state.agents.items():
            #TODO: Agents can block pathing of box to goal in a narrow tunnel
            self.level_grid[agent[0]][agent[1]] = True

        # Setup value grid
        self.val_grid = np.arange(lvl_rows * lvl_cols).reshape(lvl_rows, lvl_cols)
        self.val_grid.fill(0000)

        # Set value of destination and start cells
        self.val_grid[end_index[0]][end_index[1]] = 1000
        self.val_grid[start_index[0]][start_index[1]] = -1

        # Map cells
        self.calc_cells(end_index[0], end_index[1])

        if self.is_path_found(start_index):
            return self.val_grid
        return None

        # Surrounding cells
    def calc_cells(self,v_index,h_index):
        u = v_index - 1
        d = v_index + 1
        l = h_index - 1
        r = h_index + 1
        dh,vr,vl,uh = False,False,False,False
        dh_vicinity,vr_vicinity,vl_vicinity,uh_vicinity = [],[],[],[]
        
        if self.level_grid[u][h_index] != True:
            #Calculate Empty North Cell (NC)
            if self.val_grid[u-1][h_index] >= 1:# Cell North of NC
                uh_vicinity.append(self.val_grid[u-1][h_index])
            if self.val_grid[u+1][h_index] >= 1:# Cell South of NC
                uh_vicinity.append(self.val_grid[u+1][h_index])
            if self.val_grid[u][h_index+1] >= 1:# Cell East of NC
                uh_vicinity.append(self.val_grid[u][h_index+1])
            if self.val_grid[u][h_index-1] >= 1:# Cell West of NC
                uh_vicinity.append(self.val_grid[u][h_index-1])
            uh_avg = sum(uh_vicinity)/len(uh_vicinity)
            if len(uh_vicinity) > 1:
                self.val_grid[u][h_index] = uh_avg * 0.99
            else:
                self.val_grid[u][h_index] = self.val_grid[v_index][h_index] * 0.99
            self.level_grid[u][h_index] = True
            uh = True

        if self.level_grid[v_index][r] != True: 
            #Calculate Empty East Cell (EC)
            if self.val_grid[v_index-1][r] >= 1:# Cell North of EC
                vr_vicinity.append(self.val_grid[v_index-1][r])
            if self.val_grid[v_index+1][r] >= 1:# Cell South of EC
                vr_vicinity.append(self.val_grid[v_index+1][r])
            if self.val_grid[v_index][r+1] >= 1:# Cell East of EC
                vr_vicinity.append(self.val_grid[v_index][r+1])
            if self.val_grid[v_index][r-1] >= 1:# Cell West of EC
                vr_vicinity.append(self.val_grid[v_index][r-1])
            vr_avg = sum(vr_vicinity)/len(vr_vicinity)
            if len(vr_vicinity) > 1:
                self.val_grid[v_index][r] = vr_avg * 0.99
            else:
                self.val_grid[v_index][r] = self.val_grid[v_index][h_index] * 0.99
            self.level_grid[v_index][r] = True
            vr = True

        if self.level_grid[d][h_index] != True: 
            #Calculate Empty South Cell (SC)
            if self.val_grid[d-1][h_index] >= 1:# Cell North of SC
                dh_vicinity.append(self.val_grid[d-1][h_index])
            if self.val_grid[d+1][h_index] >= 1:# Cell South of SC
                dh_vicinity.append(self.val_grid[d+1][h_index])
            if self.val_grid[d][h_index+1] >= 1:# Cell East of SC
                dh_vicinity.append(self.val_grid[d][h_index+1])
            if self.val_grid[d][h_index-1] >= 1:# Cell West of SC
                dh_vicinity.append(self.val_grid[d][h_index-1])
            dh_avg = sum(dh_vicinity)/len(dh_vicinity)
            if len(dh_vicinity) > 1:
                self.val_grid[d][h_index] = dh_avg * 0.99
            else:
                self.val_grid[d][h_index] = self.val_grid[v_index][h_index] * 0.99
            self.level_grid[d][h_index] = True
            dh = True

        if self.level_grid[v_index][l] != True:
            #Calculate Empty WEST Cell (WC)
            if self.val_grid[v_index-1][l] >= 1:# Cell North of WC
                vl_vicinity.append(self.val_grid[v_index-1][l])
            if self.val_grid[v_index+1][l] >= 1:# Cell South of WC
                vl_vicinity.append(self.val_grid[v_index+1][l])
            if self.val_grid[v_index][l+1] >= 1:# Cell East of WC
                vl_vicinity.append(self.val_grid[v_index][l+1])
            if self.val_grid[v_index][l-1] >= 1:# Cell West of WC
                vl_vicinity.append(self.val_grid[v_index][l-1])
            vl_avg = sum(vl_vicinity)/len(vl_vicinity)
            if len(vl_vicinity) > 1:
                self.val_grid[v_index][l] = vl_avg * 0.99
            else:
                self.val_grid[v_index][l] = self.val_grid[v_index][h_index] * 0.99
            self.level_grid[v_index][l] = True
            vl = True
        if uh == True and vr == True:
            if uh == True: self.calc_cells(u,h_index);uh = False
            if vr == True: self.calc_cells(v_index,r);vr = False
            if dh == True: self.calc_cells(d,h_index);dh = False
            if vl == True: self.calc_cells(v_index,l);vl = False
        elif uh == True and vl == True:
            if uh == True: self.calc_cells(u,h_index,);uh = False
            if vl == True: self.calc_cells(v_index,l,);vl = False
            if vr == True: self.calc_cells(v_index,r,);vr = False
            if dh == True: self.calc_cells(d,h_index,);dh = False
        elif dh == True and vl == True:
            if dh == True: self.calc_cells(d,h_index);dh = False
            if vl == True: self.calc_cells(v_index,l);vl = False
            if uh == True: self.calc_cells(u,h_index);uh = False
            if vr == True: self.calc_cells(v_index,r);vr = False
        elif dh == True and vr == True:
            if dh == True: self.calc_cells(d,h_index);dh = False
            if vr == True: self.calc_cells(v_index,r);vr = False
            if vl == True: self.calc_cells(v_index,l);vl = False
            if uh == True: self.calc_cells(u,h_index);uh = False
        else:
            if dh == True: self.calc_cells(d,h_index);dh = False
            if vr == True: self.calc_cells(v_index,r);vr = False
            if vl == True: self.calc_cells(v_index,l);vl = False
            if uh == True: self.calc_cells(u,h_index);uh = False

    def is_path_found(self, start_index):
        # Check neighbouring cells for values greater than 0, which means path was found
        if self.val_grid[start_index[0] - 1][start_index[1]] != 0:
            return True
        elif self.val_grid[start_index[0] + 1][start_index[1]] != 0:
            return True
        elif self.val_grid[start_index[0]][start_index[1] - 1] != 0:
            return True
        elif self.val_grid[start_index[0]][start_index[1] + 1] != 0:
            return True

        return False

    def print_path(self):
        # Printing to server console doesnt look very nice, it gets confused with new lines
        # Only use this for debugging purposes
        msg_server_comment(self.val_grid)

class Navigate:
    def __init__(self):
        self.unique_count = 0
        self.open = set()
        self.closed = set()
        self.frontier = []
        heapq.heapify(self.frontier)

    def add_to_explored(self, state):
        self.closed.add(state)

    def is_explored(self, state):
        return state in self.closed

    def explored_count(self):
        return len(self.closed)

    def add_to_frontier(self, state, heuristic):
        heapq.heappush(self.frontier, (heuristic, self.unique_count, state))
        self.open.add(state)
        self.unique_count += 1
    
    def get_from_frontier(self):
        leaf = heapq.heappop(self.frontier)[2]
        self.open.remove(leaf)
        return leaf

    def in_frontier(self, state):
        return state in self.open

    def frontier_count(self):
        return len(self.open)

    def h_calculate(self, target_index, path):
        return path[target_index[0]][target_index[1]] * -1