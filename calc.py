from math import *
from prettytable import PrettyTable

def toFixed(numObj, digits=0): # функция для получения фискированного колличества знаков после запятой
    return f"{numObj:.{digits}f}"

period = 196

# Константы внешней среды
# Физические постоянные
G = 6.67 * 10 ** -11 # гравитационная постоянная
g = 9.81 # ускорение свободного падения
M = 0.029 # молярная масса воздуха 
R = 8.314 # универсальная газовая постоянна, Дж / (модуль * К)
T = 300
P0 = 101325 # атмосферное давление на поверхности Кербина

RadiusOfKerbin = 600000 # радиус Кербина, м
MassOfKerbin = 5.292 * 10 ** 22 # масса Кербина, кг

Mf = 76 * 1000 # начальная масса ракеты, кг
Me = 34 * 1000 # масса ракеты без топлива, кг
Isp = 280 # удельный импульс двигателей, секунды

massOfSideEngine = 1.97 # масса каждого отдельного бокового двигателя, кг
massOfCentralEngine = 1.97 # масса центрального двигателя, кг
massOfManeurEngine = 1.97 # масса маневорового двигателя, кг

massOfSideTankFull = 6.78 * 1000 # масса каждого бака бокового двигателя в наполненном состоянии, кг
massOfSideTankEmpty = 0.75 * 1000 # масса каждого бака бокового двигателя в сухом состоянии, кг
massOfCentralBottomTankFull = 10.13 * 1000 # масса нижнего бака центрального двигателя в наполненном состоянии, кг
massOfCentralBottomTankEmpty = 1.13 * 1000 # масса нижнего бака центрального двигателя в сухом состоянии, кг
massOfCentralTopTankFull = 5.06 * 1000 # масса верхнего бака центрального двигателя в наполненном состоянии, кг
massOfCentralTopTankEmpty = 0.56 * 1000 # масса верхнего бака центрального двигателя в сухом состоянии, кг
massOfManeurTankFull = 5.06 * 1000 # масса бака маневрового двигателя в наполненном состоянии, кг
massOfManeurTankEmpty = 0.56 * 1000 # масса бак2.7611а маневрового двигателя в сухом состоянии, кг

stageEngineDuration = [120, 160, 36] # время работы двигателей кажой ступени
stagePeriods = [120, 160, 196]

Cf = 0.5 # коэффициент лобового аэродинамического сопротивления
S = 2.7611 # метры в квадрате, площадь конуса

startMassOnStage = [ # масса ракеты в начале каждой ступени
    Mf,
    Mf - (massOfSideEngine + massOfSideTankFull) * 4,
    Mf - (massOfSideEngine + massOfSideTankFull) * 4 - (massOfCentralEngine + massOfCentralBottomTankFull + massOfCentralTopTankFull),
    Mf - (massOfSideEngine + massOfSideTankFull) * 4 - (massOfCentralEngine + massOfCentralBottomTankFull + massOfCentralTopTankFull) - (massOfManeurEngine + massOfManeurTankFull)
]

endMassOnStage = [
    startMassOnStage[0] - (massOfSideTankFull - massOfSideTankEmpty) * 4,
    startMassOnStage[1] - (massOfCentralTopTankFull - massOfCentralTopTankEmpty) - (massOfCentralBottomTankFull - massOfCentralBottomTankEmpty),
    startMassOnStage[2] - (massOfManeurTankFull - massOfManeurTankEmpty),
    startMassOnStage[3]
]

def fuel_consumption_coefficient(massWithFuel, massWithoutFuel, timeOfWork): # формула расчета коэффицента расхода топлива, кг в секунду
    return (massWithFuel - massWithoutFuel) / timeOfWork

fuelConsumptionCoefficient = [
    fuel_consumption_coefficient(massOfSideTankFull, massOfSideTankEmpty, stageEngineDuration[0]),
    fuel_consumption_coefficient(massOfCentralTopTankFull + massOfCentralBottomTankFull, massOfCentralTopTankEmpty + massOfCentralBottomTankEmpty, stageEngineDuration[1]),
    fuel_consumption_coefficient(massOfManeurTankFull, massOfManeurTankEmpty, stageEngineDuration[2]),
    0
]

fuelConsumptionCoefficientOnStage = [
    fuelConsumptionCoefficient[0] * 4 + fuelConsumptionCoefficient[1],
    fuelConsumptionCoefficient[1],
    fuelConsumptionCoefficient[2],
    0
]

