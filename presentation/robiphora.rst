Robiphora
=========
Probabilistic Multi-modal Reference Resolution for Robots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Author: Jack Rosenthal
:Date:   May 9, 2018

.. default-role:: math

Motivation
~~~~~~~~~~

Motivation: Inherital Structures
--------------------------------

Consider this sentence:

    `\underbrace{\text{The house}}_{\text{referent}}` was cold because
    `\underbrace{\text{the window}}_{\text{anaphor}}` was open.

Or this sentence:

    `\underbrace{\text{John}}_{\text{referent}}` was sad since Sally did not
    show up to the movie with `\underbrace{\text{him}}_{\text{anaphor}}`.

What did our resolution of the referent have in common here? An inherital based
system.

Problem Statement
-----------------

Build an algorithm for multi-modal reference resolution which:

* Works on a **well-defined** set of inputs reflecting an inherital structure
* Supports **multiple-inheritance** to allow for ease of definition of the
  structure
* Uses **probabilistic measures** to find the most likely inherital pattern

.. admonition:: Not a part of the problem statement

    Just because Robiphora intends to operate using probabilistic measures does
    not mean that the algorithm is stochastic.

Related Work
------------

Reference resolution has been done using logical programming techniques for
ages. Without using another technique (such as probabilistic programming),
Robiphora would not be very unique.

The closest related work is from Chai et. al. in 2004: reference resolution of
inherital structures using a graph-matching algorithm.

Object Property Definition Language (OPDL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OPDL
----

OPDL is a domain-specific declarative programming language created for use with
Robiphora. OPDL consists of two kinds of expressions:

:Types:   Definitions of what *kinds of objects* exist in the world, how they
          relate to each other, and what nouns can be used to refer to them.
:Objects: Definitions of instances of objects that exist in the world,
          providing a mechanism to define the context of the robot.

OPDL: An Example
----------------

.. sourcecode:: scheme

    (object jack
      :type (man speaker))

    (type man
      :bases (male)
      :nouns ("man"))

    (type male
      :bases (human)
      :antibases (female)
      :pronouns ("he" "him" "himself"))

    (type speaker
      :pronouns ("I" "me"))

Probability Evaluation
~~~~~~~~~~~~~~~~~~~~~~

Defining Probability Relations
------------------------------

Without probability relations, OPDL serves as a linguistically-oriented way of
writing Prolog facts. To derive probabilistic knowledge from OPDL, I use the
following constant symbols:

* **Relation between bases:** `P(I) = 0.9`
* **Relation between antibases:** `P(A) = 0.0`
* **No relation:** `P(\lnot I) = 0.1`

Resolving Probability
---------------------

Robiphora takes inspiration from the DPLL SAT-solving algorithm. Inputs are the
knowledge base, two types, and a set of visited nodes.

.. raw:: latex

    \begin{algorithmic}
        \Procedure{TypeProbability}{$K, a, b, v$}
            \If{$a$ is $b$}
                \State \Return 1.0
            \EndIf
            \If{$K$ states $a$ is in $b$'s antibases}
                \State \Return $P(A)$
            \EndIf
            \State{Add $A$ to $v$}
            \State \Return{
                $\begin{aligned}
                    \max(&\{P(I) \times \hbox{\Call{TypeProbability}{$K, c, b, v$}}\ |\ c \in K_a - v\} \\ 
                    \cup\  &\{P(\lnot I) \times \hbox{\Call{TypeProbability}{$K, c, b, v$}}\ |\ c \in K_a^c - v\})
                \end{aligned}$}
        \EndProcedure
    \end{algorithmic}

Pruning
-------

By adding an `\alpha` parameter, we are able to avoid visiting nodes we would
not be able to maximize any further:

.. raw:: latex

    \begin{algorithmic}
        \Procedure{TypeProbabilityPruned}{$K, a, b, v, \alpha$}
            \State{Base case unchanged from \Call{TypeProbability}{$\cdot$}}
            \ForAll{$c$ in $K_a - v$}
                \State{$p \gets P(I) \times \hbox{\Call{TypeProbabilityPruned}{$K, c, b, v, \alpha$}}$}
                \If{$p > \alpha$}
                    \State{$\alpha \gets p$}
                \EndIf
            \EndFor
            \If{$\alpha < P(\lnot I)$}
                \ForAll{$c$ in $K_a^c - v$}
                    \State{$p \gets P(\lnot I) \times \hbox{\Call{TypeProbabilityPruned}{$K, c, b, v, \alpha$}}$}
                    \If{$p > \alpha$}
                        \State{$\alpha \gets p$}
                    \EndIf
                \EndFor
            \EndIf
            \State\Return{$\alpha$}
        \EndProcedure
    \end{algorithmic}

Evaluation
~~~~~~~~~~

Compared to Existing Techniques
-------------------------------

* The only paper found which focused on the automatic generation of these
  inherital structures was Chai's from 2004.
* Unfortunaly, Chai only gave the discussion of her technique about `\frac12`
  of a page.
* Therefore, it is hard to compare to other algorithms which don't have an
  OPDL-like structure

Evaluation of Algorithmic Efficency
-----------------------------------

* Without pruning, the probability type determination algorithm will have an
  efficency of `\Theta(2^n)`, where `n` is the number of types in the system.
* This is similar to Chai's work, which uses a truth-table-esque algorithm also
  bound by `\Theta(2^n)`.
* *Once we introduce pruning*, efficency can be as good as `o(n)` if a good
  ordering heuristic is selected.

Conclusion
----------

* Robiphora's biggest advantage is also its biggest disadvantage: having a
  well-defined object system means that you need something to automatically
  generate that object system for practical use.
* Future work could include automatic generation of OPDL-like structures, or
  desigining ordering heuristics for the probability evaluation algorithm.
* Any questions?
