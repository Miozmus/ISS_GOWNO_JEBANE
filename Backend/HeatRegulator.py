c = 729     #Ciepło właściwe powietrza [J / (kg*K)]
Pmax = 15   #Moc maksymalna piecyka [kW]
#deltaQ, Moc Pieca, Temperatura Max, stepTime


def calculateAirHeat(mAir, T):
    #ile ciepła potrzeba do ogrzania powietrza wewnątrz balonu do wyznaczonej temperatury
    heat = c * mAir * T
    return heat

def calculateAirTemperature(heat, mAir):
    #jaka jest temperatura wewnątrz balonu
    T = heat / (c * mAir)
    return T