def lengthOfVector(v):
    return (v[0] ** 2 + v[1] ** 2) ** 0.5

def angle(h): # определяет, какой угол должен быть взависимости от высоты
    if h <= 2000:
        return 0
    elif h >= 70000:
        return 45
    return (h - 2000) / (70000 - 2000) * 45

def stage(t): # определяет, какая ступень сейчас активна
    global stagePeriods
    res = 3
    for i in range(len(stagePeriods)):
        if stagePeriods[i] >= t:
            res = i
            break
    
    return res

def mass_of_rocket_in_moment(t): # масса топлива взависиомсти от времени на конктретной ступени, кг
    global stagePeriods
    global startMassOnStage
    timeOnStage = t
    if (stage(t) > 0):
        timeOnStage -= stagePeriods[stage(t) - 1]
    
    return startMassOnStage[stage(t)] - fuelConsumptionCoefficient[stage(t)] * timeOnStage

def drag_force(Cf, velocityArray_in_time, S, ro): # сила сопротивления среды (воздуха) в Ньютонах
    return (Cf * ro * velocityArray_in_time ** 2 * S) / 2

def Ro(P, M, R, T_temperatur): # плотность среды (воздуха)
    return (P * M) / (T_temperatur * R) 

def pressure(P0, M, R, T, g, h): # атмосферное давление от высоты
    return (P0 * exp(-M * g * h / (R * T)))

def the_Tsiolkovsky_Formula(Isp, CurrentMass, FinalMassOnStage, EnginesQuantity): # формула Циолковского, м/с
    return Isp * EnginesQuantity * log(CurrentMass / FinalMassOnStage)

def force_of_gravity(G, mass1, mass2, distance): # модуль силы гравитационного взаимодействия, Н
    return (G * mass1 * mass2) / (distance ** 2)

def scalar_to_vector(scalar, vector):
    distance = lengthOfVector(vector)
    if distance == 0:
        return (0, 0)
    cosinus = -vector[0] / distance
    sinus = -vector[1] / distance
    return (scalar * cosinus, scalar * sinus)

def force_of_thrust(Isp, FuelConsumptionCoefficient): # сила тяги двигателя, Н
    return Isp * FuelConsumptionCoefficient * g

def acceleration(ForceOfThrust, ForceOfGravity, ForceOfAirResistance, Angle, mass): # ускорение, м/с^2
    return ((ForceOfThrust * cos(radians(Angle)) + ForceOfGravity[0] + ForceOfAirResistance[0]) / mass, (ForceOfThrust * sin(radians(Angle)) + ForceOfGravity[1] + ForceOfAirResistance[1]) / mass)

def array_to_csv(row):
    return '\t'.join(row) + '\n'

def head_to_csv(head):
    return array_to_csv([f'"{i}"' for i in head])

forceOfThrust = [
    5 * force_of_thrust(Isp, fuelConsumptionCoefficientOnStage[0]),
    force_of_thrust(Isp, fuelConsumptionCoefficientOnStage[1]),
    force_of_thrust(Isp, fuelConsumptionCoefficientOnStage[2]),
    0
]

positionArray = [(RadiusOfKerbin, 0)]
heightArray = [lengthOfVector(positionArray[0]) - RadiusOfKerbin]
velocityArray = [(0, 0)]
massOfRocketArray = [mass_of_rocket_in_moment(t) for t in range(period + 1)]
forceOfGravityArray = [
    force_of_gravity(
        G,
        massOfRocketArray[0],
        MassOfKerbin,
        heightArray[0] + RadiusOfKerbin
    )
]

timeArray = list(range(period + 1))
pressureArray = [pressure(P0, M, R, T, forceOfGravityArray[0] / massOfRocketArray[0], heightArray[0])]
roArray = [Ro(pressureArray[0], M, R, T)]
dragForceArray = [drag_force(Cf, lengthOfVector(velocityArray[0]), S, Ro(pressureArray[0], M, R,  T))]
forceOfThrustArray = [forceOfThrust[stage(t)] for t in range(period + 1)]
angelArray = [angle(heightArray[0])]


accelerationArray = [
    acceleration(
        forceOfThrust[0],
        scalar_to_vector(forceOfGravityArray[0], positionArray[0]),
        scalar_to_vector(dragForceArray[0], velocityArray[0]),
        angelArray[0],
        massOfRocketArray[0]
    )
]

