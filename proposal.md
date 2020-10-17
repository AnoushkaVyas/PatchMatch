# PatchMatch project proposal

### Project ID and title
1. [Patch Match: A Randomized Correspondence Algorithm for Structural Image Editing ](https://gfx.cs.princeton.edu/pubs/Barnes_2009_PAR/patchmatch.pdf)

### Github link
[project-strawhat](https://github.com/Digital-Image-Processing-IIITH/project-strawhat)

### Team Members
1. [Rahul Sajnani](https://github.com/RahulSajnani)
2. [Anoushka Vyas](https://github.com/AnoushkaVyas)
3. [Ajay Shrihari](https://github.com/AjayShrihari)
4. [Chaitanya Kharyal](https://github.com/kharyal)

### Main Goal(s) of the project

The PatchMatch paper proposes a novel patch matching algorithm that is simple yet efficient and fast. The algorithm initialises the patch locations by sampling from a uniform random distribution of locations and assigns the initial patch matching error.

#### Notations

f(x, y) determines the location of the patch in image **B** that is closest to the patch at the location (x, y) in image **A**. D(A[x, y]. B[f(x,y)]) determines the distance (can be mean L1 cost)  between the patches of image **A** and image **B**. Here, A[x,y] and B[x,y] determine the patch with center at (x,y) in image A and image B.

#### Algorithm

The algorithm iteratively finds the closest matching patch in a 2 step process:

1. **Propagation:**

   In this step, we find look at the use the locations of (f(x-1, y), f(x, y - 1)) (in even iter) and (f(x + 1, y), f(x, y + 1)) (in odd iter) for closest patch to (x,y). The idea here is that the patch for the neighbors of (x, y) should be close to the patch at (x,y). The final distance is the D = min(D(A[x, y]. B[f(x,y)]), D(A[x, y]. B[f(x - 1,y)]), D(A[x, y]. B[f(x,y - 1)])).  

2. **Random search:**

   Propagation step might converge to a non optimal minima in finding the nearest patch to resolve this the paper uses random search. 

### Problem definition

### Results of the project

### Milestones and expected timeline

### Dataset
