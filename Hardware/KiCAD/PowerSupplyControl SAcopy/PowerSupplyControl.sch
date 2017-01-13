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
Sheet 1 5
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 3200 1100 2    60   Input ~ 0
V_PWM1
Text GLabel 3200 1200 2    60   Input ~ 0
I_PWM1
Text GLabel 1300 1900 0    60   Input ~ 0
V_READING1
Text GLabel 1300 2100 0    60   Input ~ 0
I_READING1
Text GLabel 3200 4200 2    60   Input ~ 0
ON/OFF(P)1_CON
Text GLabel 3200 2000 2    60   Input ~ 0
ON/OFF(A)1
Text GLabel 3200 1300 2    60   Input ~ 0
V_PWM2
Text GLabel 3200 1400 2    60   Input ~ 0
I_PWM2
Text GLabel 1300 2200 0    60   Input ~ 0
V_READING2
Text GLabel 1300 2000 0    60   Input ~ 0
I_READING2
Text GLabel 3200 4400 2    60   Input ~ 0
ON/OFF(P)2_CON
Text GLabel 3200 2100 2    60   Input ~ 0
ON/OFF(A)2
Text GLabel 7200 800  0    60   Input ~ 0
V_MONITOR1
$Comp
L GND #PWR24
U 1 1 5787BC84
P 6600 1000
F 0 "#PWR24" H 6600 750 50  0001 C CNN
F 1 "GND" H 6600 850 50  0000 C CNN
F 2 "" H 6600 1000 50  0000 C CNN
F 3 "" H 6600 1000 50  0000 C CNN
	1    6600 1000
	0    1    1    0   
$EndComp
$Comp
L R R27
U 1 1 5787BC85
P 6750 1000
F 0 "R27" V 6830 1000 50  0000 C CNN
F 1 "13k" V 6750 1000 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 6680 1000 50  0001 C CNN
F 3 "" H 6750 1000 50  0000 C CNN
	1    6750 1000
	0    1    1    0   
$EndComp
$Comp
L GND #PWR28
U 1 1 5787BC86
P 7400 1200
F 0 "#PWR28" H 7400 950 50  0001 C CNN
F 1 "GND" H 7400 1050 50  0000 C CNN
F 2 "" H 7400 1200 50  0000 C CNN
F 3 "" H 7400 1200 50  0000 C CNN
	1    7400 1200
	0    -1   -1   0   
$EndComp
$Comp
L +12V #PWR27
U 1 1 5787BC87
P 7400 600
F 0 "#PWR27" H 7400 450 50  0001 C CNN
F 1 "+12V" H 7400 740 50  0000 C CNN
F 2 "" H 7400 600 50  0000 C CNN
F 3 "" H 7400 600 50  0000 C CNN
	1    7400 600 
	0    1    1    0   
$EndComp
$Comp
L R R31
U 1 1 5787BC8B
P 8100 1750
F 0 "R31" V 8180 1750 50  0000 C CNN
F 1 "13k" V 8100 1750 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8030 1750 50  0001 C CNN
F 3 "" H 8100 1750 50  0000 C CNN
	1    8100 1750
	0    1    1    0   
$EndComp
$Comp
L R R32
U 1 1 5787BC8C
P 8100 2100
F 0 "R32" V 8180 2100 50  0000 C CNN
F 1 "487k" V 8100 2100 50  0000 C CNN
F 2 "Resistors_SMD:R_0805" V 8030 2100 50  0001 C CNN
F 3 "" H 8100 2100 50  0000 C CNN
	1    8100 2100
	0    1    1    0   
$EndComp
$Comp
L R R35
U 1 1 5787BC8D
P 8450 1050
F 0 "R35" V 8530 1050 50  0000 C CNN
F 1 "1.4k" V 8450 1050 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8380 1050 50  0001 C CNN
F 3 "" H 8450 1050 50  0000 C CNN
	1    8450 1050
	1    0    0    -1  
$EndComp
$Comp
L R R36
U 1 1 5787BC8E
P 8450 1550
F 0 "R36" V 8530 1550 50  0000 C CNN
F 1 "1k" V 8450 1550 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8380 1550 50  0001 C CNN
F 3 "" H 8450 1550 50  0000 C CNN
	1    8450 1550
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR33
U 1 1 5787BC8F
P 8450 1700
F 0 "#PWR33" H 8450 1450 50  0001 C CNN
F 1 "GND" H 8450 1550 50  0000 C CNN
F 2 "" H 8450 1700 50  0000 C CNN
F 3 "" H 8450 1700 50  0000 C CNN
	1    8450 1700
	1    0    0    -1  
$EndComp
Text GLabel 8650 1300 3    60   Input ~ 0
V_READING1
Text GLabel 9650 1250 0    60   Input ~ 0
I_MONITOR1
$Comp
L GND #PWR34
U 1 1 5787BC90
P 9050 1450
F 0 "#PWR34" H 9050 1200 50  0001 C CNN
F 1 "GND" H 9050 1300 50  0000 C CNN
F 2 "" H 9050 1450 50  0000 C CNN
F 3 "" H 9050 1450 50  0000 C CNN
	1    9050 1450
	0    1    1    0   
$EndComp
$Comp
L R R39
U 1 1 5787BC91
P 9200 1450
F 0 "R39" V 9280 1450 50  0000 C CNN
F 1 "13k" V 9200 1450 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 9130 1450 50  0001 C CNN
F 3 "" H 9200 1450 50  0000 C CNN
	1    9200 1450
	0    1    1    0   
$EndComp
$Comp
L GND #PWR38
U 1 1 5787BC92
P 9850 1650
F 0 "#PWR38" H 9850 1400 50  0001 C CNN
F 1 "GND" H 9850 1500 50  0000 C CNN
F 2 "" H 9850 1650 50  0000 C CNN
F 3 "" H 9850 1650 50  0000 C CNN
	1    9850 1650
	0    -1   -1   0   
$EndComp
$Comp
L +12V #PWR37
U 1 1 5787BC93
P 9850 1050
F 0 "#PWR37" H 9850 900 50  0001 C CNN
F 1 "+12V" H 9850 1190 50  0000 C CNN
F 2 "" H 9850 1050 50  0000 C CNN
F 3 "" H 9850 1050 50  0000 C CNN
	1    9850 1050
	0    1    1    0   
$EndComp
$Comp
L R R43
U 1 1 5787BC97
P 10550 2200
F 0 "R43" V 10630 2200 50  0000 C CNN
F 1 "13k" V 10550 2200 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10480 2200 50  0001 C CNN
F 3 "" H 10550 2200 50  0000 C CNN
	1    10550 2200
	0    1    1    0   
$EndComp
$Comp
L R R44
U 1 1 5787BC98
P 10550 2550
F 0 "R44" V 10630 2550 50  0000 C CNN
F 1 "487k" V 10550 2550 50  0000 C CNN
F 2 "Resistors_SMD:R_0805" V 10480 2550 50  0001 C CNN
F 3 "" H 10550 2550 50  0000 C CNN
	1    10550 2550
	0    1    1    0   
$EndComp
$Comp
L R R48
U 1 1 5787BC99
P 10900 1500
F 0 "R48" V 10980 1500 50  0000 C CNN
F 1 "1.4k" V 10900 1500 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10830 1500 50  0001 C CNN
F 3 "" H 10900 1500 50  0000 C CNN
	1    10900 1500
	1    0    0    -1  
