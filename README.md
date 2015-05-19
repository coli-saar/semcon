# Semantic construction with NLTK #

This is a tool for semantic construction with hand-written
grammars, based on [NLTK](http://www.nltk.org). It was developed by
[Alexander Koller](http://www.ling.uni-potsdam.de/~koller), primarily
for pedagogical purposes.

NLTK is an excellent library for teaching computational linguistics,
but it is lacking in the area of semantic construction, i.e. the
computation of formal semantic representations for a sentence from a
syntactic parse using a (hand-written) grammar. There is some code for
combining lambda terms within a context-free grammar with feature
structures, but it is badly documented and (as far as I can tell) has
issues with variable renaming.

The semcon system in this repository is meant to address this issue,
and to help lecturers in letting students explore semantic
construction.


### Installation ###

Using semcon requires that you have a working installation of
[Python](http://www.python.org) and [NLTK 3](http://www.nltk.org) on
your computer.

You can download the source code of semcon by cloning the Mercurial
repository, using a Mercurial client of your choice. 


### Compiling a grammar ###

Grammars for the semcon tool consist of two parts: a context-free
grammar that defines the valid syntactic structures, and a Python file
that defines a mapping from grammar rules to semantic construction
rules.

These files will typically not be written by hand, but compiled from a
human-readable grammar using the `grcompile` script, as follows:

```
python grcompile.py <semcon-grammar.scfg> <grammar_syn.cfg> <grammar_sem.py>
```

where `semcon-grammar.scfg` is a human-readable grammar consisting of
both syntax rules and semantic construction rules; `grammar_syn.cfg`
is the filename into which the script will write the syntax part of
the grammar; and `grammar_sem.py` is the filename into which the
script will write the semantic construction part of the grammar. You
can choose the filenames freely, but note that the filename of
`grammar_sem.py` must end in `.py`.


### Grammars ###

Semantic construction grammars (`semcon-grammar.scfg` in the example
above) consist of context-free production rules, each of which is
annotated with a semantic construction rule. The intuition is that
when a rule `A -> B C` is used to combine a `B`-constituent and a
`C`-constituent, the semantic representation for the new
`A`-constituent is computed by applying the semantic construction rule
to the semantic representations for `B` and `C`.

Here is an example grammar:

```
% start S

S -> NP VP
%% ({X1})({X2})

NP -> Det N
%% ({X1})({X2})

Det -> 'every'
%% y: \P Q. all y. (P(y) -> Q(y))

N -> 'man'
%% man

VP -> 'sleeps'
%% sleep
```

All lines that do not start with `%%` are copied into the syntactic
grammar, and will be read into an NLTK grammar. Thus they must conform
to the usual syntax of NLTK grammar files. In the example, we have a
context-free grammar with five production rules and start symbol `S`.

Each line that starts with `%%` provides a semantic construction rule
for the grammar rule that immediately precedes it. In the simplest
case, the rule provides a lambda term that is used directly as the
semantic representation of the parent nonterminal. For instance, the
rule for "man" expresses that the semantic representation for the `N`
node in the parse tree should be the lambda term `man`. You can use
arbitrary lambda terms here, using the syntax of NLTK's `nltk.logic`
module.

For rules that have nonterminals on the right-hand side, you will want
to insert the meaning representations of these children into the
meaning representation for the parent. You can do this with the curly
brace syntax as in the first two grammar rules. The semantic
representations for the NP and VP are inserted, as strings, into the
placeholders `{X1}` (for the NP) and `{X2}` (for the VP). The
resulting string then becomes the semantic representations for the new
S constituent. The placeholders are sorted alphabetically; thus `X1`
is the "first" placeholder and `X2` is the "second" one. Because NP is
the first (= left) child of the grammar rule and VP is the second (=
right) child, this means that `X1` gets the NP semantics and `X2` the
VP semantics. Note the brackets around `{X1}` and `{X2}`; these are
needed to make sure NLTK parses the resulting lambda terms correctly.

The names you use for the placeholders can be any string that would be
a valid variable name in Python after stripping of the curly braces
(i.e., not `{1}` or something like that, but `{_1}` should be
okay). Note that the placeholder names have no meaning, except to
establish the alphabetical order of placeholders, and that you cannot
use the same placeholder twice in the same rule (i.e., you can't do
`{VP}({NP},{NP})`).

Finally, you will sometimes want to generate fresh names during
semantic construction. For instance, in the "every" rule, all
occurrences of the universally quantified variable y should be
replaced by a new name that is not used anywhere else, so the
quantifier doesn't accidentally capture occurrences of y that are free
in P or Q. This is achieved by prefixing the entire lambda term with
`y: `. This tells the parser to generate new names `y1`, `y2`,
etc. for each instance of the grammar rule.




### Parsing a sentence ###

Once you have written a grammar and compiled it with `grcompile.py`,
you can use it from a Python shell. Change to the directory that has
the grammar files and the `semcon.py` script, run Python and do the
following:

```
>>> from semcon import *
>>> gr = load_grammar("test.cfg", "test_sem")
>>> parse("every man loves a woman", gr)
Found 1 parse trees.
Using parse tree: (S (NP (Det every) (N man)) (VP (TV loves) (NP (Det a) (N woman))))
Semantics: all y1.(man(y1) -> exists y2.(woman(y2) & love(y2))(y1))
<AllExpression all y1.(man(y1) -> exists y2.(woman(y2) & love(y2))(y1))>
```

Observe that the `load_grammar` function loads a grammar and returns
it. You pass the filename of the syntactic grammar first, and the name
of the file with the semantic construction rules (minus the ending
`.py`) second.

You can then parse a sentence with the `parse` function. The `parse`
function returns a lambda expression for the semantic representation
of the complete sentence. One limitation is that if the sentence is
syntactically ambiguous, the parser will only look at the first parse
tree that NLTK returns.


### Executing Geoquery queries ###

The semcon tool integrates with the Geoquery database, a dataset with
geographical information about the United States that is popular in
the semantic parsing literature.

To do this, you need to install the following additional things:

 * [SWI Prolog](http://www.swi-prolog.org/Download.html); edit
   `semcon.py` to set the `SWIPL` variable to the directory containing
   the `swipl` binary.
 * From the
   [Geoquery website](https://www.cs.utexas.edu/users/ml/nldata/geoquery.html),
   get the `geobase` file and save it as `geobase.pl`, and get the
   `geoquery` file and save it as `geoquery.pl`.

You can then call the `query` function to evaluate a Geoquery query
and show you the list of results. You can find examples of such
queries in the annotated `geoqueries880` corpus on the Geoquery
website. Note that `query` expects an NLTK logic expression, which you
can construct from a query string using `nltk.logic.Expression.fromstring`.

As a fun exercise, you can write a grammar for the Geoquery language
by hand and make it map English natural-language queries into Geoquery
queries. The end result should behave like this (assuming `gr` is your
grammar, which you have previously loaded with `load_grammar`):

```
>>> query(parse("name the cities in oregon", gr))
Found 2 parse trees.
Using parse tree: (S name (NP (NP the (NP cities)) (PP in (NP oregon))))
Semantics: answer(A2,(city(A2) & loc(A2,B1) & const(B1,stateid(oregon))))
answer(A2,(city(A2) , loc(A2,B1) , const(B1,stateid(oregon))))

Found 3 answers:
 - eugene
 - portland
 - salem
```

