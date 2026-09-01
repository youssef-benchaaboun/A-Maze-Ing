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
# Proof: `_open_dead_ends()` Cannot Create an Open 3×3 Area

Assume, for contradiction, that `_open_dead_ends()` creates a completely open \(3 \times 3\) block:

$$
\begin{matrix}
C_1 & C_2 & C_3 \\
C_4 & C_5 & C_6 \\
C_7 & C_8 & C_9
\end{matrix}
$$

A completely open \(3 \times 3\) block requires the center cell \(C_5\) to be connected in all four directions:

$$
C_5 \leftrightarrow C_2,\quad
C_5 \leftrightarrow C_4,\quad
C_5 \leftrightarrow C_6,\quad
C_5 \leftrightarrow C_8
$$

Therefore:

$$
\text{walls}(C_5)=0
$$

However, `_open_dead_ends()` only modifies dead-end cells:

$$
\text{walls}_{before}=3
$$

and removes at most one wall from each such cell:

$$
\text{walls}_{after}
=
\text{walls}_{before}-1
=
3-1
=
2
$$

Thus every cell modified by `_open_dead_ends()` satisfies:

$$
\boxed{\text{walls}_{after}=2}
$$

It therefore cannot transform a dead end into a cell having:

$$
0 \text{ or } 1 \text{ walls}
$$

But a completely open \(3 \times 3\) area requires:

$$
\text{walls}(C_5)=0
$$

and its four edge-center cells require at most:

$$
\text{walls}(C_2),
\text{walls}(C_4),
\text{walls}(C_6),
\text{walls}(C_8)
\leq 1
$$

Hence the required state cannot be produced by opening a single wall of a dead end:

$$
3-1=2 > 1
$$

Therefore:

$$
\boxed{
\_open\_dead\_ends()
\text{ cannot by itself transform a dead-end cell into the}
\ 0\text{- or }1\text{-wall cells required by an open }3\times3\text{ block}
}
$$

$$
\blacksquare
$$
