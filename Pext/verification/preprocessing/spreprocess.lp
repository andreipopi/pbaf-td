
% compute all possible supports
% but in the TD algorithm only use the ones that are incident to the guessed stuff.
support(A,C) :- support(A,B), support(B,C). % support is transitive.

datt(A,B) :- att(A,B).
datt(A,C) :- support(A,B), att(B,C).
%datt(A,B) :- support(B,C), att(A,C). 

#show support/2.
#show datt/2.