$EndComp
$Comp
L R R49
U 1 1 5787BC9A
P 10900 2000
F 0 "R49" V 10980 2000 50  0000 C CNN
F 1 "1k" V 10900 2000 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10830 2000 50  0001 C CNN
F 3 "" H 10900 2000 50  0000 C CNN
	1    10900 2000
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR46
U 1 1 5787BC9B
P 10900 2150
F 0 "#PWR46" H 10900 1900 50  0001 C CNN
F 1 "GND" H 10900 2000 50  0000 C CNN
F 2 "" H 10900 2150 50  0000 C CNN
F 3 "" H 10900 2150 50  0000 C CNN
	1    10900 2150
	1    0    0    -1  
$EndComp
Text GLabel 11150 1750 3    60   Input ~ 0
I_READING1
Text GLabel 7150 2400 0    60   Input ~ 0
V_MONITOR2
$Comp
L GND #PWR23
U 1 1 5787BC9C
P 6550 2600
F 0 "#PWR23" H 6550 2350 50  0001 C CNN
F 1 "GND" H 6550 2450 50  0000 C CNN
F 2 "" H 6550 2600 50  0000 C CNN
F 3 "" H 6550 2600 50  0000 C CNN
	1    6550 2600
	0    1    1    0   
$EndComp
$Comp
L R R26
U 1 1 5787BC9D
P 6700 2600
F 0 "R26" V 6780 2600 50  0000 C CNN
F 1 "13k" V 6700 2600 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 6630 2600 50  0001 C CNN
F 3 "" H 6700 2600 50  0000 C CNN
	1    6700 2600
	0    1    1    0   
$EndComp
$Comp
L GND #PWR26
U 1 1 5787BC9E
P 7350 2800
F 0 "#PWR26" H 7350 2550 50  0001 C CNN
F 1 "GND" H 7350 2650 50  0000 C CNN
F 2 "" H 7350 2800 50  0000 C CNN
F 3 "" H 7350 2800 50  0000 C CNN
	1    7350 2800
	0    -1   -1   0   
$EndComp
$Comp
L +12V #PWR25
U 1 1 5787BC9F
P 7350 2200
F 0 "#PWR25" H 7350 2050 50  0001 C CNN
F 1 "+12V" H 7350 2340 50  0000 C CNN
F 2 "" H 7350 2200 50  0000 C CNN
F 3 "" H 7350 2200 50  0000 C CNN
	1    7350 2200
	0    1    1    0   
$EndComp
$Comp
L R R29
U 1 1 5787BCA3
P 8050 3350
F 0 "R29" V 8130 3350 50  0000 C CNN
F 1 "13k" V 8050 3350 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 7980 3350 50  0001 C CNN
F 3 "" H 8050 3350 50  0000 C CNN
	1    8050 3350
	0    1    1    0   
$EndComp
$Comp
L R R30
U 1 1 5787BCA4
P 8050 3700
F 0 "R30" V 8130 3700 50  0000 C CNN
F 1 "487k" V 8050 3700 50  0000 C CNN
F 2 "Resistors_SMD:R_0805" V 7980 3700 50  0001 C CNN
F 3 "" H 8050 3700 50  0000 C CNN
	1    8050 3700
	0    1    1    0   
$EndComp
$Comp
L R R33
U 1 1 5787BCA5
P 8400 2650
F 0 "R33" V 8480 2650 50  0000 C CNN
F 1 "1.4k" V 8400 2650 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8330 2650 50  0001 C CNN
F 3 "" H 8400 2650 50  0000 C CNN
	1    8400 2650
	1    0    0    -1  
$EndComp
$Comp
L R R34
U 1 1 5787BCA6
P 8400 3150
F 0 "R34" V 8480 3150 50  0000 C CNN
F 1 "1k" V 8400 3150 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8330 3150 50  0001 C CNN
F 3 "" H 8400 3150 50  0000 C CNN
	1    8400 3150
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR32
U 1 1 5787BCA7
P 8400 3300
F 0 "#PWR32" H 8400 3050 50  0001 C CNN
F 1 "GND" H 8400 3150 50  0000 C CNN
F 2 "" H 8400 3300 50  0000 C CNN
F 3 "" H 8400 3300 50  0000 C CNN
	1    8400 3300
	1    0    0    -1  
$EndComp
Text GLabel 8650 2900 3    60   Input ~ 0
V_READING2
Text GLabel 9700 2850 0    60   Input ~ 0
I_MONITOR2
$Comp
L GND #PWR35
U 1 1 5787BCA8
P 9100 3050
F 0 "#PWR35" H 9100 2800 50  0001 C CNN
F 1 "GND" H 9100 2900 50  0000 C CNN
F 2 "" H 9100 3050 50  0000 C CNN
F 3 "" H 9100 3050 50  0000 C CNN
	1    9100 3050
	0    1    1    0   
$EndComp
$Comp
L R R38
U 1 1 5787BCA9
P 9250 3050
F 0 "R38" V 9330 3050 50  0000 C CNN
F 1 "13k" V 9250 3050 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 9180 3050 50  0001 C CNN
F 3 "" H 9250 3050 50  0000 C CNN
	1    9250 3050
	0    1    1    0   
$EndComp
$Comp
L GND #PWR40
U 1 1 5787BCAA
P 9900 3250
F 0 "#PWR40" H 9900 3000 50  0001 C CNN
F 1 "GND" H 9900 3100 50  0000 C CNN
F 2 "" H 9900 3250 50  0000 C CNN
F 3 "" H 9900 3250 50  0000 C CNN
	1    9900 3250
	0    -1   -1   0   
$EndComp
$Comp
L +12V #PWR39
U 1 1 5787BCAB
P 9900 2650
F 0 "#PWR39" H 9900 2500 50  0001 C CNN
F 1 "+12V" H 9900 2790 50  0000 C CNN
F 2 "" H 9900 2650 50  0000 C CNN
F 3 "" H 9900 2650 50  0000 C CNN
	1    9900 2650
	0    1    1    0   
$EndComp
$Comp
L R R41
U 1 1 5787BCAF
P 10600 3800
F 0 "R41" V 10680 3800 50  0000 C CNN
F 1 "13k" V 10600 3800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10530 3800 50  0001 C CNN
F 3 "" H 10600 3800 50  0000 C CNN
	1    10600 3800
	0    1    1    0   
$EndComp
$Comp
L R R42
U 1 1 5787BCB0
P 10600 4150
F 0 "R42" V 10680 4150 50  0000 C CNN
F 1 "487k" V 10600 4150 50  0000 C CNN
F 2 "Resistors_SMD:R_0805" V 10530 4150 50  0001 C CNN
F 3 "" H 10600 4150 50  0000 C CNN
	1    10600 4150
	0    1    1    0   
$EndComp
$Comp
L R R46
U 1 1 5787BCB1
P 10950 3100
F 0 "R46" V 11030 3100 50  0000 C CNN
F 1 "1.4k" V 10950 3100 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10880 3100 50  0001 C CNN
F 3 "" H 10950 3100 50  0000 C CNN
	1    10950 3100
	1    0    0    -1  
