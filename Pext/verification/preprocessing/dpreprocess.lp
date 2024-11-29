%----old encoding
% compute all possible supports
% but in the TD algorithm only use the ones that are incident to the guessed stuff.
support(A,C) :- support(A,B), support(B,C). % support is transitive.

datt(A,B) :- att(A,B).
datt(A,C) :- support(A,B), att(B,C).
datt(A,B) :- support(B,C), att(A,C). 

#show support/2.
#show datt/2.

%-------------------turns out still the correct one





%potential new encoding, but not sure this is the one needed
% compute all possible supports
% but in the TD algorithm only use the ones that are incident to the guessed stuff.
%support(A,C) :- support(A,B), support(B,C). % support is transitive.
%datt(A,B) :- att(A,B).
%datt(A,C) :- support(A,D), att(D,C). %derived a supported attack
%datt(A,B) :- support(B,C), datt(A,C). %derived if a supermediated attack through a supported attack
%datt(A,B) :- support(B,C), att(A,C). %derived if a supermediated through the special case of a supported attack
%#show support/2.
%#show datt/2.
%----------

