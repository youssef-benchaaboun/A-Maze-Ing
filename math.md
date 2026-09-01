# Mathematical Proof of Perfect Maze Generation

## Definition of a Perfect Maze

In graph theory, a maze can be represented as an undirected graph:

$$
G = (V, E)
$$

where:

* \(V\) is the set of maze cells.
* \(E\) is the set of open passages between adjacent cells.

For a maze of width \(W\) and height \(H\):

$$
|V| = W \times H
$$

A maze is called **perfect** when its graph forms a **spanning tree** of the underlying grid graph.

Therefore, a perfect maze must satisfy three properties:

1. **Spanning**
   Every cell belongs to the generated maze.

   $$
   V_{\text{maze}} = V
   $$

2. **Connected**
   A path exists between every pair of cells.

3. **Acyclic**
   The maze contains no closed loops or cycles.

An equivalent property of a spanning tree is:

$$
|E| = |V| - 1
$$

provided the graph is connected.

---

## Core Graph-Theory Principle

The proofs for all maze-generation algorithms rely on the following theorem.

> **Tree Growth Theorem**
>
> Start with a graph containing a single vertex.
>
> If, at every step, exactly one previously unvisited vertex is connected to the existing graph using exactly one edge, the graph remains connected and acyclic.
>
> If this process eventually includes every vertex, the resulting graph is a spanning tree.

Formally, suppose at step \(t\):

$$
G_t = (V_t, E_t)
$$

is a tree.

Let:

$$
v \notin V_t
$$

and let \(u \in V_t\).

If we construct:

$$
V_{t+1} = V_t \cup \{v\}
$$

and:

$$
E_{t+1} = E_t \cup \{(u,v)\}
$$

then \(G_{t+1}\) is also a tree.

The new vertex cannot create a cycle because it previously had no connection to the existing tree and receives exactly one new edge.

This invariant is the basis of all three generation algorithms.

---

# 1. `_generate_dfs`

## Depth-First Search Maze Generation

The DFS generator grows the maze recursively from one starting cell.

The important condition is:

```python
if not self.grid[ny][nx].visited:
```

A passage is therefore opened only toward a cell that has never previously been included in the generated maze.

---

## Base Case

Initially, only the starting cell is visited.

$$
V_0 = \{s\}
$$

and:

$$
E_0 = \emptyset
$$

A graph containing one vertex and no edges is trivially:

* connected,
* acyclic.

Therefore:

$$
G_0 = (V_0, E_0)
$$

is a tree.

---

## Inductive Step

Assume that after some number of iterations:

$$
G_t = (V_t, E_t)
$$

is a tree.

DFS examines a neighbor \(v\) of the current cell \(u\).

The algorithm only continues when:

$$
v \notin V_t
$$

because the neighbor must not already be visited.

The passage between the two cells is opened:

$$
E_{t+1}
=
E_t \cup \{(u,v)\}
$$

and the new cell becomes visited:

$$
V_{t+1}
=
V_t \cup \{v\}
$$

The new vertex \(v\) is connected to the existing tree using exactly one edge.

Therefore:

* connectivity is preserved,
* no cycle can be created.

Thus \(G_{t+1}\) is also a tree.

---

## Termination

The grid graph itself is connected.

DFS recursively explores every unvisited neighbor and backtracks whenever the current cell has no remaining unvisited neighbors.

Eventually:

$$
V_{\text{final}} = V
$$

Every maze cell has been visited.

Because the graph is:

* spanning,
* connected,
* acyclic,

the final graph is a spanning tree.

Therefore `_generate_dfs` generates a **perfect maze**.

$$
\boxed{G_{\text{final}} \text{ is a spanning tree}}
$$

---

# 2. `_generate_couple`

## Randomized Prim-Style Generation

The `_generate_couple` algorithm grows a connected region using a collection of candidate edges stored in:

```python
couple_list
```

Each candidate represents a possible connection between a cell already belonging to the maze and one of its neighboring cells.

---

## Base Case

