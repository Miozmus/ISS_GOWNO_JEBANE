g = 9.80665 #m/(s^2)
pressSeaLvl = 101325 #Pa
tempLapseRate = 0.00976 #K/m
constPressureHeat =1004.68506 #J/(kg*K)
tempSeaLvl = 288.16 #K
molarMass = 0.02896968 #kg/mol
univGas = 8.314462618 #J/(mol*K)



def calculateForce(m, h, Vo, Tout, Tins, Vlast):
    ro = _calculateAirDensity(h, Tout)
    Fc = g* Vo * ro * (1 - (Tout / Tins))
    Fg = m * g
    Fg += 0.2 * Vlast**2
    F = Fc - Fg
    return F

def _calculateAirDensity(h, Tout):
    press = _calculateAirPressure(h)
    ro = press * molarMass / (univGas * Tout)
    return ro
def _calculateAirPressure(h):
    press = pressSeaLvl * ( (1 - (tempLapseRate * h / tempSeaLvl) )**(g * molarMass / (univGas * tempLapseRate)) )
    return press




