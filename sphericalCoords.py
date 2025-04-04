import numpy as np

def convertForceToSpherical(lashing):

    if lashing.RelativeSide == 'R':
        if lashing.leaningtoward == 'R':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 90 - lashing.beta
        if lashing.leaningtoward == 'L':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 270+ lashing.beta

    elif lashing.RelativeSide == 'L':
        if lashing.leaningtoward == 'R':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 270 - lashing.beta
        if lashing.leaningtoward == 'L':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 90 + lashing.beta

    elif lashing.RelativeSide == 'F':
        if lashing.leaningtoward == 'R':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 180 - lashing.beta
        if lashing.leaningtoward == 'L':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = lashing.beta
    elif lashing.RelativeSide == 'A':
        if lashing.leaningtoward == 'R':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 360 - lashing.beta
        if lashing.leaningtoward == 'L':

            sphericalAlpha = lashing.alpha + 90
            sphericalBeta = 180+ lashing.beta

    [Fx,Fy,Fz] = [np.cos(np.deg2rad(sphericalBeta))*np.sin(np.deg2rad(sphericalAlpha))*lashing.BreakingStrength,
                np.sin(np.deg2rad(sphericalAlpha))*np.sin(np.deg2rad(sphericalBeta))*lashing.BreakingStrength,
                lashing.BreakingStrength*np.sin(np.deg2rad(sphericalAlpha))]
    lashing.LashingForceForMoments = [Fx,Fy,Fz]
    preu
    


    


