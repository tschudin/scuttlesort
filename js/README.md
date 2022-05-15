# ScuttleSort -- Incremental Convergent Topological Sort for Secure Scuttlebutt (SSB)

## Synopsis

ScuttleSort converts SSB's tangled append-only logs into a single
linear sequence. Because this sequence changes as new log entries are
incrementally added, an append-only stream of instructions ('insert'
and 'move' commands) is derived as a side effect that permits to
replicate and update copies of the sequence. ScuttleSort is convergent
which means that the resulting sequence is the same for all receivers
having seen the same set of log entries, regardless of the order in
which they process a new log entry as long as it follows the
append-order.

## Note on the JavaScript Implementation
