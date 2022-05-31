
# scuttlesort/__init__.py

# incremental consistent topological sort, "secure scuttlebutt style"
# 2022-04-29 <christian.tschudin@unibas.ch

class Timeline:

    def __init__(self, update_callback=None):
        self.linear = []   # linearized DAG
        self.name2p = {}   # name ~ point_in_time
        self.pending = {}  # cause_name ~ [effect_name]
        self.notify = update_callback
        self.cmds = []
        self.tips = set()

    def __len__(self):
        return len(self.linear)

    def __getitem__(self, pos):
        return self.linear[pos].name

    def __iter__(self):
        for h in self.linear:
            yield h.name

    def __reversed__(self):
        for h in reversed(self.linear):
            yield h.name

    def _insert(self, pos, h):
        self.linear.insert(pos, h)
        if self.notify:
            self.cmds.append( ('ins', h.name, pos) )

    def _move(self, old, new):
        h = self.linear[old]
        del self.linear[old]
        self.linear.insert(new, h)
        if self.notify:
            self.cmds.append( ('mov', old, new) )

    def set_notify(self, update_callback=None):
        self.notify = update_callback

    def add(self, nm, after=[]):
        self.cmds = []  # this is not reentrant: add a lock if necessary
        n = SCUTTLESORT_NODE(nm, self, after)
        # optimizer: compress the stream of update commands
        #            ins(X,nm), mov X Y, mov Y Z etc --> ins(Z,nm)
        #            mov X Y, mov Y Z etc            --> mov X Z
        if self.notify:
            base = None
            for c in self.cmds:
                if base != None:
                    if c[0] == 'mov' and base[2] == c[1]:
                        base[2] = c[2]
                        continue
                    self.notify( *base )
                base = list(c)
            if base != None:
                self.notify( *base )
        return n


    def index(self, name): # return rank (logical time) of an event
        return self.name2p[name].indx

    def is_concurrent(self, nm_a, nm_b):
        pa, pb = self.name2p[nm_a], self.name2p[nm_b]
        if pa == pb: return False
        if pa.rank == pb.rank: return True
        if pa.indx > pb.indx:
            pa, pb = pb, pa
        visited = set()
        pending = set()
        pending.add(pa)
        while len(pending) > 0:
            x = pending.pop()
            if x == pb:
                return False
            visited.add(x)
            if x.rank > pb.rank:
                continue
            for s in x.succ:
                if not s in visited:
                    pending.add(s)
        return True

    def get_tips(self):
        return [x.name for x in self.tips]


class SCUTTLESORT_NODE: # push updates towards the future, "genesis" has rank 0

    def __init__(self, name, timeline, after=[]):
        if name in timeline.name2p: # can add a name only once, must be unique
            raise KeyError
        self.name = name
        self.prev = [x for x in after if x != name] # copy the dependencies
                    # hack alert: these are str/bytes, will be replaced by nodes
        # internal fields of sorting algorithm:
        self.cycl = False   # cycle detection (could be removed for SSB)
        self.succ = []      # my future successors (="outgoing")
        self.vstd = False   # visited
        self.rank = 0       # 0 for a start, we will soon know better

        timeline.name2p[name] = self

        for i in range(len(self.prev)):
            c = self.prev[i]
            if not c in timeline.name2p:
                if not c in timeline.pending:
                    timeline.pending[c] = []
                if not self in timeline.pending[c]:
                    timeline.pending[c].append(self)
            else:
                p = timeline.name2p[c]
                p.succ.append(self)
                if p in timeline.tips:
                    timeline.tips.remove(p)
                self.prev[i] = p # replace str/bytes by respective node

        pos = 0
        for p in self.prev:
            if isinstance(p, SCUTTLESORT_NODE) and p.indx > pos:
                pos = p.indx
        for i in range(pos, len(timeline.linear)):
            timeline.linear[i].indx += 1
        self.indx = pos
        timeline._insert(pos, self)

        anchors = [x for x in self.prev if isinstance(x, SCUTTLESORT_NODE)]
        if len(anchors) > 0:
            for p in anchors:
                self.add_edge_to_the_past(timeline, p)
        elif len(timeline.linear) > 1: # there was already at least one feed
            self._rise(timeline)       # insert us lexicographically at time:

        if self.name in timeline.pending:  # our node was pending
            for e in timeline.pending[self.name]:
                for c in [x for x in e.prev if x == self.name]:
                    e.add_edge_to_the_past(timeline, self)
                    self.succ.append(e)
                    if self in timeline.tips:
                        timeline.tips.remove(self)
                    e.prev[e.prev.index(c)] = self # replace str/bytes
            del timeline.pending[self.name]

        if len(self.succ) == 0:
            timeline.tips.add(self)

        # FIXME: we should undo the changes in case of a cycle ...

    def add_edge_to_the_past(self, timeline, cause):
        # insert causality edge (self-to-cause) into topologically sorted graph
        visited = set()
        cause.cycl = True
        self._visit(cause.rank, visited)
        cause.cycl = False

        si = self.indx
        ci = cause.indx
        if si < ci:
            self._jump(timeline, ci)
        else:
            self._rise(timeline)

        for v in sorted(visited, key=lambda x: -x.indx):
            v._rise(timeline) # bubble up towards the future
            v.vstd = False

    def _visit(self, rnk, visited): # "affected" wave towards the future
        out = [[self]]
        while len(out) > 0:
            o = out[-1]
            if len(o) == 0:
                out.pop()
                continue
            c = o.pop()
            c.vstd = True
            visited.add(c)
            if c.cycl:
                raise Exception('cycle')
            if c.rank <= rnk + len(out) - 1:
                c.rank = rnk + len(out)
                out.append([x for x in c.succ])

    def _jump(self, timeline, pos):
        #              self.indx   pos
        #              v           v
        #  before .. | e | f | g | h | ... -> future
        #
        #  after  .. | f | g | h | e | ... -> future
        si = self.indx
        for i in range(si+1, pos+1):
            timeline.linear[i].indx -= 1
        timeline._move(si, pos)
        self.indx = pos
        
    def _rise(self, timeline):
        len1 = len(timeline.linear) - 1
        si = self.indx
        pos = si
        while pos < len1 and self.rank > timeline.linear[pos+1].rank:
            pos += 1
        while pos < len1 and self.rank == timeline.linear[pos+1].rank and \
                                        timeline.linear[pos+1].name < self.name:
            pos += 1
        if si < pos:
            self._jump(timeline, pos)

# eof
