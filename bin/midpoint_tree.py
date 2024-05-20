import sys

from ete4 import Tree

intree = sys.argv[1]

tree = Tree(open(intree))

# Calculate the midpoint node
midpoint = tree.get_midpoint_outgroup()

# Set midpoint as outgroup.
tree.set_outgroup(midpoint)

print(tree.write())
