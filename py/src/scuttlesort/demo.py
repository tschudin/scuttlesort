#!/usr/bin/env python3

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
''')

    print("commands for creating the timeline array:")
    notify = lambda a,b,c: \
             print("  ", a, f"'{c}' at {b}" if a=='ins' else f" {b}  to {c}")

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
        print(n)
        timeline.add(n, a)

    print("\ndependency graph was, in input order:")
    for n,a in g.items():
        print("  ", n, a)


    print("\nlinearized DAG:")
    print(" ", [nm for nm in timeline])
    print("  note the lexicographic order within the same rank")
    # would also be valid: {X}{A}{B,C}{D,F}{E,Y} etc

    # if not timeline.classic:
    print("\nname  rank  successor(s)")
    for h in timeline.linear:
        print("  ", h.name, ("%5d " % h.rank), [x.name for x in h.succ])

    print("\ngeneration of graphviz files: dag.dot, dag.pdf")
    with open('dag.dot', 'w') as f:
        for l in to_dot(timeline): f.write(l + '\n')
    os.system("dot -Tpdf dag.dot >dag.pdf")
    
''' Output for ScuttleSort:

commands for creating the timeline array:
  ins 'X' at 0
  ins 'A' at 1
  ins 'D' at 0
  ins 'E' at 3
  ins 'F' at 1
  ins 'B' at 5
  mov  0  to 5
  mov  3  to 5
  mov  0  to 3
  mov  3  to 4
  ins 'Y' at 2
  ins 'C' at 4

linearized DAG:
  ['X', 'A', 'Y', 'B', 'C', 'D', 'F', 'E']
  note the lexicographic order within the same rank

input dependency graph was:
  X []
  A ['X']
  Y ['X']
  B ['A']
  C ['A']
  D ['B', 'C']
  F ['B']
  E ['D', 'F']

name  rank  successor(s)
   X     0  ['A', 'Y']
   A     1  ['B', 'C']
   Y     1  []
   B     2  ['D', 'F']
   C     2  ['D']
   D     3  ['E']
   F     3  ['E']
   E     4  []
'''

# eof
