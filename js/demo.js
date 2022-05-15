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

let timeline = new Timeline( (x) => { console.log(" ", x); } );

for (let n in g) {
    console.log("adding", n);
    timeline.add(n, g[n]);
}

console.log("\nResulting timeline: (pos, name, rank, successors)")
for (let e of timeline.linear)
    console.log(" ", e.indx, e.name, e.rank,
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

  Note that arrows show "Scuttlebutt hash pointers", not
  the "parent before child" arrow (as is usually the case
  in textbook descriptions of topological sort algorithms).
  For example, event A has predecessor X and knows X'
  hash value, hence happened afterwards, depends on X.

  after sort, we get: {X}{A,Y}{B,C}{D,F}{E} (ScuttleSort)
                      {X}{A}{B,C}{D,F}{E,Y} (one among more linearizations)
                       

Expected output:

adding X
  [ 'ins', 'X', 0 ]
adding A
  [ 'ins', 'A', 1 ]
adding D
  [ 'ins', 'D', 0 ]
adding E
  [ 'ins', 'E', 3 ]
adding F
  [ 'ins', 'F', 1 ]
adding B
  [ 'ins', 'B', 5 ]
  [ 'mov', 0, 5 ]
  [ 'mov', 3, 5 ]
  [ 'mov', 0, 4 ]
adding Y
  [ 'ins', 'Y', 2 ]
adding C
  [ 'ins', 'C', 4 ]

Resulting timeline: (pos, name, rank, successors)
  0 X 0 [ 'A', 'Y' ]
  1 A 1 [ 'B', 'C' ]
  2 Y 1 []
  3 B 2 [ 'D', 'F' ]
  4 C 2 [ 'D' ]
  5 D 3 [ 'E' ]
  6 F 3 [ 'E' ]
  7 E 4 []

 */

// eof
