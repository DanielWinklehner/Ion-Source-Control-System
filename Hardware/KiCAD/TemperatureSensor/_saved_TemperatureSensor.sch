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
Sheet 1 2
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 4400 7050 1500 200 
U 5A00E52F
F0 "TempSensors" 60
F1 "tempsensors.sch" 60
$EndSheet
$Comp
L ARDUINO_MICRO_SHIELD U1
U 1 1 5A00EB35
P 1850 2000
F 0 "U1" H 3600 2400 60  0000 C CNN
F 1 "ARDUINO_MICRO_SHIELD" H 2700 2600 60  0000 C CNN
F 2 "TemperatureSensor:ARDUINO_MICRO_SHIELD" H 2250 1950 60  0001 C CNN
F 3 "" H 2250 1950 60  0000 C CNN
	1    1850 2000
	0    1    1    0   
$EndComp
Text GLabel 3000 2050 2    60   Input ~ 0
SCK
Text GLabel 1650 2050 0    60   Input ~ 0
SDO
Text GLabel 3000 2150 2    60   Input ~ 0
SDI
$Comp
L GND #PWR01
U 1 1 5A134B36
P 1650 2550
F 0 "#PWR01" H 1650 2300 50  0001 C CNN
F 1 "GND" H 1650 2400 50  0000 C CNN
F 2 "" H 1650 2550 50  0001 C CNN
F 3 "" H 1650 2550 50  0001 C CNN
	1    1650 2550
	0    1    1    0   
$EndComp
$Comp
L +5V #PWR02
U 1 1 5A134B4C
P 3000 2550
F 0 "#PWR02" H 3000 2400 50  0001 C CNN
F 1 "+5V" H 3000 2690 50  0000 C CNN
F 2 "" H 3000 2550 50  0001 C CNN
F 3 "" H 3000 2550 50  0001 C CNN
	1    3000 2550
	0    1    1    0   
$EndComp
$Comp
L GND #PWR03
U 1 1 5A134B61
P 3000 2350
F 0 "#PWR03" H 3000 2100 50  0001 C CNN
F 1 "GND" H 3000 2200 50  0000 C CNN
F 2 "" H 3000 2350 50  0001 C CNN
F 3 "" H 3000 2350 50  0001 C CNN
	1    3000 2350
	0    -1   -1   0   
$EndComp
Text GLabel 1650 2750 0    60   Input ~ 0
CS1
Text GLabel 1650 2850 0    60   Input ~ 0
CS2
Text GLabel 1650 2950 0    60   Input ~ 0
CS3
Text GLabel 1650 3050 0    60   Input ~ 0
CS4
NoConn ~ 3000 2850
NoConn ~ 3000 2950
NoConn ~ 3000 3050
NoConn ~ 3000 3150
NoConn ~ 3000 3250
NoConn ~ 3000 3350
NoConn ~ 3000 3450
NoConn ~ 3000 3550
NoConn ~ 3000 3650
NoConn ~ 3000 2450
NoConn ~ 3000 2250
NoConn ~ 1650 2150
NoConn ~ 1650 2250
NoConn ~ 1650 2350
NoConn ~ 1650 2650
NoConn ~ 1650 3150
NoConn ~ 1650 3250
NoConn ~ 1650 3350
NoConn ~ 1650 3450
NoConn ~ 1650 3550
NoConn ~ 1650 3650
$EndSCHEMATC
