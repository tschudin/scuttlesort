// 

// scuttlesort/demo.js
// 2022-05-14 <christian.tschudin@unibas.ch


"use strict"

const Timeline = require("scuttlesort")

let g = {
    'X': [],
    'A': ['X'],
    'D': ['B', 'C'],
    'E': ['D', 'F'],
    'F': ['B'],
    'B': ['A'],
    'Y': ['X'],
    'C': ['A']
};

let timeline = new Timeline( (x) => { console.log(x); } );

for (let n in g)
    timeline.add(n, g[n]);

for (let e of timeline.linear)
    console.log(e.indx, e.name, e.rank,
                e.succ.map( x => {return x.name;} ) );


/*

  Demo graph for incremental ScuttleSort:

                .-- F <-- E
               /         /
  X <-- A <-- B <-- D <-'
  ^     ^          /
   \     `--- C <-'
    \ 
     `- Y

  after sort, we get: {X}{A}{B,C}{D,F}{E,Y}, or
                      {X}{A,Y}{B,C}{D,F}{E}, etc

  from Python run:

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

*/

// eof
