EESchema Schematic File Version 2
LIBS:power
LIBS:device
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
LIBS:arduino_shieldsNCL
LIBS:adr4550
LIBS:PowerSupplyControl-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 4 5
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
L +5V #PWR85
U 1 1 5790E95B
P 3700 6700
F 0 "#PWR85" H 3700 6550 50  0001 C CNN
F 1 "+5V" H 3700 6840 50  0000 C CNN
F 2 "" H 3700 6700 50  0000 C CNN
F 3 "" H 3700 6700 50  0000 C CNN
	1    3700 6700
	1    0    0    -1  
$EndComp
Text GLabel 4850 7000 2    60   Input ~ 0
V_REF
$Comp
L GND #PWR86
U 1 1 5790E98A
P 3700 7200
F 0 "#PWR86" H 3700 6950 50  0001 C CNN
F 1 "GND" H 3700 7050 50  0000 C CNN
F 2 "" H 3700 7200 50  0000 C CNN
F 3 "" H 3700 7200 50  0000 C CNN
	1    3700 7200
	1    0    0    -1  
$EndComp
$Comp
L C C17
U 1 1 5790E9C5
P 3600 6950
F 0 "C17" H 3625 7050 50  0000 L CNN
F 1 "1uF" H 3625 6850 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 3638 6800 50  0001 C CNN
F 3 "" H 3600 6950 50  0000 C CNN
	1    3600 6950
	-1   0    0    1   
$EndComp
$Comp
L C C18
U 1 1 5790E9A0
P 3800 6950
F 0 "C18" H 3825 7050 50  0000 L CNN
F 1 ".1uF" H 3825 6850 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 3838 6800 50  0001 C CNN
F 3 "" H 3800 6950 50  0000 C CNN
	1    3800 6950
	-1   0    0    1   
$EndComp
$Comp
L C C19
U 1 1 5790EC0D
P 4800 7150
F 0 "C19" H 4825 7250 50  0000 L CNN
F 1 ".1uF" H 4825 7050 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 4838 7000 50  0001 C CNN
F 3 "" H 4800 7150 50  0000 C CNN
	1    4800 7150
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR87
U 1 1 5790EC57
P 4800 7300
F 0 "#PWR87" H 4800 7050 50  0001 C CNN
F 1 "GND" H 4800 7150 50  0000 C CNN
F 2 "" H 4800 7300 50  0000 C CNN
F 3 "" H 4800 7300 50  0000 C CNN
	1    4800 7300
	1    0    0    -1  
$EndComp
Wire Wire Line
	3700 6700 3700 6800
Wire Wire Line
	3600 6800 3800 6800
Connection ~ 3700 6800
Wire Wire Line
	3600 7100 3800 7100
Wire Wire Line
	3700 7100 3700 7200
Connection ~ 3700 7100
Wire Wire Line
	3700 7150 4050 7150
Wire Wire Line
	4050 7150 4050 7100
Wire Wire Line
	3700 6750 4050 6750
Wire Wire Line
	4050 6750 4050 6900
Connection ~ 3700 6750
Connection ~ 3700 7150
$Comp
L ADR4550 U4
U 1 1 5790ED40
P 4400 6750
F 0 "U4" H 4400 6900 60  0000 C CNN
F 1 "ADR4550" H 4450 6100 60  0000 C CNN
F 2 "Housings_SOIC:SOIC-8_3.9x4.9mm_Pitch1.27mm" H 4400 6750 60  0001 C CNN
F 3 "" H 4400 6750 60  0000 C CNN
	1    4400 6750
	1    0    0    -1  
$EndComp
Wire Wire Line
	4750 7000 4850 7000
Connection ~ 4800 7000
$EndSCHEMATC
