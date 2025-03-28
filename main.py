import pandas as pd
import numpy as np
import lashing as ls
import load as ld
import forces as ff
import calcs


#Load properties dimX,dimY,dimZ,mass
#Moving direction is Y
load = ld.Load(3,23,2.7,160)
wind = ff.Wind(load,0)

forces = ff.Forces(load,3,wind)
print(forces.valueOftheForces)

lashings = []

#angle between cable and floor//angle between projection and load perpendicular//Breaking Strength of lashing material//Friction coefficient//Lashing moving direction is F 
lashings.append(ls.Lashing(0,0,5,0.2,'F'))
lashings.append(ls.Lashing(0,0,5,0.2,'R'))
lashings.append(ls.Lashing(0,0,5,0.2,'L'))
lashings.append(ls.Lashing(0,0,5,0.2,'A'))



calcs.transverseSliding(load,lashings,forces)
calcs.longtidunalSliding(load,lashings,forces)















