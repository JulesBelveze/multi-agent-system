import big_map as bm

f=open("levels/demo-level.lvl", "r")
file = f.readlines()

f2=open("levels/demo-level2.lvl", "r")
file2 = f2.readlines()

print('Map ONE:')
agt1 = bm.big_map()
idx1 = agt1.setup(file,'A')
agt1.calc_cells(idx1[0],idx1[1],verbose=False)
agt1.map_dump()

print('\nMap TWO:')
agt2 = bm.big_map()
idx2 = agt2.setup(file2,'A')
agt2.calc_cells(idx2[0],idx2[1],verbose=False)
agt2.map_dump()





