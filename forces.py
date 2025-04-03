import numpy as np

class Forces:
    g = 9.81
    forceDict={
            'breakAccel':0.8*g,
            'Accel':0.5*g,
            'Cornering':0.5*g,
            }
    valueOftheForces = {
        'forward':0,
        'aft':0,
        'left':0,
        'right':0
    }
    windDict = {
        'forward':0,
        'left':0

    }
    xyDict ={
        'totalX':0,
        'totalY':0 
    }
    
    def __init__(self,Load,slope,Wind):
        self.LoadT = Load 
        self.mass = Load.mass
        self.slope = slope
        self.wind = Wind 
        self.calculateForcesByMotion()


    def calculateForcesByMotion(self):
        
        if self.slope>0:
            Forces.valueOftheForces['forward'] = self.mass*Forces.forceDict['breakAccel']+self.mass*Forces.g*np.sin(np.deg2rad(self.slope))+self.wind.forceYdir
        else:
            Forces.valueOftheForces['forward'] =  self.mass*Forces.forceDict['breakAccel']+self.wind.forceYdir
        
        if self.slope<0:
            Forces.valueOftheForces['aft'] = self.mass*Forces.forceDict['breakAccel']-self.mass*Forces.g*np.sin(np.deg2rad(self.slope))+self.wind.forceYdir
        else:
            Forces.valueOftheForces['aft'] = self.mass*Forces.forceDict['Accel']+self.wind.forceYdir

        Forces.valueOftheForces['left'] = self.mass*Forces.forceDict['Cornering']+self.wind.forceXdir
        Forces.valueOftheForces['right'] = self.mass*Forces.forceDict['Cornering']+self.wind.forceXdir
        Forces.xyDict['totalY'] = max(Forces.valueOftheForces['forward'],Forces.valueOftheForces['aft']) 
        Forces.xyDict['totalX'] = max(Forces.valueOftheForces['left'],Forces.valueOftheForces['right']) 



class Wind:
    beaufort_max_kmh = {
    0: 1,
    1: 5,
    2: 11,
    3: 19,
    4: 28,
    5: 38,
    6: 49,
    7: 61,
    8: 74,
    9: 88,
    10: 102,
    11: 117,
    12: 180,  # No upper limit for hurricane-force winds
}
    def __init__(self,Load,beaufort):
        self.Load = Load
        self.beaufort = beaufort
        self.forceXdir = 0
        self.forceYdir = 0
        self.windLoad()

    def windLoad(self):
        rho = 1.225 
        self.forceYdir = 0.001*0.5*self.Load.XZCrossSection*rho*Wind.beaufort_max_kmh[self.beaufort]**2
        self.forceXdir = 0.001*0.5*self.Load.YZCrossSection*rho*Wind.beaufort_max_kmh[self.beaufort]**2
        