The algorithm begins with:

$$
V_0 = \{(0,0)\}
$$

and:

$$
E_0 = \emptyset
$$

`couple_list` initially contains candidate edges from the starting cell to its valid neighbors.

The initial graph contains one vertex and no edges, so it is a tree.

---

## Inductive Step

Suppose:

$$
G_t = (V_t, E_t)
$$

is currently a tree.

The algorithm removes a candidate edge:

$$
(p_1, p_2)
$$

from `couple_list`.

It then checks whether \(p_2\) has already been visited.

Conceptually:

```python
if not self.grid[y][x].visited:
```

Two cases are possible.

### Case 1 — `p2` is already visited

If:

$$
p_2 \in V_t
$$

the candidate is discarded.

No passage is opened.

Therefore:

$$
G_{t+1} = G_t
$$

and the tree remains unchanged.

---

### Case 2 — `p2` is unvisited

If:

$$
p_2 \notin V_t
$$

the algorithm opens the passage:

$$
E_{t+1}
=
E_t \cup \{(p_1,p_2)\}
$$

and adds the new cell:

$$
V_{t+1}
=
V_t \cup \{p_2\}
$$

Because \(p_2\) was not already part of the tree, connecting it using exactly one edge cannot create a cycle.

The new vertex is also connected to the existing component.

Therefore \(G_{t+1}\) remains a tree.

---

## Frontier Expansion

After adding \(p_2\), candidate edges from \(p_2\) toward its neighboring cells are added to `couple_list`.

The frontier therefore continues expanding through the grid.

---

## Termination

The algorithm stops when:

```python
couple_list
```

becomes empty.

Since the underlying rectangular grid is connected, every cell can eventually be reached through the growing frontier.

Therefore:

$$
V_{\text{final}} = V
$$

The resulting graph is:

* spanning,
* connected,
* acyclic.

Therefore `_generate_couple` generates a **perfect maze**.

$$
\boxed{G_{\text{final}} \text{ is a spanning tree}}
$$

---

# 3. `_generate_walk`

## Random-Walk-Based Generation

The `_generate_walk` algorithm uses sets representing visited and unvisited cells.

Conceptually:

$$
V = V_{\text{visited}} \cup V_{\text{not visited}}
$$

with:

$$
V_{\text{visited}}
\cap
V_{\text{not visited}}
=
\emptyset
$$

The critical property of this algorithm is that a passage is carved only when the algorithm moves from the current generated structure to a cell that has not yet been visited.

---

## Tree Invariant

Let:

$$
G_t = (V_t, E_t)
$$

represent the currently carved maze.

Whenever the algorithm selects an unvisited neighbor \(v\) from the current cell \(u\), it performs:

$$
V_{t+1}
=
V_t \cup \{v\}
$$

and:

$$
E_{t+1}
=
E_t \cup \{(u,v)\}
$$

The new vertex \(v\) was previously outside the generated maze.

Therefore it is connected to the existing graph using exactly one edge.

By the tree-growth theorem, the graph remains connected and acyclic.

---

## Handling Already Visited Cells

During the random walk, the algorithm may encounter cells that have already been visited.

In that situation, it does **not** carve another passage between already connected vertices.

Instead, the walk continues or selects another previously visited starting position.

This restriction is important because adding an arbitrary edge between two vertices already belonging to a tree could create a cycle.

The algorithm avoids this operation.

Therefore the following invariant is preserved:

> Every carved edge introduces a previously unvisited vertex into the existing tree.

---

## Termination

The outer generation loop continues while unvisited cells remain.

Conceptually:

```python
while not_visited:
```

The algorithm stops only when:

$$
V_{\text{not visited}} = \emptyset
$$

Therefore:

$$
V_{\text{visited}} = V
$$

Every maze cell belongs to the generated graph.

Since every new cell was introduced using exactly one edge, the final graph remains connected and acyclic.

Therefore `_generate_walk` generates a **perfect maze**.

$$
\boxed{G_{\text{final}} \text{ is a spanning tree}}
$$