$EndComp
$Comp
L R R47
U 1 1 5787BCB2
P 10950 3600
F 0 "R47" V 11030 3600 50  0000 C CNN
F 1 "1k" V 10950 3600 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10880 3600 50  0001 C CNN
F 3 "" H 10950 3600 50  0000 C CNN
	1    10950 3600
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR47
U 1 1 5787BCB3
P 10950 3750
F 0 "#PWR47" H 10950 3500 50  0001 C CNN
F 1 "GND" H 10950 3600 50  0000 C CNN
F 2 "" H 10950 3750 50  0000 C CNN
F 3 "" H 10950 3750 50  0000 C CNN
	1    10950 3750
	1    0    0    -1  
$EndComp
Text GLabel 11150 3350 3    60   Input ~ 0
I_READING2
$Comp
L LM324N U2
U 4 1 5787BCB6
P 10000 2950
F 0 "U2" H 10050 3150 50  0000 C CNN
F 1 "LM324N" H 10150 2750 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 9950 3050 50  0001 C CNN
F 3 "" H 10050 3150 50  0000 C CNN
	4    10000 2950
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR16
U 1 1 5787BCBB
P 4350 1350
F 0 "#PWR16" H 4350 1100 50  0001 C CNN
F 1 "GND" H 4350 1200 50  0000 C CNN
F 2 "" H 4350 1350 50  0000 C CNN
F 3 "" H 4350 1350 50  0000 C CNN
	1    4350 1350
	0    1    1    0   
$EndComp
$Comp
L +12V #PWR17
U 1 1 5787BCBC
P 4450 1350
F 0 "#PWR17" H 4450 1200 50  0001 C CNN
F 1 "+12V" H 4550 1500 50  0000 C CNN
F 2 "" H 4450 1350 50  0000 C CNN
F 3 "" H 4450 1350 50  0000 C CNN
	1    4450 1350
	-1   0    0    1   
$EndComp
$Comp
L +12V #PWR45
U 1 1 5787BCBD
P 10900 700
F 0 "#PWR45" H 10900 550 50  0001 C CNN
F 1 "+12V" H 10900 840 50  0000 C CNN
F 2 "" H 10900 700 50  0000 C CNN
F 3 "" H 10900 700 50  0000 C CNN
	1    10900 700 
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR44
U 1 1 5787BCBE
P 10450 700
F 0 "#PWR44" H 10450 450 50  0001 C CNN
F 1 "GND" H 10450 550 50  0000 C CNN
F 2 "" H 10450 700 50  0000 C CNN
F 3 "" H 10450 700 50  0000 C CNN
	1    10450 700 
	-1   0    0    1   
$EndComp
$Comp
L PWR_FLAG #FLG3
U 1 1 5787BCBF
P 10900 700
F 0 "#FLG3" H 10900 795 50  0001 C CNN
F 1 "PWR_FLAG" H 10900 880 50  0000 C CNN
F 2 "" H 10900 700 50  0000 C CNN
F 3 "" H 10900 700 50  0000 C CNN
	1    10900 700 
	-1   0    0    1   
$EndComp
$Comp
L PWR_FLAG #FLG2
U 1 1 5787BCC0
P 10450 700
F 0 "#FLG2" H 10450 795 50  0001 C CNN
F 1 "PWR_FLAG" H 10450 880 50  0000 C CNN
F 2 "" H 10450 700 50  0000 C CNN
F 3 "" H 10450 700 50  0000 C CNN
	1    10450 700 
	-1   0    0    1   
$EndComp
Text GLabel 5300 2950 2    60   Input ~ 0
V_CONTROL2
Text GLabel 5300 3050 2    60   Input ~ 0
I_CONTROL2
Text GLabel 5300 3150 2    60   Input ~ 0
V_MONITOR2
Text GLabel 5300 3250 2    60   Input ~ 0
I_MONITOR2
Text GLabel 5250 4350 2    60   Input ~ 0
V_CONTROL1
Text GLabel 5250 4450 2    60   Input ~ 0
I_CONTROL1
Text GLabel 5250 4550 2    60   Input ~ 0
V_MONITOR1
Text GLabel 5250 4650 2    60   Input ~ 0
I_MONITOR1
$Comp
L +5V #PWR41
U 1 1 5787CAE7
P 10000 700
F 0 "#PWR41" H 10000 550 50  0001 C CNN
F 1 "+5V" H 10000 840 50  0000 C CNN
F 2 "" H 10000 700 50  0000 C CNN
F 3 "" H 10000 700 50  0000 C CNN
	1    10000 700 
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG1
U 1 1 5787CB99
P 10000 700
F 0 "#FLG1" H 10000 795 50  0001 C CNN
F 1 "PWR_FLAG" H 10000 880 50  0000 C CNN
F 2 "" H 10000 700 50  0000 C CNN
F 3 "" H 10000 700 50  0000 C CNN
	1    10000 700 
	-1   0    0    1   
$EndComp
Text GLabel 3200 3800 2    60   Input ~ 0
INTERLOCK1_CON
Text GLabel 3200 4000 2    60   Input ~ 0
INTERLOCK2_CON
Text GLabel 3200 4650 2    60   Input ~ 0
HV_INDICATOR1
Text GLabel 1300 5150 0    60   Input ~ 0
HV_INDICATOR2
Text GLabel 1300 4950 0    60   Input ~ 0
TRIP2
Text GLabel 3200 4850 2    60   Input ~ 0
TRIP1
Text GLabel 3200 5050 2    60   Input ~ 0
LOCAL/REMOTE1
Text GLabel 1300 4750 0    60   Input ~ 0
LOCAL/REMOTE2
Text GLabel 3200 5250 2    60   Input ~ 0
ARC_MONITOR1
Text GLabel 1300 4550 0    60   Input ~ 0
ARC_MONITOR2
$Comp
L GND #PWR5
U 1 1 577D84A9
P 1300 3750
F 0 "#PWR5" H 1300 3500 50  0001 C CNN
F 1 "GND" H 1300 3600 50  0000 C CNN
F 2 "" H 1300 3750 50  0000 C CNN
F 3 "" H 1300 3750 50  0000 C CNN
	1    1300 3750
	0    1    1    0   
$EndComp
Text GLabel 3200 4950 2    60   Input ~ 0
COM
Text GLabel 1300 5500 0    60   Input ~ 0
ERROR
Text GLabel 1300 5600 0    60   Input ~ 0
V_STATUS1
Text GLabel 1300 5400 0    60   Input ~ 0
I_STATUS1
Text GLabel 1300 4300 0    60   Input ~ 0
V_STATUS2
Text GLabel 1300 4100 0    60   Input ~ 0
I_STATUS2
Text GLabel 5300 3750 2    60   Input ~ 0
ON/OFF(A)2_10V
Text GLabel 5300 3450 2    60   Input ~ 0
ON/OFF(P)2_OUT
Text GLabel 8600 5550 2    60   Input ~ 0
HV_INDICATOR2_OUT
Text GLabel 8600 5650 2    60   Input ~ 0
TRIP2_OUT
Text GLabel 8600 5850 2    60   Input ~ 0
ARC_MONITOR2_OUT
Text GLabel 5250 5150 2    60   Input ~ 0
ON/OFF(A)1_10V
Text GLabel 5250 4750 2    60   Input ~ 0
ON/OFF(P)1_IN
Text GLabel 6850 5600 2    60   Input ~ 0
HV_INDICATOR1_OUT
Text GLabel 6850 5700 2    60   Input ~ 0
TRIP1_OUT
Text GLabel 6850 5800 2    60   Input ~ 0
LOCAL/REMOTE1_OUT
Text GLabel 6850 5900 2    60   Input ~ 0
ARC_MONITOR1_OUT
Text GLabel 6850 6000 2    60   Input ~ 0
V_STATUS1_OUT
Text GLabel 6850 6100 2    60   Input ~ 0
I_STATUS1_OUT
$Comp
L CONN_01X08 P9
U 1 1 578816CF
P 5200 7100
F 0 "P9" H 5200 7550 50  0000 C CNN
F 1 "FROM RELAY" V 5300 7100 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x08" H 5200 7100 50  0001 C CNN
F 3 "" H 5200 7100 50  0000 C CNN
	1    5200 7100
	0    1    1    0   
