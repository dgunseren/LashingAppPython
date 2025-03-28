import numpy as np

class Lashing:
    def __init__(self,alpha,beta,BreakingStrength,FrictionCoefficient,RelativeSide,groundPosition = [0,0,0],LoadPosition = [0,0,0] ):
        self.alpha = alpha
        self.beta = beta
        self.BreakingStrength = BreakingStrength
        self.FrictionCoefficient = FrictionCoefficient
        self.RelativeSide = RelativeSide
        self.groundPosition = groundPosition
        self.LoadPosition = LoadPosition
        self.forces()
        self.effectiveCoeff()
        

    def forces(self):
        self.fxCoef = self.BreakingStrength*(np.cos(np.deg2rad(self.alpha)*np.cos(np.deg2rad(self.beta))+self.FrictionCoefficient*np.sin(np.deg2rad(self.alpha))))
        self.fyCoef = self.BreakingStrength*(np.cos(np.deg2rad(self.alpha)*np.sin(np.deg2rad(self.beta))+self.FrictionCoefficient*np.sin(np.deg2rad(self.alpha))))
    def effectiveCoeff(self):
        self.fx = self.fxCoef*self.BreakingStrength
        self.fy = self.fyCoef*self.BreakingStrength