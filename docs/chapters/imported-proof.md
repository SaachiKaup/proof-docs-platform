# Imported LaTeX document

## 1. Introduction



Let $G$ be a group and $A$ a right $G$-module. It is well-known that the second group cohomology $\Hgp2(G;A)$ is in natural correspondence with the group $\E(G;A)$ of (equivalence classes of) extensions of $G$ by $A$. Topologically, it is also known that $\Hgp2(G;A)$ is in natural correspondence with $H^2(BG;A)$, the singular cohomology of $BG$ with local $A$-coefficients. Hence, we obtain a natural correspondence


<span id="eq-classical-deg2"></span>

$$
\E(G;A)\iso H^2(BG;A).\tag{1}
$$


In this project, we construct and study a natural map


$$
\alpha:\E(G;A)\to [BG,(B^2A)_{hG}]_{BG}
$$


which is defined when $G$ and $A$ are topological groups (with mild niceness assumptions) with $G$ acting continuously on $A$, such that $\alpha$ agrees with the classical isomorphism when $G$ and $A$ are discrete. Here, $\E(G;A)$ denotes the group of (equivalence classes of) those extensions of $G$ by $A$ which are also locally trivial principal $A$-bundles. $[BG,(B^2A)_{hG}]_{BG}$ is the group of homotopy classes of sections of the projection $(B^2A)_{hG}\to BG$, where $(B^2A)_{hG}$ denotes the homotopy $G$-orbit space of $B^2A$. When $A$ is discrete, this naturally agrees with singular cohomology with local $A$-coefficients:


$$
[BG,(B^nA)_{hG}]_{BG}\cong H^n(BG;A).
$$



