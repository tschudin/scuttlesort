//

// scuttlesort.js
// 2022-05-14 <christian.tschudin@unibas.ch


"use strict"

class Timeline {

    constructor(update_cb) {
        this.linear  = [];
        this.name2p  = {}; // name ~ point_in_time
        this.pending = {}; // cause_name ~ [effect_name]
        this.notify  = update_cb;
        this.cmds    = [];
    }

    _insert(pos, h) {
        this.linear.splice(pos, 0, h);
        if (this.notify)
            this.cmds.push( ['ins', h.name, pos] );
    }

    _move(from, to) {
        let h = this.linear[from];
        this.linear.splice(from, 1);
        this.linear.splice(to, 0, h);
        if (this.notify)
            this.cmds.push( ['mov', from, to] );
    }

    add(nm, after) {
        this.cmds = []; // this is not reentrant: add a lock if necessary
        let n = new ScuttleSortNode(nm, this, after);
        // optimizer: compress the stream of update commands
        //            ins(X,nm), mov X Y, mov Y Z etc --> ins(Z,nm)
        //            mov X Y, mov Y Z etc            --> mov X Z
        if (this.notify) {
            var base = null;
            for (let c of this.cmds) {
                if (base) {
                    if (c[0] == 'mov' && base[2] == c[1]) {
                        base[2] = c[2];
                        continue;
                    }
                    this.notify( base );
                }
                base = c;
            }
            if (base)
                this.notify( base );
        }
    }

    index(nm) {
        return this.name2p[nm].indx;
    }
}

class ScuttleSortNode {

    constructor(name, timeline, after) {
        if (name in timeline.name2p) // can add a name only once, must be unique
            throw new Error("KeyError");
        this.name = name;
        this.prev = after.map( x => { return x; } ); // copy of the causes we depend on
                  // hack alert: these are str/bytes, will be replaced by nodes
        // --- internal fields for insertion algorithm:
        this.cycl = false;  // cycle detection, could be removed for SSB
        this.succ = [];     // my future successors (="outgoing")
        this.vstd = false;  // visited
        this.rank = 0;      // 0 for a start, we will soon know better

        timeline.name2p[name] = this
        for (let i = 0; i < this.prev.length; i++) {
            let c = this.prev[i];
            let p = timeline.name2p[c]
            if (p) {
                p.succ.push(this);
                this.prev[i] = p; // replace str/bytes by respective node
            } else {
                if (!timeline.pending[c])
                    timeline.pending[c] = [];
                let a = timeline.pending[c];
                if (!a.includes(this))
                    a.splice(a.length, 0, this);
            }
        }

        var pos = 0;
        for (let i = 0; i < this.prev.length; i++) {
            let p = this.prev[i];
            if (typeof(p) != "string" && p.indx > pos)
                pos = p.indx;
        }
        for (let i = pos; i < timeline.linear.length; i++)
            timeline.linear[i].indx += 1;
        this.indx = pos;
        timeline._insert(pos, this);

        var no_anchor = true;
        for (let p of this.prev) {
            if (typeof(p) != "string") {
                this.add_edge_to_the_past(timeline, p);
                no_anchor = false;
            }
        }
        if (no_anchor && timeline.linear.length > 1) {
            // there was already at least one feed, hence
            // insert us lexicographically at time t=0
            this._rise(timeline);
        }

        let s = timeline.pending[this.name];
        if (s) {
            for (let e of s) {
                for (let i = 0; i < e.prev.length; i++) {
                    if (e.prev[i] != this.name)
                        continue;
                    e.add_edge_to_the_past(timeline, this);
                    this.succ.push(e);
                    e.prev[i] = this;
                }
            }
            delete timeline.pending[this.name];
        }

        // FIXME: should undo the changes in case of a cycle exception ...
    }

    add_edge_to_the_past(timeline, cause) {
        // insert causality edge (self-to-cause) into topologically sorted graph
        let visited = new Set();
        cause.cycl = true;
        this._visit(cause.rank, visited)
        cause.cycl = false;

        let si = this.indx;
        let ci = cause.indx;
        if (si < ci)
            this._jump(timeline, ci);
        else
            this._rise(timeline)

        let a = Array.from(visited);
        a.sort( (x,y) => { return y.indx - x.indx; });
        for (let v of a) {
            v._rise(timeline); // bubble up towards the future
            v.vstd = false;
        }
    }

    _visit(rnk, visited) { // "affected" wave towards the future
        let out = [[this]];
        while (out.length > 0) {
            let o = out[out.length - 1];
            if (o.length == 0) {
                out.pop();
                continue
            }
            let c = o.pop();
            c.vstd = true;
            visited.add(c);
            if (c.cycl)
                throw new Error('cycle');
            if (c.rank <= (rnk + out.length - 1)) {
                c.rank = rnk + out.length;
                out.push(Array.from(c.succ));
            }
        }
    }

    _jump(timeline, pos) {
        //              this.indx   pos
        //              v           v
        //  before .. | e | f | g | h | ... -> future
        //
        //  after  .. | f | g | h | e | ... -> future
        let si = this.indx
        for (let i = si+1; i < pos+1; i++)
            timeline.linear[i].indx -= 1;
        timeline._move(si, pos);
        this.indx = pos
    }

    _rise(timeline) {
        let len1 = timeline.linear.length - 1;
        let si = this.indx;
        var pos = si
        while (pos < len1 && this.rank > timeline.linear[pos+1].rank)
            pos += 1;
        while (pos < len1 && this.rank == timeline.linear[pos+1].rank
                          && timeline.linear[pos+1].name < this.name)
            pos += 1;
        if (si < pos)
            this._jump(timeline, pos);
    }
}

module.exports = Timeline

// eof
