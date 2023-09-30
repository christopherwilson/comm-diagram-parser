# Useful links
**some software suggestions**  
https://math.stackexchange.com/questions/82024/software-for-creating-commutative-diagrams    

# GUI Software
## Quiver
https://q.uiver.app/   
GUI, can convert to latex with tikz-cd.  
Doesn't generate from morphisms/can't convert to morphsims.

## tikzcd-editor
https://tikzcd.yichuanshen.de/  
Similar to Quiver, GUI for tikz-cd. Annoyingly similar name to tikz-cd
## General Diagram Software
These are capable of producing Commutative Diagrams, but can't convert from/to morphisms. Also unlikely to do latex.

# LaTeX
Generally packages seem to either use matrix-like grids or cartesian coordinates to position objects and arrows between them.

## tikz-cd
https://www.ctan.org/pkg/tikz-cd   
Generates commutative diagrams. In some sense the result isn't very human readable, but the text isn't very human readable. Good candidate for a thing to convert my input into though. Will still probably need some kind of algorithm to determine where to place each object in the diagram to avoid overlaps.
## Generating Latex Code for Commutative Diagrams
https://cs230.stanford.edu/projects_fall_2022/reports/103.pdf    
Attempting to create a model that generates TikZ code for a commutative diagram based off an image of a commutative diagram.  
Stuff like this could be useful if I want to be able to feed any commutative diagram in, but I know almost nothing about machine learning or being able to read in images, so this would be challenging for me to implement. Additionally, the model in this paper seems to generate incorrect diagrams often, especially on labels, which isn't ideal. 

## Guide to commutative diagram packages
https://www.jmilne.org/not/CDGuide.html           
Guide to a variety of latex packages for drawing commutative diagrams, although made in 2006 so outdated.

## DCpic
https://www.ctan.org/pkg/dcpic        
Basically does the morphisms -> commutative diagram portion of this project, works by defining the objects (and their position), then the morphisms between the objects. Would still need good placement of objects to avoid overlapping arrows.

## CoDi
https://www.ctan.org/pkg/commutative-diagrams        
Very similar to DCpic, but uses matrix for layout instead of cartesian grid.