#!/usr/bin/env node

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


let chains = [
    [ ['F',['B']], ['E',['D','F']] ],
    [ ['X',[]], ['A',['X']], ['B',['A']], ['D',['B','C']] ],
    [ ['C',['A']] ],
    [ ['Y',['X']] ]
];

function interleave(pfx, config, lst) {
    var empty = true;
    for (let i=0; i < config.length; i++) {
        if (config[i].length > 0) {
            let config2 = JSON.parse(JSON.stringify(config));
            let e = config2[i].shift();
            interleave(pfx + e[0], config2, lst);
            empty = false;
        }
    }
    if (empty) {
        lst.push(pfx);
        return;
    }
}

var lst = [];
interleave('', chains, lst);

console.log("\nRunning ScuttleSort for all", lst.length,
            "possible ingestion schedules:\n");
console.log("  ingest");
console.log("   order   resulting (total) ScuttleSort order");
console.log("--------   -----------------------------------")
for (let pfx of lst) {
    let tl2 = new Timeline();
    for (let nm of pfx) {
        tl2.add(nm, g[nm]);
    }
    console.log(pfx, " ", JSON.stringify(tl2.linear.map( x => {return x.name;} )))
}

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

Running ScuttleSort for all 840 possible ingestion schedules:

  ingest
   order   resulting (total) ScuttleSort order
--------   -----------------------------------
FEXABDCY   ["X","A","Y","B","C","D","F","E"]
FEXABDYC   ["X","A","Y","B","C","D","F","E"]
FEXABCDY   ["X","A","Y","B","C","D","F","E"]
FEXABCYD   ["X","A","Y","B","C","D","F","E"]
FEXABYDC   ["X","A","Y","B","C","D","F","E"]
FEXABYCD   ["X","A","Y","B","C","D","F","E"]
...

 */

// eof