The motivation behind this project is two-fold. First observe that in the classical case, the definition of the map [(1)](#eq-classical-deg2) goes through group cohomology. Working with topological groups forces one to instead use more direct topological insights to construct and study the map, hence providing new topological insight for what initially seems like an algebraic coincidence. Second, the map $\alpha$ can be thought of as assigning to each extension a characteristic class, hence allowing the use of homotopy-theoretic tools in the study of such extensions.

It turns out that $\alpha$ is not a bijection in general **cite thesis examples**,





## 2. Preliminaries on the Milgram--Steenrod construction


Let $G$ be a CW group and let $A$ be an abelian topological group with a continuous right $G$-action via group homomorphisms. All points in Milgram--Steenrod constructions are written in semi-normal form (i.e. $0\leq t_1\leq t_2\leq\dots\leq t_n\leq 1$).



::: proof-ref id="hom-orb" type="lemma"
\label{hom orb}
There is a natural homeomorphism


$$
B(G\ltimes A)\cong (BA)_{hG}.
$$
:::





<div class="proof-details" data-reference-id="hom-orb" markdown="1">

**Proof.** Let $p:G\ltimes A\to G$ be the projection and consider the map $\phi:E(G\ltimes A)\to EA$ given by the formula


<span id="eq-e-semi-dir"></span>

$$
\phi\left(\prod_{i=1}^n(g_i,a_i,t_i)\right)=\left(\prod_{i=1}^n(a_i\cdot(g_{i+1}\dots g_n),t_i)\right).\tag{2}
$$


One checks that $\phi$ is well-defined and $(G\ltimes A)$-equivariant. Hence, $Ep\times \phi:E(G\ltimes A)\to EG\times EA$ is also $(G\ltimes A)$-equivariant, and has a continuous inverse. Taking the quotient by the $(G\ltimes A)$-action yields the desired homeomorphism.

</div>



Henceforth, we will treat the above homeomorphisms $B(G\ltimes A)\cong (BA)_{hG}$ and $E(G\ltimes A)\cong EG\times EA$ as identifications. Note that $(BA)_{hG}\to BG$ is a group bundle with fiber group $BA$; fiber-wise multiplication and inversion are descended from the trivial group bundle $EG\times EA\to EG$ with fiber group $EA$.




## 3. Topological abelian group extensions


Let $G$ be a CW group and let $A$ be an abelian topological group with a continuous right $G$-action via group homomorphisms. 
An extension of $G$ by $A$ is a short exact sequence


$$
\calE: 1\to A \to E \to G \to 1
$$


of groups which is a principal $A$-bundle and respects the action of $G$ on $A$.
Write $\E(G;A)$ for the group (under Baer sums) of equivalence classes of such extensions.

Given $\calE\in\E(G;A)$, we obtain a $G$-equivariant principal $BA$-bundle


$$
BA\to EE/A \to EG.
$$


The underlying principal $(G\ltimes BA)$-bundle yields a class $\alpha(\calE)\in [BG, B(G\ltimes BA)]_{BG}$. By \Cref{hom orb}, this defines a map


$$
\alpha:\E(G;A)\to [BG, (B^2A)_{hG}]_{BG}
$$


Since $(B^2A)_{hG}\to BG$ is an abelian group bundle, $[BG, (B^2A)_{hG}]_{BG}$ is an abelian group and $\alpha$ is a homomorphism. Write $F$ for the forgetful map


$$
\E(G;A)\to\Bun_G(A)
$$


which remembers only the principal $A$-bundle structure underlying an extension.



::: proof-ref id="bundle-str" type="proposition"
\label{bundle str}
$\ker\alpha\subset\ker F$, i.e., $\alpha$ detects the underlying bundle structure of extensions.
:::





<div class="proof-details" data-reference-id="bundle-str" markdown="1">

**Proof.** Let $\calE\in\ker\alpha$. Hence, as a $(G\ltimes BA)$-principal bundle, $EE/A \to BG$ is the push-forward of the universal $G$-bundle along the projection $G\ltimes BA\to G$. Hence, the inclusion $\iota:G\inc G\ltimes BA\inc EE/A$ factors through $EG\inc EE/A$. Since $EG$ is contractible, this shows that $\iota$ is null-homotopic. However, the pull-back of the principal $A$-bundle $EE\to EE/A$ along $\iota$ is $F(\calE)$,[^imported-1] so $\calE\in\ker T$.

</div>



Recall the correspondence $T:\Hc2(G;A)\iso\ker F$, which is the continuous analogue of the classical correspondence between second group cohomology and abelian group extensions for discrete groups. For $f:G^{\wedge2}\to A$ a normalized continuous 2-cocycle, we wish to describe $\alpha T(f)$ explicitly in terms of $f$.



::: proof-ref id="alpha-2" type="theorem"
\label{alpha_2}
The image of $\alpha T(f)$ under the restriction


$$
[BG, (B^2A)_{hG}]_{BG}\to[B_2G, (B^2A)_{hG}]_{BG}
$$


is represented by the formula


$$
\Phi_f:(\vec{g},\vec{t})\mapsto \left((\vec{g},\vec{t}),(f(\vec{g}),\eta_2(\vec{t})\right).
$$
:::



Let $\calE=T(f)$. For the proof of the theorem, we construct a zigzag of continuous group morphisms


<span id="eq-zigzag"></span>



<figure class="tikz-diagram">
<script type="text/tikz" data-tex-packages='{"tikz-cd":"","amssymb":""}'>
\begin{tikzcd}
G & \tilde G \arrow[l, "\pi"'] \arrow[r, "\kappa"] & G\ltimes BA
\end{tikzcd}
</script>
<figcaption>Diagram description needed.</figcaption>
</figure>


(3)

such that the first arrow is a homotopy equivalence and


<span id="eq-bzigzag"></span>



<figure class="tikz-diagram">
<script type="text/tikz" data-tex-packages='{"tikz-cd":"","amssymb":""}'>
\def\calE{\mathcal{E}}
\begin{tikzcd}
BG \arrow[rr, "\alpha(\calE)", bend left] & B\tilde G \arrow[r,"B\kappa"] \arrow[l,"B\pi"'] & B(G\ltimes BA)
\end{tikzcd}
</script>
<figcaption>Diagram description needed.</figcaption>
</figure>


(4)

commutes up to homotopy. Let


$$
\begin{aligned}
A'&=\{(a,(a,1))\mid a\in A\}\subset E\ltimes EA
\end{aligned}
$$


and set


$$
\tilde G=(E\ltimes EA)/A'.
$$


$\pi$ is the projection $\tilde G\to E/A\cong G$. Viewed as a group extension,


$$
1\to EA\to\tilde{G}\to G\to 1
$$


is the push-forward of $\calE$ along $A\inc EA$. Hence,


<span id="eq-tilde-g"></span>

$$
\tilde G\cong G\times EA\tag{5}
$$


as spaces and $\tilde G\to G$ is a homotopy-equivalence. With $A''$ the image of $A\inc E\to \tilde G$ (equivalently, the image of $A\inc EA\to \tilde G$), $\kappa$ is the projection


<span id="eq-second-arrow"></span>

$$
\tilde G\to \tilde G/A''\cong G\ltimes BA.\tag{6}
$$



It remains to see that [(4)](#eq-bzigzag) commutes up to homotopy. For this, we claim that the principal $(G\ltimes BA)$-bundle corresponding to the two maps $B\tilde G\to B(G\ltimes BA)$ are isomorphic. The $(E\ltimes EA)$-action on $EE$ factors through a free $\tilde G$-action, and the composite projection
$EE\to BE\to BG$ induces a homeomorphism $EE/\tilde G\cong BG$, i.e., $EE\to BG$ is a universal $\tilde G$-bundle. $B\pi$ pulls this back to the Milgram--Steenrod model:



::: proof-ref id="shriek-lemma" type="lemma"
\label{shriek lemma}
$B\pi$ lifts to a $\tilde G$-equivariant map $\Pi:E\tilde G\to EE$, i.e., there is a pull-back square


<span id="eq-shriek-eq"></span>



<figure class="tikz-diagram">
<script type="text/tikz" data-tex-packages='{"tikz-cd":"","amssymb":""}'>
\begin{tikzcd}
E\tilde G \arrow[d] \arrow[r, "\Pi", dashed] & EE \arrow[d] \\
B\tilde G \arrow[r, "B\pi"]                  & BG          
\end{tikzcd}
</script>
<figcaption>Diagram description needed.</figcaption>
</figure>


(7)
:::


Factoring out the $A''$ action in [(7)](#eq-shriek-eq) yields a pull-back square




<figure class="tikz-diagram">
<script type="text/tikz" data-tex-packages='{"tikz-cd":"","amssymb":""}'>
\begin{tikzcd}
E\tilde G/A'' \arrow[d] \arrow[r] & EE/A \arrow[d] \\
B\tilde G \arrow[r, "B\pi"]                  & BG          
\end{tikzcd}
</script>
<figcaption>Diagram description needed.</figcaption>
</figure>


of principal $(G\ltimes BA)$-bundles. These principal bundles are $(B\kappa)^\ast E(G\ltimes BA)$ and $\alpha(\calE)^\ast E(G\ltimes BA)$ respectively, so the commutativity of [(4)](#eq-bzigzag) follows.



<div class="proof-details" data-reference-id="shriek-lemma" markdown="1">

**Proof of \Cref{shriek lemma}.**

Treating [(5)](#eq-tilde-g) as an identification, the formula for $\Pi$ is


$$
\Pi:\prod_{i=1}^n(g_i, z_i, t_i)\mapsto\prod_{i=1}^n(g_i,1_{A},t_i)(1_{G},-z_i^{t_i}),
$$


where for $\displaystyle z=\prod_{j=1}^m(a_j,s_j)\in EA$ and $t\in [0,1]$ we write


$$
z^t=\prod_{j=1}^m(a_j,s_jt).
$$


One checks that the formula for $\Pi$ is well-defined and $\tilde G$-equivariant, keeping in mind that the multiplication on $G\times EA$ induced by [(5)](#eq-tilde-g) is given by the formula


<span id="eq-tildeg-mult"></span>

$$
(g_1,z_1)(g_2,z_2)=(g_1g_2,z_1\cdot g_2+z_2-(f(g_1,g_2),1)).\tag{8}
$$


Commutativity of [(7)](#eq-shriek-eq) is clear.

</div>





<div class="proof-details" data-reference-id="alpha-2" markdown="1">

**Proof of \Cref{alpha_2}.**

In light of [(4)](#eq-bzigzag), it suffices to show that $B\kappa|_{B_2\tilde G}$ is homotopic to $\Phi_f\circ B\pi|_{B_2\tilde G}$. Treating [(5)](#eq-tilde-g) as an identification, we have


$$
\begin{aligned}
L:=B\kappa|_{B_2\tilde G}:(\vec{g},\vec{z},\vec{t})&\mapsto((\vec{g},\vec{t}),(z_1\cdot g_2,t_1)(z_2,t_2))\text{ and}\\
R:=\Phi_f\circ B\pi|_{B_2\tilde G}:(\vec{g},\vec{z},\vec{t})&\mapsto ((\vec{g},\vec{t}),(f(\vec g), \eta_2(\vec t))
\end{aligned}
$$


Since $(B^2A)_{hG}\to BG$ is a group-bundle, $L\cdot R^{-1}$ makes sense (using the fiber-wise group structure), and we wish to show that $L\cdot R^{-1}$ is null-homotopic. An explicit null-homotopy $H_s$ with $H_0$ constant and $H_1=L\cdot R^{-1}$ is given as follows.


$$
H_s:(\vec{g},\vec{z},\vec{t})\mapsto L(\vec{g},\vec{z}^{\,s},\vec{t})\cdot ((\vec{g},\vec{t}),(f(\vec g), \eta_2(st_1,t_2))^{-1}.
$$


Some well-definedness checks need to be done. All are trivial, except the case of $t_1=t_2=t$, which is spelt out below. By [(8)](#eq-tildeg-mult), we wish to show that


$$
H_s(\vec{g},\vec{z},\vec{t})=H_s(\vec{g}\,',\vec{z}\,',\vec{t}\,'),
$$


where $\vec{g}\,'=(1_G,g_1g_2)$, $\vec{z}\,'=(0_{BA},z_1\cdot g_2+z_2-(f(g_1,g_2),1))$, and $\vec{t}\,'=(0,t)$. This is easy to see.

</div>





## 4. Essential surjectivity of $\alpha$



Which classes in $[BG,(B^2A)_{hG}]_{BG}$ come from an abelian group extension, i.e., what is the image of $\alpha$? This is a hard question to answer for a general pair $(G,A)$, but it turns out that $\alpha$ is surjective in a coarser sense when $G$ acts trivially on $A$:



::: proof-ref id="imported-theorem-4-1" type="theorem"
\label{imported-theorem-4-1}

There exist CW groups $G'$ and $A'$ which are weakly equivalent to $G$ and $A$ respectively (as spaces) such that $\alpha:\E(G';A')\to H^2(BG';A')$ is surjective.
:::





<div class="proof-details" data-reference-id="imported-theorem-4-1" markdown="1">

**Proof.** Write $\mathbb{G}:\textbf{sSet}_0\to \textbf{sGrp}$ for Kan's loop-group functor and $\bar W:\textbf{sGrp}\to\textbf{sSet}_0$ for its right-adjoint. Let $X\in\textbf{sSet}_0$ be the based singular complex on $BG$ and let $\mathcal{A}\in\textbf{sAb}$ be the singular complex on $A$. **Note that $\bar W$ takes $\textbf{sAb}$ to $\textbf{sAb}$**, so $\bar W^2\mathcal{A}$ makes sense. Also, we know that


- $|X|\simeq BG$ and $|\mathbb{G}X|\simeq \Omega BG\simeq G$, and similarly\\

- $|\mathcal{A}|\simeq A$ and $|\bar W^2\mathcal{A}|\simeq B^2A$.



Pick a class $\zeta\in H^2(BG;A)$, and let **$f:X\to\bar{W}^2\mathcal{A}$ be a simplicial representative**. **The adjoint $\hat{f}:\mathbb{G}X\to\bar{W}\mathcal{A}$ is a simplicial group homomorphism**, so pulling back the simplicial central extension


$$
\mathcal{A}\to W\mathcal{A}\to \bar{W}\mathcal{A}
$$


along $\hat{f}$ gives a simplicial central extension


$$
\mathcal{A}\to \mathcal{E}\to \mathbb{G}X.
$$


Since




<figure class="tikz-diagram">
<script type="text/tikz" data-tex-packages='{"tikz-cd":"","amssymb":""}'>
\begin{tikzcd}
\Omega|X| \arrow[d,"which way"] \arrow[r, "\Omega|f|"] & \Omega|\bar W^2\mathcal{A}| \arrow[d,"which way"] \\
\mathbb{G}X \arrow[r, "\hat{f}"] & \bar W\mathcal{A}                
\end{tikzcd}
</script>
<figcaption>Diagram description needed.</figcaption>
</figure>


**commutes up to homotopy, it follows that taking $G'=|\mathbb{G}X|$ and $A'=|\mathcal{A}|$ works.**

</div>





## References

<span id="bib-admi"></span>

**[1]** Adem, A. \& Milgram, R. J. (2004). Cohomology of Finite Groups (2nd ed.). Springer-Verlag.

<span id="bib-bowa"></span>

**[2]** Borel, A., \& Wallach, N. R. (2000). Continuous Cohomology, Discrete Subgroups, and Representations of Reductive Groups. Amer. Math. Soc.

<span id="bib-br"></span>

**[3]** Brown, R. (2006). Topology and Groupoids, published online at groupoids.org.uk. PDF available at <https://groupoids.org.uk/pdffiles/topgrpds-e.pdf>.

<span id="bib-di"></span>

**[4]** tom Dieck, T. (2008). Algebraic Topology. EMS Textbooks in Math.

<span id="bib-dufo"></span>

**[5]** Dummit, D. S., \& Foote, R. M. (2004). Abstract Algebra (3rd ed.). John Wiley \& Sons.

<span id="bib-eima"></span>

**[6]** Eilenberg, S., \& MacLane, S. (1947). Cohomology Theory in Abstract Groups. I. Annals of Math., 48(1), 51–78. <https://doi.org/10.2307/1969215>

<span id="bib-fuwo"></span>

**[7]** Fuchssteiner, M., \& Wockel, C. (2012). Topological Group Cohomology with Loop Contractible Coefficients. Topology and its App., 159(10-11), 2627-2634. <https://doi.org/10.1016/j.topol.2012.04.006>

<span id="bib-ha"></span>

**[8]** Hatcher, A. (2002). Algebraic Topology. Cambridge Uni. Press. <https://pi.math.cornell.edu/~hatcher/AT/ATpage.html>

<span id="bib-josp"></span>

**[9]** Joshi, R., \& Spallone, S. (2023). Central Extensions and Cohomology. arXiv preprint. arXiv:2307.14658v2. <https://arxiv.org/abs/2307.14658v2>

<span id="bib-mi"></span>

**[10]** Milgram, R. J. (1967). The Bar Construction and Abelian H-spaces. Illinois J. Math., 11(2), 242-250. <https://doi.org/10.1215/ijm/1256054662>

<span id="bib-pisp"></span>

**[11]** Piccinini, R. A., \& Spreafico, M. (1998). The Milgram--Steenrod Construction of Classifying Spaces for Topological Groups. Exposition. Math., 16(2):97–130.

<span id="bib-pu"></span>

**[12]** Puppe, D. (1967). Bemerkungen über die Erweiterung von Homotopien. Archiv der Mathematik, 18, 81-88. <https://doi.org/10.1007/BF01899475>

<span id="bib-a1"></span>

**[13]** Stasheff, J. D. (1963). Homotopy Associativity of H-Spaces. I. Trans. Amer. Math. Soc., 108(2), 275–292. <https://doi.org/10.2307/1993608>

<span id="bib-a2"></span>

**[14]** Stasheff, J. D. (1963). Homotopy Associativity of H-Spaces. II. Trans. Amer. Math. Soc., 108(2), 293–312. <https://doi.org/10.2307/1993609>

<span id="bib-stash"></span>

**[15]** Stasheff, J.D. (1978). Continuous Cohomology of Groups and Classifying Spaces. Bull. Amer. Math. Soc., 84(4), 513-530. <https://www.ams.org/journals/bull/1978-84-04/S0002-9904-1978-14488-7/>

<span id="bib-st"></span>

**[16]** Steenrod, N. E. (1968). Milgram's Classifying Space of a Topological Group. Topology, 7(4), 349-368. <https://core.ac.uk/download/pdf/82066845.pdf>

<span id="bib-strickland"></span>

**[17]** Strickland, N. P. (2009). The Category of CGWH Spaces. preprint. <https://ncatlab.org/nlab/files/StricklandCGHWSpaces.pdf>

<span id="bib-wawo"></span>

**[18]** Wagemann, F., \& Wockel, C. (2015). A Cocycle Model for Topological and Lie Group Cohomology. Trans. Amer. Math. Soc., 367(3), 1871-1909. <https://www.jstor.org/stable/24513021>

<span id="bib-we"></span>

**[19]** Weibel, C. A. (1994). An Introduction to Homological Algebra. Cambridge Uni. Press.

<span id="bib-wi"></span>

**[20]** Wigner, D. (1973). Algebraic Cohomology of Topological Groups. Trans. Amer. Math. Soc., 178, 83-93. <https://egg.epfl.ch/~nmonod/bonn/Wigner_1973.pdf>





[^imported-1]: In fact, the same is true at the level of group extensions by $A$.
