# A commutative square

Let $A$, $B$, $C$, and $D$ be objects, and let the arrows be morphisms
between them. The square commutes when the two paths from $A$ to $D$ are
equal: $h \circ f = k \circ g$.

The square can be written as display math directly in Markdown:

$$
\begin{array}{ccc}
A & \xrightarrow{\quad f \quad} & B \\
\downarrow{g} & & \downarrow{h} \\
C & \xrightarrow{\quad k \quad} & D
\end{array}
$$

The same notation also works inside a plain HTML `div`:

<div>
$$
\begin{array}{ccc}
A & \xrightarrow{\quad f \quad} & B \\
\downarrow{g} & & \downarrow{h} \\
C & \xrightarrow{\quad k \quad} & D
\end{array}
$$
</div>
