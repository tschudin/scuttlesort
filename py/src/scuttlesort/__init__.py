
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
            self.cmds.append( ('ins', pos, h.name) )

    def _move(self, old, new):
        h = self.linear[old]
        del self.linear[old]
        self.linear.insert(new, h)
        if self.notify:
            self.cmds.append( ('mov', old, new) )

    def add(self, nm, after=[]):
        print("add", nm, after)
        self.cmds = []
        SCUTTLESORT_NODE(nm, self, after)
        # optimizer: compress the stream of update commands
        #            ins(nm,X), mov X Y, mov Y Z --> ins(nm,Z)
        if self.notify:
            ins = None
            for c in self.cmds:
                if ins != None:
                    if c[0] == 'mov' and ins[0] == c[1]:
                        ins[0] = c[2]
                        continue
                    self.notify('ins', ins[0], ins[1])
                    ins = None
                if c[0] == 'ins':
                    ins = list(c[1:])
                else:
                    self.notify(*c)
            if ins != None:
                self.notify('ins', ins[0], ins[1])
        # another target could be:  mov X Y, mov Y Z -> mov X Z
                

    def index(self, name): # return rank (logical time) of an event
        return self.name2p[name].indx
        # return self.linear.index(self.name2p[name])


class SCUTTLESORT_NODE: # push updates towards the future, "genesis" has rank 0

    def __init__(self, name, timeline, after=[]):
        if name in timeline.name2p: # can add a name only once, must be unique
            raise KeyError
        self.name = name
        self.prev = [x for x in after] # copy of the causes we depend on
                    # hack alert: these are str/bytes, will be replaced by nodes
        # internal fields for insertion algorithm:
        self.cycl = False   # cycle detection, could be removed for SSB
        self.succ = []      # my future successors (="outgoing")
        self.vstd = False   # visited
        self.rank = 0       # 0 for a start, we will soon know better

        timeline.name2p[name] = self

        for i in range(len(self.prev)):
            c = self.prev[i]
            if not c in timeline.name2p:
                if not c in timeline.pending:
                    timeline.pending[c] = set()
                timeline.pending[c].add(self)
            else:
                p = timeline.name2p[c]
                p.succ.append(self)
                self.prev[i] = p # replace str/bytes by respective node

        pos = 0
        for p in self.prev:
            if type(p) != str and p.indx > pos:
                pos = p.indx
        for i in range(pos, len(timeline.linear)):
            timeline.linear[i].indx += 1
        self.indx = pos
        timeline._insert(pos, self)

        for p in [x for x in self.prev if type(x) != str]:
            self.add_edge_to_the_past(timeline, p)
        else:
            if len(timeline.linear) > 1: # there was already at least one feed
                self._rise(timeline)     # insert us lexicographically at time t=0

        if self.name in timeline.pending:  # our node was pending
            for e in timeline.pending[self.name]:
                for c in [x for x in e.prev if x == self.name]:
                    e.add_edge_to_the_past(timeline, self)
                    self.succ.append(e)
                    e.prev[e.prev.index(c)] = self # replace str/bytes
            del timeline.pending[self.name]

        # FIXME: we should undo the changes in case of a cycle ...

    def add_edge_to_the_past(self, timeline, cause):
        # insert causality edge (self-to-cause) into topologically sorted graph
        visited = set()
        cause.cycl = True
        self._visit2(cause.rank, visited)
        cause.cycl = False

        si = self.indx # timeline.linear.index(self)
        ci = cause.indx # timeline.linear.index(cause)
        if si < ci:
            self._jump(timeline, ci)
        else:
            self._rise(timeline)

        # for v in sorted(visited, key=lambda x: -timeline.linear.index(x)):
        for v in sorted(visited, key=lambda x: -x.indx):
            v._rise(timeline) # bubble up towards the future
            v.vstd = False

    def _visit(self, rnk, visited): # "affected" wave towards the future
        self.vstd = True
        visited.add(self)
        # if self.cycl:
        #     raise Exception('cycle')
        if self.rank <= rnk:
            self.rank = rnk + 1
            for effect in self.succ: # those referencing us from the future
                effect._visit(self.rank, visited)

    def _visit2(self, rnk, visited): # "affected" wave towards the future
        out = [[self]]
        while len(out) > 0:
            o = out[-1]
            if len(o) == 0:
                out.pop()
                continue
            c = o.pop()
            c.vstd = True
            visited.add(c)
            # if c.cycl:
            #     raise Exception('cycle')
            if c.rank <= rnk + len(out) - 1:
                c.rank = rnk + len(out)
                out.append([x for x in c.succ])

    def _jump(self, timeline, pos):
        #              self.indx   pos
        #              v           v
        #  before .. | e | f | g | h | ... -> future
        #
        #  after  .. | f | g | h | e | ... -> future
        si = self.indx # timeline.linear.index(self)
        for i in range(si+1, pos+1):
            timeline.linear[i].indx -= 1
        timeline._move(si, pos)
        self.indx = pos
        
    def _rise(self, timeline):
        len1 = len(timeline.linear) - 1
        si = self.indx # timeline.linear.index(self)
        pos = si
        while pos < len1 and self.rank > timeline.linear[pos+1].rank:
            pos += 1
        while pos < len1 and self.rank == timeline.linear[pos+1].rank and \
                                        timeline.linear[pos+1].name < self.name:
            pos += 1
        if si < pos:
            self._jump(timeline, pos)

# eof
