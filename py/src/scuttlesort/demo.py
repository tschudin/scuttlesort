#!/usr/bin/env python3

# scuttlesort/demo.py
# 2022-05-12 <christian.tschudin@unibas.ch>

# ----------------------------------------------------------------------

if __name__ == '__main__':

    from scuttlesort import Timeline
    import os

    def to_dot(timeline): # generator for graphviz
        yield "digraph {"
        yield "  rankdir=RL;"
        yield "  splines=true;"
        yield "  subgraph dag {"
        yield "    node[shape=Mrecord];"
        for p in timeline.linear:
            yield f'    "{p.name}" [label="{p.name}\\nr={p.rank}"]'
            for c in p.prev:
                yield f'    "{p.name}" -> "{c.name}"'
        yield "  }"
        yield "  subgraph time {"
        yield "    node[shape=plain];"
        yield '   " t" -> " " [dir=back];'
        yield "  }"
        yield("}")


    print('''Demo graph for incremental ScuttleSort:

                .-- F <-- E
               /         /
  X <-- A <-- B <-- D <-'
  ^     ^          /
   \     `--- C <-'
    \ 
     `- Y

  Note that arrows show "Scuttlebutt hash pointers", not
  the "parent before child" arrow (as is usually the case
  in textbook descriptions of topological sort algorithms).
  For example, event A has predecessor X and knows X'
  hash value, hence happened afterwards, depends on X.
''')

    print("commands for creating the timeline array:")
    notify = lambda a,b,c: \
             print("    ", a, f"'{b}' at {c}" if a=='ins' else f" {b}  to {c}")

    timeline = Timeline(notify)   # for scuttlesort

    g = { 'X': [],
          'A': ['X'],
          'D': ['B', 'C'],
          'E': ['D', 'F'],
          'F': ['B'],
          'B': ['A'],
          'Y': ['X'],
          'C': ['A']  }

    for n,a in g.items():
        print("  adding", n)
        timeline.add(n, a)

    print("\ndependency graph was, in input order:")
    for n,a in g.items():
        print("  ", n, a)

    print("\nScuttlesort's timeline (other valid linearizations may exist):")
    print(" ", [nm for nm in timeline])
    print("  note the lexicographic order within the same rank")

    print("\nname  rank  successor(s)")
    for h in timeline.linear:
        print("  ", h.name, ("%5d " % h.rank), [x.name for x in h.succ])

    try:
        with open('dag.dot', 'w') as f:
            for l in to_dot(timeline): f.write(l + '\n')
        os.system("dot -Tpdf dag.dot >dag.pdf")
        print("\ngeneration of graphviz files: see dag.dot, dag.pdf")
    except:
        pass
    
''' Output for ScuttleSort:

commands for creating the timeline array:
  adding X
     ins 'X' at 0
  adding A
     ins 'A' at 1
  adding D
     ins 'D' at 0
  adding E
     ins 'E' at 3
  adding F
     ins 'F' at 1
  adding B
     ins 'B' at 5
     mov  1  to 5
     mov  3  to 5
     mov  0  to 3
  adding Y
     ins 'Y' at 2
  adding C
     ins 'C' at 4

dependency graph was, in input order:
   X []
   A ['X']
   D ['B', 'C']
   E ['D', 'F']
   F ['B']
   B ['A']
   Y ['X']
   C ['A']

Scuttlesort's timeline (other valid linearizations may exist):
  ['X', 'A', 'Y', 'B', 'C', 'D', 'F', 'E']
  note the lexicographic order within the same rank

name  rank  successor(s)
   X     0  ['A', 'Y']
   A     1  ['B', 'C']
   Y     1  []
   B     2  ['F', 'D']
   C     2  ['D']
   D     3  ['E']
   F     3  ['E']
   E     4  []
'''

# eof
