from collections import defaultdict
from node import node
from edge import edge

def get_nodes_and_edges(rows):

 lmdict = defaultdict(list)

 nodes = defaultdict(node)
 for row in rows:
  lmdict[row[2]].append(row[0])
 for row in rows:
  nodeid = int(row[2])
  if nodeid not in nodes.keys():
   nodes[nodeid] = node(row[8], str(row[9])+","+str(row[10]), lmdict[row[2]])

 edges = defaultdict(list)
 for i in range(len(rows)):
  if rows[i][1] != 0:
   e = edge(nodes[rows[i][1]], rows[i][4], rows[i][5], rows[i][6], rows[i][11], nodes[rows[i][2]])
   edges[rows[i][0]].append(e)
 return nodes, edges