$EndComp
$Comp
L LM324N U3
U 3 1 5788DF5B
P 8200 4800
F 0 "U3" H 8250 5000 50  0000 C CNN
F 1 "LM324N" H 8350 4600 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 8150 4900 50  0001 C CNN
F 3 "" H 8250 5000 50  0000 C CNN
	3    8200 4800
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR6
U 1 1 5789086A
P 1300 3850
F 0 "#PWR6" H 1300 3600 50  0001 C CNN
F 1 "GND" H 1300 3700 50  0000 C CNN
F 2 "" H 1300 3850 50  0000 C CNN
F 3 "" H 1300 3850 50  0000 C CNN
	1    1300 3850
	0    1    1    0   
$EndComp
Text GLabel 7900 4700 0    60   Input ~ 0
ON/OFF(A)1
$Comp
L GND #PWR31
U 1 1 5787BF33
P 8100 5100
F 0 "#PWR31" H 8100 4850 50  0001 C CNN
F 1 "GND" H 8100 4950 50  0000 C CNN
F 2 "" H 8100 5100 50  0000 C CNN
F 3 "" H 8100 5100 50  0000 C CNN
	1    8100 5100
	1    0    0    -1  
$EndComp
$Comp
L +12V #PWR30
U 1 1 5787BFE3
P 8100 4500
F 0 "#PWR30" H 8100 4350 50  0001 C CNN
F 1 "+12V" H 8100 4640 50  0000 C CNN
F 2 "" H 8100 4500 50  0000 C CNN
F 3 "" H 8100 4500 50  0000 C CNN
	1    8100 4500
	1    0    0    -1  
$EndComp
$Comp
L R R37
U 1 1 5787F3DB
P 8650 4800
F 0 "R37" V 8730 4800 50  0000 C CNN
F 1 "20k" V 8650 4800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 8580 4800 50  0001 C CNN
F 3 "" H 8650 4800 50  0000 C CNN
	1    8650 4800
	0    1    1    0   
$EndComp
$Comp
L R R28
U 1 1 5787F508
P 7650 4900
F 0 "R28" V 7730 4900 50  0000 C CNN
F 1 "20k" V 7650 4900 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 7580 4900 50  0001 C CNN
F 3 "" H 7650 4900 50  0000 C CNN
	1    7650 4900
	0    1    1    0   
$EndComp
Text GLabel 8900 4500 3    60   Input ~ 0
ON/OFF(A)1_10V
$Comp
L LM324N U3
U 2 1 57880B36
P 10150 4750
F 0 "U3" H 10200 4950 50  0000 C CNN
F 1 "LM324N" H 10300 4550 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 10100 4850 50  0001 C CNN
F 3 "" H 10200 4950 50  0000 C CNN
	2    10150 4750
	1    0    0    -1  
$EndComp
Text GLabel 9850 4650 0    60   Input ~ 0
ON/OFF(A)2
$Comp
L GND #PWR43
U 1 1 57880B3D
P 10050 5050
F 0 "#PWR43" H 10050 4800 50  0001 C CNN
F 1 "GND" H 10050 4900 50  0000 C CNN
F 2 "" H 10050 5050 50  0000 C CNN
F 3 "" H 10050 5050 50  0000 C CNN
	1    10050 5050
	1    0    0    -1  
$EndComp
$Comp
L +12V #PWR42
U 1 1 57880B43
P 10050 4450
F 0 "#PWR42" H 10050 4300 50  0001 C CNN
F 1 "+12V" H 10050 4590 50  0000 C CNN
F 2 "" H 10050 4450 50  0000 C CNN
F 3 "" H 10050 4450 50  0000 C CNN
	1    10050 4450
	1    0    0    -1  
$EndComp
$Comp
L R R45
U 1 1 57880B49
P 10600 4750
F 0 "R45" V 10680 4750 50  0000 C CNN
F 1 "20k" V 10600 4750 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 10530 4750 50  0001 C CNN
F 3 "" H 10600 4750 50  0000 C CNN
	1    10600 4750
	0    1    1    0   
$EndComp
$Comp
L R R40
U 1 1 57880B4F
P 9600 4850
F 0 "R40" V 9680 4850 50  0000 C CNN
F 1 "20k" V 9600 4850 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 9530 4850 50  0001 C CNN
F 3 "" H 9600 4850 50  0000 C CNN
	1    9600 4850
	0    1    1    0   
$EndComp
Text GLabel 10850 4450 3    60   Input ~ 0
ON/OFF(A)2_10V
$Comp
L GND #PWR29
U 1 1 57880F06
P 7500 4900
F 0 "#PWR29" H 7500 4650 50  0001 C CNN
F 1 "GND" H 7500 4750 50  0000 C CNN
F 2 "" H 7500 4900 50  0000 C CNN
F 3 "" H 7500 4900 50  0000 C CNN
	1    7500 4900
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR36
U 1 1 5788100A
P 9450 4850
F 0 "#PWR36" H 9450 4600 50  0001 C CNN
F 1 "GND" H 9450 4700 50  0000 C CNN
F 2 "" H 9450 4850 50  0000 C CNN
F 3 "" H 9450 4850 50  0000 C CNN
	1    9450 4850
	1    0    0    -1  
$EndComp
Text GLabel 3300 6650 1    60   Input ~ 0
COM
$Comp
L R R8
U 1 1 5788B251
P 3300 6800
F 0 "R8" V 3400 6650 50  0000 C CNN
F 1 "1k" V 3300 6800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 3230 6800 50  0001 C CNN
F 3 "" H 3300 6800 50  0000 C CNN
	1    3300 6800
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR11
U 1 1 5788BCA6
P 3400 6950
F 0 "#PWR11" H 3400 6700 50  0001 C CNN
F 1 "GND" V 3400 6750 50  0000 C CNN
F 2 "" H 3400 6950 50  0000 C CNN
F 3 "" H 3400 6950 50  0000 C CNN
	1    3400 6950
	-1   0    0    1   
$EndComp
Text GLabel 3900 6650 1    60   Input ~ 0
ERROR
$Comp
L GND #PWR12
U 1 1 5788BEAB
P 3600 6950
F 0 "#PWR12" H 3600 6700 50  0001 C CNN
F 1 "GND" V 3600 6750 50  0000 C CNN
F 2 "" H 3600 6950 50  0000 C CNN
F 3 "" H 3600 6950 50  0000 C CNN
	1    3600 6950
	-1   0    0    1   
