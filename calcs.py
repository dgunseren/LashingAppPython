
import numpy as np



def transverseSliding(load,lashings,forces):

    xForces = forces.xyDict['totalX']
    totalLashingX = 0
    friction = lashings[0].FrictionCoefficient * load.weight

    for _ in lashings:
        totalLashingX = totalLashingX+ abs(_.fx)
    finalforceX = totalLashingX+friction*np.cos(np.deg2rad(forces.slope))


    if xForces<finalforceX:
        print('No transverse sliding occurs.')
    else:
        print('Transverse sliding!! Check lashing!')
        flag = 1
        requiredLashing = 0
        while flag:
            finalforceX = finalforceX+ lashings[0].fx
            requiredLashing = requiredLashing+1
            if xForces<finalforceX:
                print('You need %d more lashing on rear' % requiredLashing)
                flag = 0



        

    


def longtidunalSliding(load,lashings,forces):

    yForces = forces.xyDict['totalY']
    totalLashingY = 0
    friction = lashings[0].FrictionCoefficient * load.weight

    for _ in lashings:
        totalLashingY = totalLashingY+ abs(_.fy)
    finalforceY = totalLashingY+friction*np.cos(np.deg2rad(forces.slope))

    if yForces<finalforceY:
        print('No longtidunal sliding occurs.')
    else:
        print('Longtidunal sliding occurs.')
        flag = 1
        requiredLashing = 0
        while flag:
            finalforceY = finalforceY+ lashings[0].fy
            requiredLashing = requiredLashing+1
            if yForces<finalforceY:
                print('You need %d more lashing on front or back' % requiredLashing)
                flag = 0

    