absoluteMassError = 500 # абсолютная погрешность массы в нулеврй момент времени, кг
relativeMassError = absoluteMassError / massOfRocketArray[0] # относительная погрешность массы

absoluteThrustError = 100 # абсолютная погрешность тяги, Н
relativeThrustError = absoluteThrustError / forceOfThrustArray[0] # относительная погрешность массы

table = PrettyTable()
head = ['Время с момента запуска, с', 'Сила тяги двигателя, Н', 'Масса ракеты, кг', 'Сила гравитационного взаимодействия, Н', 'Атмосферное давление', 'Плотность среды', 'Сила лобового сопротивления, Н', 'Ускорение, м/с^2', 'Скорость, м/с', 'Высота над поверхностью Кербина, м']
table.field_names = head
table.align = "r"
csvFile = ''
textFile = ''
if __name__ == '__main__':
    csvFile = open('table.csv', 'w', encoding='utf-16')
    csvFile.write(array_to_csv(head))
    textFile = open('table.txt', 'w', encoding='utf-16')

for t in range(period):

    row = [
        str(t), 
        toFixed(forceOfThrustArray[t], 6) + ' ± ' + toFixed(relativeThrustError * forceOfThrustArray[t], 6), 
        toFixed(massOfRocketArray[t], 6) + ' ± ' + toFixed(relativeMassError * massOfRocketArray[t], 6), 
        toFixed(forceOfGravityArray[t], 6) + ' ± ' + toFixed(relativeMassError * forceOfGravityArray[t], 6),
        toFixed(pressureArray[t], 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / (lengthOfVector(accelerationArray[t]) * massOfRocketArray[t]) * pressureArray[t], 6),
        toFixed(roArray[t], 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / (lengthOfVector(accelerationArray[t]) * massOfRocketArray[t]) * roArray[t], 6),
        toFixed(dragForceArray[t], 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / (lengthOfVector(accelerationArray[t]) * massOfRocketArray[t]) * 2 * dragForceArray[t], 6),
        toFixed(lengthOfVector(accelerationArray[t]), 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / massOfRocketArray[t], 6),
        toFixed(lengthOfVector(velocityArray[t]), 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / (lengthOfVector(accelerationArray[t]) * massOfRocketArray[t]) * lengthOfVector(velocityArray[t]), 6),
        toFixed(heightArray[t], 6) + ' ± ' + toFixed((relativeThrustError * forceOfThrustArray[t] + relativeMassError * forceOfGravityArray[t]) / (lengthOfVector(accelerationArray[t]) * massOfRocketArray[t]) * heightArray[t], 6)
    ]

    table.add_row(row)
    if __name__ == '__main__':
        csvFile.write(array_to_csv(row))

    forceOfGravityArray.append(
        force_of_gravity(
            G,
            massOfRocketArray[t + 1],
            MassOfKerbin,
            heightArray[t] + RadiusOfKerbin
        )
    )

    pressureArray.append(
        pressure(P0, M, R, T, forceOfGravityArray[t] / massOfRocketArray[t], heightArray[t])
    )

    roArray.append(
        Ro(
            pressureArray[t],
            M,
            R, 
            T
        )
    )

    dragForceArray.append(
        drag_force(
            Cf,
            lengthOfVector(velocityArray[t]),
            S,
            roArray[t]
        )
    )

    velocityArray.append((velocityArray[t][0] + accelerationArray[t][0], velocityArray[t][0] + accelerationArray[t][1]))

    positionArray.append((positionArray[t][0] + velocityArray[t][0], positionArray[t][1] + velocityArray[t][1]))

    heightArray.append(lengthOfVector(positionArray[t]) - RadiusOfKerbin)

    angelArray.append(angle(heightArray[t]))

    accelerationArray.append(acceleration(
        forceOfThrustArray[t + 1],
        scalar_to_vector(forceOfGravityArray[t], positionArray[t]),
        scalar_to_vector(dragForceArray[t], velocityArray[t]),
        angelArray[t],
        massOfRocketArray[t]
    ))

velocitiyScalarArray = [lengthOfVector(velocityArray[i]) for i in range(period + 1)]


if __name__ == '__main__':
    textFile.write(str(table))
    textFile.close()
    csvFile.close()
    print(table)