$EndComp
Text GLabel 4100 6950 1    60   Input ~ 0
RESET
$Comp
L R R11
U 1 1 5788C3EC
P 3900 6800
F 0 "R11" V 4000 6600 50  0000 C CNN
F 1 "1k" V 3900 6800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 3830 6800 50  0001 C CNN
F 3 "" H 3900 6800 50  0000 C CNN
	1    3900 6800
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR14
U 1 1 57897029
P 4000 6950
F 0 "#PWR14" H 4000 6700 50  0001 C CNN
F 1 "GND" V 4000 6750 50  0000 C CNN
F 2 "" H 4000 6950 50  0000 C CNN
F 3 "" H 4000 6950 50  0000 C CNN
	1    4000 6950
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR13
U 1 1 57897182
P 3800 6950
F 0 "#PWR13" H 3800 6700 50  0001 C CNN
F 1 "GND" V 3800 6750 50  0000 C CNN
F 2 "" H 3800 6950 50  0000 C CNN
F 3 "" H 3800 6950 50  0000 C CNN
	1    3800 6950
	-1   0    0    1   
$EndComp
Text GLabel 3200 5150 2    60   Input ~ 0
OPEN
Text GLabel 3200 5350 2    60   Input ~ 0
CLOSED
$Comp
L CONN_01X10 P3
U 1 1 578995A3
P 3750 7150
F 0 "P3" H 3750 7700 50  0000 C CNN
F 1 "FRONT PLATE" V 3850 7150 50  0000 C CNN
F 2 "Terminal_Blocks:TerminalBlock_Pheonix_PT-3.5mm_10pol" H 3750 7150 50  0001 C CNN
F 3 "" H 3750 7150 50  0000 C CNN
	1    3750 7150
	0    1    1    0   
$EndComp
$Comp
L GND #PWR15
U 1 1 578996C1
P 4200 6950
F 0 "#PWR15" H 4200 6700 50  0001 C CNN
F 1 "GND" V 4200 6750 50  0000 C CNN
F 2 "" H 4200 6950 50  0000 C CNN
F 3 "" H 4200 6950 50  0000 C CNN
	1    4200 6950
	-1   0    0    1   
$EndComp
Text GLabel 3500 6650 1    60   Input ~ 0
OPEN
Text GLabel 3700 6650 1    60   Input ~ 0
CLOSED
$Comp
L R R18
U 1 1 57899B6B
P 3700 6800
F 0 "R18" V 3800 6600 50  0000 C CNN
F 1 "1k" V 3700 6800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 3630 6800 50  0001 C CNN
F 3 "" H 3700 6800 50  0000 C CNN
	1    3700 6800
	-1   0    0    1   
$EndComp
$Comp
L R R19
U 1 1 57899C89
P 3500 6800
F 0 "R19" V 3600 6600 50  0000 C CNN
F 1 "1k" V 3500 6800 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 3430 6800 50  0001 C CNN
F 3 "" H 3500 6800 50  0000 C CNN
	1    3500 6800
	-1   0    0    1   
$EndComp
$Comp
L +5V #PWR18
U 1 1 5789C208
P 4550 1350
F 0 "#PWR18" H 4550 1200 50  0001 C CNN
F 1 "+5V" H 4500 1500 50  0000 C CNN
F 2 "" H 4550 1350 50  0000 C CNN
F 3 "" H 4550 1350 50  0000 C CNN
	1    4550 1350
	-1   0    0    1   
$EndComp
$Comp
L +5V #PWR22
U 1 1 5789DB9D
P 5450 1350
F 0 "#PWR22" H 5450 1200 50  0001 C CNN
F 1 "+5V" H 5450 1490 50  0000 C CNN
F 2 "" H 5450 1350 50  0000 C CNN
F 3 "" H 5450 1350 50  0000 C CNN
	1    5450 1350
	0    -1   -1   0   
$EndComp
Text GLabel 5550 1350 3    60   Input ~ 0
EXTERNAL_INTERLOCK
Text GLabel 5200 1750 0    60   Input ~ 0
EXTERNAL_INTERLOCK
$Comp
L R R5
U 1 1 578A01FC
P 5250 1950
F 0 "R5" V 5330 1950 50  0000 C CNN
F 1 "10k" V 5250 1950 50  0000 C CNN
F 2 "Resistors_SMD:R_0603" V 5180 1950 50  0001 C CNN
F 3 "" H 5250 1950 50  0000 C CNN
	1    5250 1950
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR19
U 1 1 578A045E
P 5250 2100
F 0 "#PWR19" H 5250 1850 50  0001 C CNN
F 1 "GND" H 5250 1950 50  0000 C CNN
F 2 "" H 5250 2100 50  0000 C CNN
F 3 "" H 5250 2100 50  0000 C CNN
	1    5250 2100
	1    0    0    -1  
$EndComp
$Sheet
S 4850 7450 500  150 
U 578A7053
F0 "monitors" 60
F1 "file578A7052.sch" 60
$EndSheet
$Sheet
S 5900 7450 500  150 
U 578C3E8C
F0 "Temp Sensors" 60
F1 "file578C3E8B.sch" 60
$EndSheet
Text GLabel 8600 6050 2    60   Input ~ 0
I_STATUS2_OUT
Text GLabel 8600 5950 2    60   Input ~ 0
V_STATUS2_OUT
Text GLabel 8600 5750 2    60   Input ~ 0
LOCAL/REMOTE2_OUT
$Comp
L CONN_01X06 P5
U 1 1 578A13D9
P 6650 5850
F 0 "P5" H 6650 6200 50  0000 C CNN
F 1 "INDICATOR 1" V 6750 5850 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x06" H 6650 5850 50  0001 C CNN
F 3 "" H 6650 5850 50  0000 C CNN
	1    6650 5850
	-1   0    0    1   
$EndComp
$Comp
L CONN_01X06 P7
U 1 1 578A17E7
P 8400 5800
F 0 "P7" H 8400 6150 50  0000 C CNN
F 1 "INDICATOR 2" V 8500 5800 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x06" H 8400 5800 50  0001 C CNN
F 3 "" H 8400 5800 50  0000 C CNN
	1    8400 5800
	-1   0    0    1   
$EndComp
$Comp
L CONN_01X10 P4
U 1 1 578A6977
P 5050 4800
F 0 "P4" H 5050 5350 50  0000 C CNN
F 1 "PS CONTROL 1" V 5150 4800 50  0000 C CNN
F 2 "Terminal_Blocks:TerminalBlock_Pheonix_PT-3.5mm_10pol" H 5050 4800 50  0001 C CNN
F 3 "" H 5050 4800 50  0000 C CNN
	1    5050 4800
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR20
U 1 1 578A71C1
P 5250 5250
F 0 "#PWR20" H 5250 5000 50  0001 C CNN
F 1 "GND" H 5250 5100 50  0000 C CNN
F 2 "" H 5250 5250 50  0000 C CNN
F 3 "" H 5250 5250 50  0000 C CNN
	1    5250 5250
	1    0    0    -1  