---
# Proof: `_open_dead_ends()` Cannot Create a Fully Open 3×3 Block

## Goal

We want to prove that opening dead ends cannot create a completely open \(3 \times 3\) area such as:

$$
\begin{matrix}
C_1 & C_2 & C_3 \\
C_4 & C_5 & C_6 \\
C_7 & C_8 & C_9
\end{matrix}
$$

A **fully open \(3 \times 3\) block** means that every passage between adjacent cells inside this block is open.

---

## 1. Wall Count of a Cell

Every maze cell has four possible walls:

$$
N,\ E,\ S,\ W
$$

Let:

$$
w(C)
$$

denote the number of closed walls of a cell \(C\).

Therefore:

$$
0 \leq w(C) \leq 4
$$

A dead end has exactly one open passage.

So:

$$
w(C)=3
$$

because three walls remain closed.

Therefore `_open_dead_ends()` only selects cells satisfying:

$$
\boxed{w(C)=3}
$$

---

## 2. Effect of `_open_dead_ends()`

For every selected dead end, the function removes exactly one additional wall.

Therefore:

$$
w_{\text{after}}(C)
=
w_{\text{before}}(C)-1
$$

Since a selected cell starts with:

$$
w_{\text{before}}(C)=3
$$

we obtain:

$$
w_{\text{after}}(C)=3-1=2
$$

Thus:

$$
\boxed{w_{\text{after}}(C)=2}
$$

for every dead end modified by the function.

So a cell modified exactly once by `_open_dead_ends()` can never become:

$$
w(C)=1
$$

or:

$$
w(C)=0
$$

It can only change from:

$$
3 \longrightarrow 2
$$

---

# 3. Requirements of a Fully Open 3×3 Block

Consider:

$$
\begin{matrix}
C_1 & C_2 & C_3 \\
C_4 & C_5 & C_6 \\
C_7 & C_8 & C_9
\end{matrix}
$$

The cells do not all require the same number of open passages.

There are three types of cells:

* center,
* edge centers,
* corners.

---

## Center Cell \(C_5\)

The center must connect to:

$$
C_2,\ C_4,\ C_6,\ C_8
$$

Therefore all four of its walls must be open.

Its degree inside the block is:

$$
\deg(C_5)=4
$$

and therefore:

$$
w(C_5)=4-\deg(C_5)=0
$$

Hence:

$$
\boxed{w(C_5)=0}
$$

---

## Edge Cells

Consider \(C_2\).

Inside the \(3\times3\) block it must connect to:

$$
C_1,\ C_3,\ C_5
$$

So it must have at least three open passages.

Therefore:

$$
\deg(C_2)\geq3
$$

and:

$$
w(C_2)\leq1
$$

The same applies to:

$$
C_4,\ C_6,\ C_8
$$

Thus:

$$
\boxed{
w(C_2),w(C_4),w(C_6),w(C_8)\leq1
}
$$

---

## Corner Cells

For example, \(C_1\) must connect to:

$$
C_2
$$

and:

$$
C_4
$$

Therefore it needs at least two open passages.

So:

$$
\deg(C_1)\geq2
$$

and:

$$
w(C_1)\leq2
$$

Likewise:

$$
\boxed{
w(C_1),w(C_3),w(C_7),w(C_9)\leq2
}
$$

---

# 4. Required Wall Pattern

Therefore a fully open \(3\times3\) block requires:

$$
\begin{matrix}
\leq2 & \leq1 & \leq2\\
\leq1 & 0 & \leq1\\
\leq2 & \leq1 & \leq2
\end{matrix}
$$

In particular, five cells require fewer than two walls:

$$
C_2,\ C_4,\ C_5,\ C_6,\ C_8
$$

with:

$$
w(C_5)=0
$$

and:

$$
w(C_2),w(C_4),w(C_6),w(C_8)\leq1
$$

---

# 5. Contradiction

Now consider any cell modified by `_open_dead_ends()`.

Before modification:

$$
w_{\text{before}}=3
$$

After removing one wall:

$$
w_{\text{after}}=2
$$

Therefore:

$$
\boxed{w_{\text{after}}\geq2}
$$

But a fully open \(3\times3\) block requires the center to satisfy:

$$
w(C_5)=0
$$

and the four edge-center cells to satisfy:

$$
w(C_i)\leq1
$$

Thus a dead-end transformation:

$$
3\rightarrow2
$$

cannot directly produce any of these required states:

$$
3\rightarrow1
$$

or:

$$
3\rightarrow0
$$

because only one wall is removed.

Formally:

$$
3-1=2
$$

while the required states satisfy:

$$
w\leq1
$$

Therefore:

$$
2>1
$$

which is a contradiction.

---

# 6. Graph-Theory Interpretation

We can also express this using vertex degree.

For a cell:

$$
\deg(C)=4-w(C)
$$

A dead end initially has:

$$
w(C)=3
$$

so:

$$
\deg(C)=1
$$

After opening one wall:

$$
w(C)=2
$$

therefore:

$$
\deg(C)=2
$$

Thus `_open_dead_ends()` performs only the transformation:

$$
\boxed{\deg(C):1\rightarrow2}
$$

But a fully open \(3\times3\) block requires:

### Center

$$
\deg(C_5)=4
$$

### Edge centers

$$
\deg(C_2),
\deg(C_4),
\deg(C_6),
\deg(C_8)
\geq3
$$

The function cannot transform:

$$
1\rightarrow3
$$

or:

$$
1\rightarrow4
$$

because it adds only one new passage.

It can only produce:

$$
1\rightarrow2
$$

---

# 7. Why the Perfect Maze Matters

Before `_open_dead_ends()` runs, the maze is generated as a spanning tree.

Therefore the initial graph:

$$
G=(V,E)
$$

satisfies:

$$
|E|=|V|-1
$$

and contains no cycles.

Opening a dead end adds one extra edge.

This can create a cycle, which is expected when transforming a perfect maze into a non-perfect maze.

However, each selected dead end receives only one additional edge.

So locally:

$$
\deg:1\rightarrow2
$$

The operation may therefore create loops, but it does not turn a dead end directly into a highly connected room-like cell of degree \(3\) or \(4\).

This is the important distinction:

> `_open_dead_ends()` may introduce cycles, but each modified dead end gains only one additional connection.

---

# 8. Important Assumption

This proof depends on the following implementation rule:

> Each selected dead-end cell is modified at most once during `_open_dead_ends()`.

If a cell were allowed to be processed repeatedly, then it could theoretically change as follows:

$$
3\rightarrow2\rightarrow1\rightarrow0
$$

and the proof would no longer hold.

Therefore the implementation must ensure that the function does not repeatedly reopen the same cell after its state changes.

Under this condition:

$$
\boxed{
3\rightarrow2
}
$$

is the maximum modification of any selected dead end.

---

# Conclusion

A dead end begins with:

$$
w=3
$$

and `_open_dead_ends()` removes at most one wall:

$$
3-1=2
$$

Therefore every modified dead end finishes with:

$$
\boxed{w=2}
$$

or equivalently:

$$
\boxed{\deg=2}
$$

A fully open \(3\times3\) block requires:

$$
w(C_5)=0
$$

and:

$$
w(C_2),w(C_4),w(C_6),w(C_8)\leq1
$$

equivalently:

$$
\deg(C_5)=4
$$

and:

$$
\deg(C_2),\deg(C_4),\deg(C_6),\deg(C_8)\geq3
$$

But `_open_dead_ends()` can only perform:

$$
\deg:1\rightarrow2
$$

Therefore, assuming each dead end is processed at most once:

$$
\boxed{
\_open\_dead\_ends()
\text{ cannot by itself turn a processed dead end into the highly connected}
\ 3\text{- or }4\text{-degree cells required by a fully open }3\times3\text{ area.}
}
$$

$$
\blacksquare
$$

