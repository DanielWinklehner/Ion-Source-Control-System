EESchema Schematic File Version 2
LIBS:TemperatureSensor-cache
LIBS:arduino_micro_shield
LIBS:power
LIBS:device
LIBS:switches
LIBS:relays
LIBS:motors
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 2
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L MAX31856 U?
U 1 1 5A00E90A
P 8600 2050
F 0 "U?" H 8600 2450 60  0000 C CNN
F 1 "MAX31856" H 8600 1650 60  0000 C CNN
F 2 "" H 8600 2050 60  0000 C CNN
F 3 "" H 8600 2050 60  0000 C CNN
	1    8600 2050
	1    0    0    -1  
$EndComp
NoConn ~ 8150 2250
NoConn ~ 8150 2350
Wire Wire Line
	8150 1750 8150 1450
Wire Wire Line
	8150 1450 8300 1450
Wire Wire Line
	9050 1750 9050 1450
Wire Wire Line
	9050 1450 8900 1450
$Comp
L GND #PWR?
U 1 1 5A00E917
P 8300 1450
F 0 "#PWR?" H 8300 1200 50  0001 C CNN
F 1 "GND" H 8300 1300 50  0000 C CNN
F 2 "" H 8300 1450 50  0001 C CNN
F 3 "" H 8300 1450 50  0001 C CNN
	1    8300 1450
	0    -1   -1   0   
$EndComp
$Comp
L GND #PWR?
U 1 1 5A00E91D
P 8900 1450
F 0 "#PWR?" H 8900 1200 50  0001 C CNN
F 1 "GND" H 8900 1300 50  0000 C CNN
F 2 "" H 8900 1450 50  0001 C CNN
F 3 "" H 8900 1450 50  0001 C CNN
	1    8900 1450
	0    1    1    0   
$EndComp
Wire Wire Line
	9050 2350 9050 2550
Connection ~ 9050 2450
Wire Wire Line
	9050 2450 9100 2450
$Comp
L +3.3V #PWR?
U 1 1 5A00E926
P 9100 2450
F 0 "#PWR?" H 9100 2300 50  0001 C CNN
F 1 "+3.3V" H 9100 2590 50  0000 C CNN
F 2 "" H 9100 2450 50  0000 C CNN
F 3 "" H 9100 2450 50  0000 C CNN
	1    9100 2450
	0    1    1    0   
$EndComp
$Comp
L C C?
U 1 1 5A00E92C
P 9050 2700
F 0 "C?" H 9075 2800 50  0000 L CNN
F 1 "0.1uF" H 9075 2600 50  0000 L CNN
F 2 "" H 9088 2550 50  0000 C CNN
F 3 "" H 9050 2700 50  0000 C CNN
	1    9050 2700
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 5A00E933
P 9050 2850
F 0 "#PWR?" H 9050 2600 50  0001 C CNN
F 1 "GND" H 9050 2700 50  0000 C CNN
F 2 "" H 9050 2850 50  0001 C CNN
F 3 "" H 9050 2850 50  0001 C CNN
	1    9050 2850
	1    0    0    -1  
$EndComp
Wire Wire Line
	8150 2150 8050 2150
Wire Wire Line
	8050 2150 8050 2400
Wire Wire Line
	8050 2400 7750 2400
$Comp
L +3.3V #PWR?
U 1 1 5A00E93C
P 7750 2400
F 0 "#PWR?" H 7750 2250 50  0001 C CNN
F 1 "+3.3V" H 7750 2540 50  0000 C CNN
F 2 "" H 7750 2400 50  0000 C CNN
F 3 "" H 7750 2400 50  0000 C CNN
	1    7750 2400
	-1   0    0    1   
$EndComp
Connection ~ 7900 2400
Wire Wire Line
	7900 2400 7900 2500
$Comp
L C C?
U 1 1 5A00E944
P 7900 2650
F 0 "C?" H 7925 2750 50  0000 L CNN
F 1 "0.1uF" H 7925 2550 50  0000 L CNN
F 2 "" H 7938 2500 50  0000 C CNN
F 3 "" H 7900 2650 50  0000 C CNN
	1    7900 2650
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 5A00E94B
P 7900 2800
F 0 "#PWR?" H 7900 2550 50  0001 C CNN
F 1 "GND" H 7900 2650 50  0000 C CNN
F 2 "" H 7900 2800 50  0001 C CNN
F 3 "" H 7900 2800 50  0001 C CNN
	1    7900 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7400 2050 8150 2050
