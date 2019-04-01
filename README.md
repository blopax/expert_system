[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Build Status](https://travis-ci.com/blopax/expert_system.svg?branch=master)](https://travis-ci.com/blopax/expert_system)

# Expert system

Expert system solver in python 3.7.  

It is a 42 project with some given constraints that explain choices that were made. Noticeable constraints are: use a 
backward chaining inference motor and examples with rules that are not Horn Clauses. (So in this case algorithm is not complete)

A set of options is given:
- An interactive mode where the user can change the initial true facts
- A "fast" mode where the algorithm stops as soon as it finds a confirmed value for all the queries. 
It doesn't continue the search to look for contradictions.
- An 'advice' mode for when there are ambiguous queries. Program will make a proposition on how to change initial facts
- A "complete" option that will explicitly mention if the initial ruleset contains non Horn clauses rules.
- A mode option that defaults to backward chaining inference motor but can be set to resolution mode.


## Objective
Expert systems are composed of rules (which implies letters, example : A + B => C), initial facts (example : =A) 
and queries (example : ?C). All the rules defines the relationship between letters (they are gathered into a graph, 
the expert system). Then some (or no) letters are set to true (=ABC), they are the initial facts. Finally, depending 
on the initial facts we look at the final state (True or False) of the queried letters.

```
A + B => C

=AB

?C # C is true if A and B are True else it is False (except if C is set to True at the beginning of course)
```

Please note that the subject explicitly provides examples with rules that are not 
horn clauses and to use a backward chaining algorithm. 
Only facts that are true are provided in the initial file.    
This has consequences on the way the subject is tackled (see note on resolution_mode).


### How to run the program
You must have python3 installed.  

Run the program as follow:

<pre>
python3 expert_system.py [-h] [-i] [-f] [=a] [-c]
                         [-r {backward_chaining,resolution}]
                         filename
</pre>

The only required input is the input file (`filename`). The rest is optional.


### Input file
Input file must be of this form:

<pre>
# this is a comment$
# spacing is not important

C=> E           # C implies E
A + B + C => D  # A and B and C implies D
A | B=> C       # A or B implies CA + !B=> F# A and not B implies F
C | !G=> H      # C or not G implies HV ^ W=> X# V xor W implies X
A + B=> Y + Z   # A and B implies Y and Z
C | D=> X | V   # C or D implies X or V
E + F=> !V      # E and F implies not V
A + B<=> C      # A and B if and only if C
A + B<=> !C     # A and B if and only if not C

=ABG    # Initial facts : A, B and G are true. All others are false.
        # If no facts are initially true, then a simple "=" followed# by a newline is used

?GVX# Queries : What are G, V and X ?
</pre>



### Options
<pre>
-h, --help            show this help message and exit
-i, --interactive     user can change the initial true facts on the fly
-f, --fast            algorithm stops as soon as queries values are confirmed. (only for backward chaining resolution_mode) 
-a, --advice          program displays some advice if some facts are ambiguous.   
-c, --complete        program says if ruleset contains rules that are not Horn clauses
-r, --resolution_mode {backward_chaining,resolution}
                      choose the resolution mode. default to backward_chaining
</pre>  

### Note on the resolution_mode
The 2 modes are conceptually quite different:
The backward chaining inference motor is dynamic resolution. 
By default, all facts are false, and can only be made true by the initial facts statement,or by application of a rule. 
A fact can only be undetermined if the ruleset is ambiguous, for example if I say "A is true, also if A then B or C", 
then B and C are undetermined.
Backward chaining inference is sound. It is complete if and only if all the rules are horn clauses.

When set to 'resolution', the program will ask the user to fill the facts that are False.
The facts that are not initially set to True or False will by default `undefined` except if the resolution 
algorithm set them to a specific value.
Resolution algorithm is sound and complete.


### Results displayed
Program will print the logical value of the queries or if there is a contradiction on a specific query.

put a gif


## Unit tests
Running ```python3 test.py``` will run the unit tests written for the program. 
Those tests are mainly for the backward chaining solver and for parsing errors. 
It is also included in CI.


## General learning
Propositional logic. Completeness. Vague subject so choices have to be made.


## Requirements

| Library | version |
| --- | --- |
| Python | 3.7.1 |