$EndComp
Text GLabel 5250 4850 2    60   Input ~ 0
ON/OFF(P)1_OUT
Text GLabel 5250 4950 2    60   Input ~ 0
OPEN/CLOSE1_IN
Text GLabel 5250 5050 2    60   Input ~ 0
OPEN/CLOSE1_OUT
$Comp
L CONN_01X10 P6
U 1 1 578AB02C
P 5100 3400
F 0 "P6" H 5100 3950 50  0000 C CNN
F 1 "PS CONTROL 2" V 5200 3400 50  0000 C CNN
F 2 "Terminal_Blocks:TerminalBlock_Pheonix_PT-3.5mm_10pol" H 5100 3400 50  0001 C CNN
F 3 "" H 5100 3400 50  0000 C CNN
	1    5100 3400
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR21
U 1 1 578AB35A
P 5300 3850
F 0 "#PWR21" H 5300 3600 50  0001 C CNN
F 1 "GND" H 5300 3700 50  0000 C CNN
F 2 "" H 5300 3850 50  0000 C CNN
F 3 "" H 5300 3850 50  0000 C CNN
	1    5300 3850
	1    0    0    -1  
$EndComp
Text GLabel 5300 3350 2    60   Input ~ 0
ON/OFF(P)2_IN
Text GLabel 5300 3550 2    60   Input ~ 0
OPEN/CLOSE2_IN
Text GLabel 5300 3650 2    60   Input ~ 0
OPEN/CLOSE2_OUT
Text GLabel 5050 6900 1    60   Input ~ 0
OPEN/CLOSE1_IN
Text GLabel 5150 6900 1    60   Input ~ 0
OPEN/CLOSE1_OUT
Text GLabel 4850 6900 1    60   Input ~ 0
ON/OFF(P)1_IN
Text GLabel 4950 6900 1    60   Input ~ 0
ON/OFF(P)1_OUT
Text GLabel 5350 6900 1    60   Input ~ 0
ON/OFF(P)2_OUT
Text GLabel 5250 6900 1    60   Input ~ 0
ON/OFF(P)2_IN
Text GLabel 5450 6900 1    60   Input ~ 0
OPEN/CLOSE2_IN
Text GLabel 5550 6900 1    60   Input ~ 0
OPEN/CLOSE2_OUT
$Comp
L +5V #PWR9
U 1 1 578B61BB
P 3200 3550
F 0 "#PWR9" H 3200 3400 50  0001 C CNN
F 1 "+5V" H 3200 3690 50  0000 C CNN
F 2 "" H 3200 3550 50  0000 C CNN
F 3 "" H 3200 3550 50  0000 C CNN
	1    3200 3550
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR10
U 1 1 578B62D7
P 3300 3650
F 0 "#PWR10" H 3300 3500 50  0001 C CNN
F 1 "+5V" H 3300 3790 50  0000 C CNN
F 2 "" H 3300 3650 50  0000 C CNN
F 3 "" H 3300 3650 50  0000 C CNN
	1    3300 3650
	1    0    0    -1  
$EndComp
Text GLabel 3200 3300 2    60   Input ~ 0
EXTERNAL_INTERLOCK
Text GLabel 3200 3900 2    60   Input ~ 0
CS1
Text GLabel 3200 4100 2    60   Input ~ 0
CS2
Text GLabel 3200 4300 2    60   Input ~ 0
SCK
Text GLabel 3200 4500 2    60   Input ~ 0
SDI
Text GLabel 3200 4750 2    60   Input ~ 0
SDO
NoConn ~ 1300 1300
NoConn ~ 1300 1600
NoConn ~ 1300 1700
NoConn ~ 1300 2400
NoConn ~ 1300 2500
NoConn ~ 1300 2600
NoConn ~ 1300 2800
NoConn ~ 1300 2900
NoConn ~ 1300 3000
NoConn ~ 1300 3100
NoConn ~ 1300 3200
NoConn ~ 1300 3300
NoConn ~ 1300 3400
NoConn ~ 1300 3500
NoConn ~ 3200 3200
NoConn ~ 3200 3100
NoConn ~ 3200 2400
NoConn ~ 3200 2300
NoConn ~ 3200 1000
NoConn ~ 3200 900 
$Comp
L GND #PWR4
U 1 1 578CA289
P 1300 1500
F 0 "#PWR4" H 1300 1250 50  0001 C CNN
F 1 "GND" H 1300 1350 50  0000 C CNN
F 2 "" H 1300 1500 50  0000 C CNN
F 3 "" H 1300 1500 50  0000 C CNN
	1    1300 1500
	0    1    1    0   
$EndComp
$Comp
L +5V #PWR3
U 1 1 578CA8D6
P 1300 1400
F 0 "#PWR3" H 1300 1250 50  0001 C CNN
F 1 "+5V" H 1300 1540 50  0000 C CNN
F 2 "" H 1300 1400 50  0000 C CNN
F 3 "" H 1300 1400 50  0000 C CNN
	1    1300 1400
	0    -1   -1   0   
$EndComp
Text GLabel 1300 1200 0    60   Input ~ 0
RESET
$Comp
L CONN_01X04 P1
U 1 1 578CE164
P 4500 1150
F 0 "P1" H 4500 1400 50  0000 C CNN
F 1 "PWR" V 4600 1150 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x04" H 4500 1150 50  0001 C CNN
F 3 "" H 4500 1150 50  0000 C CNN
	1    4500 1150
	0    -1   -1   0   
$EndComp
$Comp
L +12V #PWR2
U 1 1 57899F3C
P 1100 7600
F 0 "#PWR2" H 1100 7450 50  0001 C CNN
F 1 "+12V" H 1100 7740 50  0000 C CNN
F 2 "" H 1100 7600 50  0000 C CNN
F 3 "" H 1100 7600 50  0000 C CNN
	1    1100 7600
	-1   0    0    1   
$EndComp
$Comp
L +12V #PWR7
U 1 1 5789A058
P 2150 6450
F 0 "#PWR7" H 2150 6300 50  0001 C CNN
F 1 "+12V" H 2150 6590 50  0000 C CNN
F 2 "" H 2150 6450 50  0000 C CNN
F 3 "" H 2150 6450 50  0000 C CNN
	1    2150 6450
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR1
U 1 1 5789A174
P 1100 7000
F 0 "#PWR1" H 1100 6750 50  0001 C CNN
F 1 "GND" H 1100 6850 50  0000 C CNN
F 2 "" H 1100 7000 50  0000 C CNN
F 3 "" H 1100 7000 50  0000 C CNN
	1    1100 7000
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR8
U 1 1 5789A290
P 2150 7050
F 0 "#PWR8" H 2150 6800 50  0001 C CNN
F 1 "GND" H 2150 6900 50  0000 C CNN
F 2 "" H 2150 7050 50  0000 C CNN
F 3 "" H 2150 7050 50  0000 C CNN
	1    2150 7050
	1    0    0    -1  
$EndComp
$Comp
L R_Small R52
U 1 1 578A0ACA
P 1600 6550
F 0 "R52" H 1630 6570 50  0000 L CNN
F 1 "3.3k" H 1630 6510 50  0000 L CNN
F 2 "Resistors_SMD:R_0603" H 1600 6550 50  0001 C CNN
F 3 "" H 1600 6550 50  0000 C CNN
	1    1600 6550
	1    0    0    -1  