Wire Wire Line
	8000 1950 8150 1950
Wire Wire Line
	8000 1450 8000 1950
Connection ~ 8000 1750
Wire Wire Line
	7250 1750 8000 1750
$Comp
L C C?
U 1 1 5A00E956
P 7850 1900
F 0 "C?" H 7875 2000 50  0000 L CNN
F 1 "0.1uF" H 7875 1800 50  0000 L CNN
F 2 "" H 7888 1750 50  0000 C CNN
F 3 "" H 7850 1900 50  0000 C CNN
	1    7850 1900
	1    0    0    -1  
$EndComp
Connection ~ 7850 1750
Connection ~ 7850 2050
Wire Wire Line
	7850 2050 7850 2200
Wire Wire Line
	7850 2200 7650 2200
$Comp
L C C?
U 1 1 5A00E961
P 7500 2200
F 0 "C?" H 7525 2300 50  0000 L CNN
F 1 "0.1uF" H 7525 2100 50  0000 L CNN
F 2 "" H 7538 2050 50  0000 C CNN
F 3 "" H 7500 2200 50  0000 C CNN
	1    7500 2200
	0    1    1    0   
$EndComp
$Comp
L GND #PWR?
U 1 1 5A00E968
P 7350 2200
F 0 "#PWR?" H 7350 1950 50  0001 C CNN
F 1 "GND" H 7350 2050 50  0000 C CNN
F 2 "" H 7350 2200 50  0001 C CNN
F 3 "" H 7350 2200 50  0001 C CNN
	1    7350 2200
	0    1    1    0   
$EndComp
$Comp
L C C?
U 1 1 5A00E96E
P 7850 1450
F 0 "C?" H 7875 1550 50  0000 L CNN
F 1 "0.1uF" H 7875 1350 50  0000 L CNN
F 2 "" H 7888 1300 50  0000 C CNN
F 3 "" H 7850 1450 50  0000 C CNN
	1    7850 1450
	0    1    1    0   
$EndComp
$Comp
L GND #PWR?
U 1 1 5A00E975
P 7700 1450
F 0 "#PWR?" H 7700 1200 50  0001 C CNN
F 1 "GND" H 7700 1300 50  0000 C CNN
F 2 "" H 7700 1450 50  0001 C CNN
F 3 "" H 7700 1450 50  0001 C CNN
	1    7700 1450
	0    1    1    0   
$EndComp
Wire Wire Line
	8150 1850 8050 1850
Wire Wire Line
	8050 1850 8050 1300
Wire Wire Line
	8050 1300 7400 1300
Wire Wire Line
	7400 1300 7400 1750
Wire Wire Line
	7400 2050 7400 1850
Wire Wire Line
	7400 1850 7250 1850
Connection ~ 7400 1750
$Comp
L LED D?
U 1 1 5A00E982
P 9450 1850
F 0 "D?" H 9450 1950 50  0000 C CNN
F 1 "LED" H 9450 1750 50  0000 C CNN
F 2 "" H 9450 1850 50  0001 C CNN
F 3 "" H 9450 1850 50  0001 C CNN
	1    9450 1850
	1    0    0    -1  
$EndComp
Wire Wire Line
	9050 1850 9300 1850
$Comp
L R R?
U 1 1 5A00E98A
P 9750 1850
F 0 "R?" V 9830 1850 50  0000 C CNN
F 1 "1k" V 9750 1850 50  0000 C CNN
F 2 "" V 9680 1850 50  0000 C CNN
F 3 "" H 9750 1850 50  0000 C CNN
	1    9750 1850
	0    1    1    0   
$EndComp
$Comp
L +3.3V #PWR?
U 1 1 5A00E991
P 9900 1850
F 0 "#PWR?" H 9900 1700 50  0001 C CNN
F 1 "+3.3V" H 9900 1990 50  0000 C CNN
F 2 "" H 9900 1850 50  0000 C CNN
F 3 "" H 9900 1850 50  0000 C CNN
	1    9900 1850
	0    1    1    0   
$EndComp
$EndSCHEMATC
