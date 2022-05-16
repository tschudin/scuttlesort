// 

// scuttlesort/demo.js
// 2022-05-14 <christian.tschudin@unibas.ch


"use strict"

const Timeline = require("scuttlesort")

let g = {
    'X': [],
    'A': ['X'],
    'F': ['B'],
    'E': ['D', 'F'],
    'B': ['A'],
    'Y': ['X'],
    'D': ['B', 'C'],
    'C': ['A']
};

let timeline = new Timeline( (x) => { console.log(" ", x); } );

for (let n in g) {
    console.log("// when adding", n);
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

// when adding X
  [ 'ins', 'X', 0 ]
// when adding A
  [ 'ins', 'A', 1 ]
// when adding F
  [ 'ins', 'F', 0 ]
// when adding E
  [ 'ins', 'E', 3 ]
// when adding B
  [ 'ins', 'B', 4 ]
  [ 'mov', 0, 4 ]
  [ 'mov', 2, 4 ]
// when adding Y
  [ 'ins', 'Y', 2 ]
// when adding D
  [ 'ins', 'D', 4 ]
// when adding C
  [ 'ins', 'C', 4 ]

Resulting timeline: (pos, name, rank, successors)
  0 X 0 [ 'A', 'Y' ]
  1 A 1 [ 'B', 'C' ]
  2 Y 1 []
  3 B 2 [ 'F', 'D' ]
  4 C 2 [ 'D' ]
  5 D 3 [ 'E' ]
  6 F 3 [ 'E' ]
  7 E 4 []

 */

// eof