$EndComp
$Comp
L R_Small R53
U 1 1 578A0C31
P 1600 6900
F 0 "R53" H 1630 6920 50  0000 L CNN
F 1 "3.3k" H 1630 6860 50  0000 L CNN
F 2 "Resistors_SMD:R_0603" H 1600 6900 50  0001 C CNN
F 3 "" H 1600 6900 50  0000 C CNN
	1    1600 6900
	1    0    0    -1  
$EndComp
$Comp
L R_Small R50
U 1 1 578A292C
P 1650 7500
F 0 "R50" H 1680 7520 50  0000 L CNN
F 1 "3.3k" H 1680 7460 50  0000 L CNN
F 2 "Resistors_SMD:R_0603" H 1650 7500 50  0001 C CNN
F 3 "" H 1650 7500 50  0000 C CNN
	1    1650 7500
	-1   0    0    1   
$EndComp
$Comp
L R_Small R51
U 1 1 578A2932
P 1650 7150
F 0 "R51" H 1680 7170 50  0000 L CNN
F 1 "3.3k" H 1680 7110 50  0000 L CNN
F 2 "Resistors_SMD:R_0603" H 1650 7150 50  0001 C CNN
F 3 "" H 1650 7150 50  0000 C CNN
	1    1650 7150
	-1   0    0    1   
$EndComp
$Comp
L LM324N U3
U 4 1 578A6FDF
P 1000 7300
F 0 "U3" H 1050 7500 50  0000 C CNN
F 1 "LM324N" H 1150 7100 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 950 7400 50  0001 C CNN
F 3 "" H 1050 7500 50  0000 C CNN
	4    1000 7300
	-1   0    0    1   
$EndComp
$Comp
L LM324N U3
U 1 1 578A76DA
P 2250 6750
F 0 "U3" H 2300 6950 50  0000 C CNN
F 1 "LM324N" H 2400 6550 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 2200 6850 50  0001 C CNN
F 3 "" H 2300 6950 50  0000 C CNN
	1    2250 6750
	1    0    0    -1  
$EndComp
$Comp
L LM324N U2
U 3 1 578A938A
P 7450 2500
F 0 "U2" H 7500 2700 50  0000 C CNN
F 1 "LM324N" H 7600 2300 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 7400 2600 50  0001 C CNN
F 3 "" H 7500 2700 50  0000 C CNN
	3    7450 2500
	1    0    0    -1  
$EndComp
$Comp
L LM324N U1
U 4 1 578F2458
P 9950 1350
F 0 "U1" H 10100 1450 50  0000 C CNN
F 1 "LM324N" H 10100 1150 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 9900 1450 50  0001 C CNN
F 3 "" H 10000 1550 50  0000 C CNN
	4    9950 1350
	1    0    0    -1  
$EndComp
NoConn ~ 3200 3000
NoConn ~ 3200 2900
NoConn ~ 3200 2800
NoConn ~ 3200 2700
NoConn ~ 3200 2600
$Comp
L LM324N U1
U 3 1 578E4E7A
P 7500 900
F 0 "U1" H 7550 1100 50  0000 C CNN
F 1 "LM324N" H 7650 700 50  0000 C CNN
F 2 "SMD_Packages:SOIC-14_N" H 7450 1000 50  0001 C CNN
F 3 "" H 7550 1100 50  0000 C CNN
	3    7500 900 
	1    0    0    -1  
$EndComp
$Comp
L ARDUINO_MEGA_SHIELD SHIELD1
U 1 1 578B3C29
P 2300 3150
F 0 "SHIELD1" H 1900 5650 60  0000 C CNN
F 1 "ARDUINO_MEGA_SHIELD" H 2200 450 60  0000 C CNN
F 2 "arduino_shields:ARDUINO_MEGA_SHIELD" H 2300 3150 60  0001 C CNN
F 3 "" H 2300 3150 60  0000 C CNN
	1    2300 3150
	1    0    0    -1  
$EndComp
NoConn ~ 1300 4000
NoConn ~ 1300 4200
NoConn ~ 1300 4450
NoConn ~ 1300 4650
NoConn ~ 1300 4850
NoConn ~ 1300 5050
NoConn ~ 1300 5300
$Sheet
S 2700 7450 500  150 
U 57901F94
F0 "Sheet57901F93" 60
F1 "file57901F93.sch" 60
$EndSheet
Text GLabel 3200 800  2    60   Input ~ 0
V_REF
NoConn ~ 1300 2300
NoConn ~ 3200 1500
NoConn ~ 3200 1700
NoConn ~ 3200 1800
NoConn ~ 3200 1900
NoConn ~ 3200 2200
Text GLabel 4650 1350 2    60   Input ~ 0
V_REF
Wire Wire Line
	6900 1000 7200 1000
Connection ~ 6950 1000
Wire Wire Line
	8250 2100 8350 2100
Wire Wire Line
	8350 2100 8350 900 
Wire Wire Line
	8250 900  8250 1750
Wire Wire Line
	7950 1450 8150 1450
Wire Wire Line
	8150 1450 8150 900 
Wire Wire Line
	7800 900  8450 900 
Connection ~ 8150 900 
Connection ~ 8250 900 
Connection ~ 8350 900 
Connection ~ 8450 1300
Wire Wire Line
	8450 1200 8450 1400
Wire Wire Line
	8450 1300 8650 1300
Wire Wire Line
	9350 1450 9650 1450
Connection ~ 9400 1450
Wire Wire Line
	10700 2550 10800 2550
Wire Wire Line
	10800 2550 10800 1350
Wire Wire Line
	10700 1350 10700 2200
Wire Wire Line
	10600 1900 10600 1350
Wire Wire Line
	10250 1350 10900 1350
Connection ~ 10600 1350
Connection ~ 10700 1350
Connection ~ 10800 1350
Connection ~ 10900 1750
Wire Wire Line
	10900 1650 10900 1850
Wire Wire Line
	10900 1750 11150 1750
Wire Wire Line
	6850 2600 7150 2600
Connection ~ 6900 2600
Wire Wire Line
	8200 3700 8300 3700
Wire Wire Line
	8300 3700 8300 2500
Wire Wire Line
	8200 2500 8200 3350
Wire Wire Line
	8100 3050 8100 2500
Wire Wire Line
	7750 2500 8400 2500
Connection ~ 8100 2500
Connection ~ 8200 2500
Connection ~ 8300 2500
Connection ~ 8400 2900
Wire Wire Line
	8400 2800 8400 3000
Wire Wire Line
	8400 2900 8650 2900
Wire Wire Line
	9400 3050 9700 3050
Connection ~ 9450 3050
Wire Wire Line
	10750 4150 10850 4150
Wire Wire Line
	10850 4150 10850 2950
Wire Wire Line
	10750 2950 10750 3800
Wire Wire Line
	10650 3500 10650 2950
Wire Wire Line
	10300 2950 10950 2950
Connection ~ 10650 2950
Connection ~ 10750 2950
Connection ~ 10850 2950
Connection ~ 10950 3350
Wire Wire Line
	10950 3250 10950 3450
Wire Wire Line
	10950 3350 11150 3350
Wire Wire Line
	7800 4900 7900 4900
Wire Wire Line
	8800 4450 8800 5300
Wire Wire Line
	7850 5300 7850 4900
Connection ~ 7850 4900
Connection ~ 8800 4800
Wire Wire Line
	8800 4450 8900 4450
Wire Wire Line
	8900 4450 8900 4500
Wire Wire Line
	9750 4850 9850 4850
Wire Wire Line
	10750 4400 10750 5250
Wire Wire Line
	9800 5250 9800 4850
Connection ~ 9800 4850
Connection ~ 10750 4750
Wire Wire Line
	10750 4400 10850 4400
Wire Wire Line
	10850 4400 10850 4450
Wire Wire Line
	8800 5300 7850 5300
Wire Wire Line
	10750 5250 9800 5250
Wire Wire Line
	5200 1750 5250 1750
Wire Wire Line
	5250 1750 5250 1800
Wire Wire Line
	3300 3650 3200 3650
Wire Wire Line
	650  7300 700  7300
Wire Wire Line
	650  7300 650  6800
Wire Wire Line
	650  6800 1300 6800
Wire Wire Line
	1300 6800 1300 7200
Connection ~ 1100 7600
Connection ~ 1100 7050
Wire Wire Line
	1600 7000 2150 7000
Wire Wire Line
	1600 6450 2150 6450
Wire Wire Line
	1600 6650 1600 6800
Wire Wire Line
	1600 6700 1950 6700
Wire Wire Line
	1300 7350 1300 7400
Connection ~ 1600 6700
Wire Wire Line
	1950 6700 1950 6650
Wire Wire Line
	2550 6750 2550 7300
Wire Wire Line
	2550 7300 1950 7300
Wire Wire Line
	1950 7300 1950 6850
Connection ~ 2150 7000
Connection ~ 2150 6450
Wire Wire Line
	1650 7050 1100 7050
Wire Wire Line
	1650 7600 1100 7600
Wire Wire Line
	1650 7250 1650 7400
Wire Wire Line
	1650 7350 1300 7350
Connection ~ 1650 7350
Wire Wire Line
	6950 1000 6950 1800
Wire Wire Line
	7950 1500 7950 1450
Wire Wire Line
	7950 2100 7700 2100
Wire Wire Line
	10350 2200 10400 2200
Wire Wire Line
	10400 2550 10250 2550
Wire Wire Line
	9400 1450 9400 2100
Wire Wire Line
	6900 2600 6900 3500
Wire Wire Line
	9450 3050 9450 4000
Wire Wire Line
	10100 4150 10450 4150
Wire Wire Line
	6950 1800 7050 1800
$Comp
L CONN_02X03 P10
U 1 1 579957B5
P 7300 1800
F 0 "P10" H 7300 2000 50  0000 C CNN
F 1 "CONN_02X03" H 7300 1600 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x03" H 7300 600 50  0001 C CNN
F 3 "" H 7300 600 50  0000 C CNN
	1    7300 1800
	1    0    0    -1  
$EndComp
$Comp
L CONN_02X03 P12
U 1 1 57995CBE
P 9900 2100
F 0 "P12" H 9900 2300 50  0000 C CNN
F 1 "CONN_02X03" H 9900 1900 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x03" H 9900 900 50  0001 C CNN
F 3 "" H 9900 900 50  0000 C CNN
	1    9900 2100
	1    0    0    -1  
$EndComp
$Comp
L CONN_02X03 P8
U 1 1 57995E14
P 7250 3500
F 0 "P8" H 7250 3700 50  0000 C CNN
F 1 "CONN_02X03" H 7250 3300 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x03" H 7250 2300 50  0001 C CNN
F 3 "" H 7250 2300 50  0000 C CNN
	1    7250 3500
	1    0    0    -1  
$EndComp
$Comp
L CONN_02X03 P11
U 1 1 579968B6
P 9850 4000
F 0 "P11" H 9850 4200 50  0000 C CNN
F 1 "CONN_02X03" H 9850 3800 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x03" H 9850 2800 50  0001 C CNN
F 3 "" H 9850 2800 50  0000 C CNN
	1    9850 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	9450 4000 9600 4000
Wire Wire Line
	9550 3900 9550 4100
Wire Wire Line
	9550 3900 9600 3900
Connection ~ 9550 4000
Wire Wire Line
	9550 4100 9600 4100
Wire Wire Line
	10100 3900 10250 3900
Wire Wire Line
	10250 3900 10250 3500
Wire Wire Line
	10250 3500 10650 3500
Wire Wire Line
	10450 3800 10450 4000
Wire Wire Line
	10450 4000 10100 4000
Wire Wire Line
	10100 4150 10100 4100
Wire Wire Line
	6900 3500 7000 3500
Wire Wire Line
	6950 3400 6950 3600
Wire Wire Line
	6950 3400 7000 3400
Connection ~ 6950 3500
Wire Wire Line
	6950 3600 7000 3600
Wire Wire Line
	8100 3050 7500 3050
Wire Wire Line
	7500 3050 7500 3400
Wire Wire Line
	7900 3350 7900 3500
Wire Wire Line
	7900 3500 7500 3500
Wire Wire Line
	7600 3700 7900 3700
Wire Wire Line
	7600 3700 7600 3600
Wire Wire Line
	7600 3600 7500 3600
Wire Wire Line
	7000 1700 7000 1900
Wire Wire Line
	7000 1700 7050 1700
Connection ~ 7000 1800
Wire Wire Line
	7000 1900 7050 1900
Wire Wire Line
	7550 1700 7550 1500
Wire Wire Line
	7550 1500 7950 1500
Wire Wire Line
	7550 1800 7800 1800
Wire Wire Line
	7800 1800 7800 1750
Wire Wire Line
	7800 1750 7950 1750
Wire Wire Line
	7700 2100 7700 1900
Wire Wire Line
	7700 1900 7550 1900
Wire Wire Line
	9400 2100 9650 2100
Wire Wire Line
	9600 2050 9500 2050
Wire Wire Line
	9500 2050 9500 2200
Connection ~ 9500 2100
Wire Wire Line
	9650 2000 9600 2000
Wire Wire Line
	9600 2000 9600 2050
Wire Wire Line
	9500 2200 9650 2200
Wire Wire Line
	10350 2200 10350 2100
Wire Wire Line
	10350 2100 10150 2100
Wire Wire Line
	10250 2550 10250 2200
Wire Wire Line
	10250 2200 10150 2200
Wire Wire Line
	10550 1900 10150 1900
Wire Wire Line
	10150 1900 10150 2000
$Comp
L CONN_01X02 P2
U 1 1 57979508
P 5500 1150
F 0 "P2" H 5500 1300 50  0000 C CNN
F 1 "EXT_INTERLOCK" V 5600 1150 50  0000 C CNN
F 2 "Terminal_Blocks:TerminalBlock_Pheonix_PT-3.5mm_2pol" H 5500 1150 50  0001 C CNN
F 3 "" H 5500 1150 50  0000 C CNN
	1    5500 1150
	0    -1   -1   0   
$EndComp
$Sheet
S 3800 7450 550  150 
U 57997BA8
F0 "PWM_OUT" 60
F1 "PWM_OUT.sch" 60
$EndSheet
$EndSCHEMATC
