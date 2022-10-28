/* 
 * Part of Magnetic tweezers project on CBG
 * Voltage control with Arduino - Arduino is used as DAC and ADC. 
 * Program meant to be used as an interface between python and constant current generator.
 *
 * by Erik Plesko
 * 7.5.2022
 * 
 * Voltage units: mV
 * Time units: ms
 *
 * Serial commands description:
 * 		! - set
 * 		A - Answer that a command has been executed
 *		? - get
 * 		# - Answer to get
 * 		
 * 		Arguments are separated with spaces
 * 		
 * 		Example 1: !V 1 100 -> set voltage (tip 1) (to 100 mV) -> AV 1 100
 * 		Example 2: ?V 2 -> get voltage (tip 2) -> #V 2 1872
 * 
 * 		For simple overview of functions and arguments read the comments
 * 		of lines where functions are added to scmd (scmd.addCommand()... )
 * 
 *
 * V1.2 - 28.10.2022 by Erik:
 * - Added support for two tips
 * 		setting and getting the voltage of the tips (one by one)
 * 		made the timeouts work separately for each tip - just the tip you don't specify the voltage will shut off after the timeout (if timeout is on)
 *
 *
 *
*/









#include <SerialCommand.h>


// pins 5, 6 with frequency 980 Hz (all PWM pins: 3, 5, 6, 9, 10, 11, 490 Hz)
#define VinPin1 5        // Output voltage for the tip 1, but labeled as on the current generator: Vin
#define VinPin2 6        // Output voltage for the tip 2, but labeled as on the current generator: Vin
#define VLEDPin1 9       // LED, used to visualise Vin1 value
#define VLEDPin2 10       // LED, used to visualise Vin2 value
#define VsensePin1 A0    // V-sense1 pin
#define VsensePin2 A1    // V-sense2 pin


bool autoTimeoutOn = true;              // Output voltage is set to zero if there are no commands received for time of autoTimeoutTime
unsigned int autoTimeoutTime = 200;     // milliseconds
unsigned long autoTimeoutTimer1 = 0;     // Timer for tip 1. it is reset every time voltage command is received for that tip
unsigned long autoTimeoutTimer2 = 0;     // Timer for tip 2. it is reset every time voltage command is received for that tip

int Vmax = 2000;    // Max voltage to be set on any of the output pins VinPin

// Serial Command:
SerialCommand scmd;


// Debuging:
bool printAll = true;




void setup() {
	Serial.begin(19200);

	scmd.addCommand("!V", cmd_set_voltage);            // _ #tip_number [] #voltageIn [mV]   // Set voltage In for a specific tip (it goes out, but the signal goes to V-in on the current generator)
	scmd.addCommand("?V", cmd_get_voltage);            // _ #tip_number []                  // Read the voltage of a specific pin (connected to V-sense)

	scmd.addCommand("!TT", cmd_set_auto_timeout_time);  // _ #autoTimeoutTime
	scmd.addCommand("!TO", cmd_set_auto_timeout_on);    // _ #autoTimeoutOn (0 or 1)
	scmd.addCommand("!VM", cmd_set_voltage_max);        // _ #Vmax (in range 0 to 3000)

	// General:
	scmd.addCommand("!PA", cmd_setPrintAll);            // _ #printAll (0 or 1)
	scmd.addCommand("Test", cmd_test);                  // _ (#a #b #c #d ...)
	scmd.addDefaultHandler(unrecognized);


	// I/O
	pinMode(LED_BUILTIN, OUTPUT);   // Builtin LED

	Serial.println(F("Setup done."));
	Serial.println(F("File: V01_voltageControl.2"));

}


void loop() {
	// Serial commands
	scmd.readSerial();

	if (autoTimeoutOn) {
		if (millis() > autoTimeoutTimer1 + autoTimeoutTime) {
			set_voltage_pin(1, 0);
		}
		if (millis() > autoTimeoutTimer2 + autoTimeoutTime) {
			set_voltage_pin(2, 0);
		}

	}
	

  
	// delay(300);
	// cmd_get_voltage();
	// set_voltage_pin(4500);
	// delay(10);
	// set_voltage_pin(100);
	// delay(10);
	
	
	
	
}


// -------------------------------------------------------------------------------
// *** Functions: *** ------------------------------------------------------------


byte mV_2_DA(long mV) {
	long val;
	byte DA;

	val = mV*255/5000;  // 255 PWM scale is 5000 mV

	if (val > 255) {
		DA = 255;
	} else if (val < 0) {
		DA = 0;
	} else {
		DA = val;
	}

	return DA;
}

long AD_2_mV(long AD) {
	return AD*5000/1023; // 5000 mV is 1023 analog read value
}


void set_voltage_pin(int tip_number, int voltage) {
	byte DA;    // value to set to DAC

	if (voltage > Vmax) {
		voltage = Vmax;
	}

	DA = mV_2_DA(voltage);

	if (tip_number == 1) {
		analogWrite(VinPin1, DA);    
		analogWrite(VLEDPin1, DA);
		autoTimeoutTimer1 = millis();   
	} else if (tip_number == 2) {
		analogWrite(VinPin2, DA);    
		analogWrite(VLEDPin2, DA);
		autoTimeoutTimer2 = millis();   
	}    

}


void blinkBuiltinLED(int number, int blinkTime) {
	// -number blinks, time of one blink-on-of is -blinktime (in ms)

	digitalWrite(LED_BUILTIN, LOW); 

	for (int i = 0; i < number; i++) {
		digitalWrite(LED_BUILTIN, HIGH);   
		delay(blinkTime/2);                
		digitalWrite(LED_BUILTIN, LOW);    
		delay(blinkTime/2); 
	}
}







// -------------------------------------------------------------------------------
// *** SerialCommand functions: *** ----------------------------------------------

void unrecognized() {
	Serial.println(F("Unrecognized command."));
}

void cmd_test() {
	Serial.println(F("cmd_test function call."));

	char * arg;

	arg = scmd.next();
	while(arg != NULL) {
		Serial.print(arg);
		Serial.print(' ');
		arg = scmd.next();
	}

	Serial.println(F("End of test function."));
}


void cmd_set_voltage() {
	// Set the voltage based on the serial message value.
	// First serial argument is tip number and the second gives the voltage value
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		int tip_number = atol( arg );

		arg = scmd.next();
		if ( arg != NULL) {
			val = atol( arg );

			if (tip_number == 1 || tip_number == 2) {
				set_voltage_pin(tip_number, val);

				Serial.print(F("AV ")); 
				Serial.print(tip_number); 
				Serial.print(F(" ")); 
				Serial.println(val);
			} else {
				Serial.print(F("ERR - unsupported tip number: ")); Serial.println(tip_number);
				return;
			}

			if (printAll) {
				Serial.print(F("voltage set to "));
				Serial.println(val);
			}
		} else Serial.println(F("ERR - cmd_set_voltage(): Not enough arguments."));
	} else Serial.println(F("ERR - cmd_set_voltage(): Not enough arguments."));
}


void cmd_get_voltage () {
	// Get the voltage Of the specified pin and send it over serial.
	// The serial argument in the command calling the function specifies tip number .
	char * arg;

	arg = scmd.next();
	if ( arg != NULL) {
		int tip_number = atol( arg );
		int AD_val;
		if (tip_number == 1) {
			AD_val = analogRead(VsensePin1);
		} else if (tip_number == 2) {
			AD_val = analogRead(VsensePin2);
		} else {
			Serial.print(F("ERR - unsupported tip number: ")); Serial.println(tip_number);
			return;
		}

		Serial.print(F("#V ")); 
		Serial.print(tip_number); 
		Serial.print(F(" ")); 
		Serial.println(AD_2_mV(AD_val));
	
		if (printAll) {
			Serial.println(F("That was VsensePin [mV] "));
		}
	} else {
		Serial.println(F("ERR - cmd_get_voltage(): Not enough arguments."));

	}
}


void cmd_set_auto_timeout_time () {
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		val = atol( arg );
		autoTimeoutTime = val;
		if (printAll) {
			Serial.print(F("autoTimeoutTime set to "));
			Serial.println(autoTimeoutTime);
		}
	}
}

void cmd_set_auto_timeout_on () {
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		val = atol( arg );
		autoTimeoutOn = val;
		if (printAll) {
			Serial.print(F("autoTimeoutOn set to "));
			Serial.println(autoTimeoutOn);
		}
	}
}

void cmd_set_voltage_max () {
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		val = atol( arg );
		// Vmax should be in the range [0, 3000]
		if (val >= 0 && val <= 3000) {
			Vmax = val;
		} else {
			if (printAll) {
				Serial.println(F("Value for Vmax is out of range [0, 3000]."));
			}
		}
		if (printAll) {
			Serial.print(F("Vmax set to "));
			Serial.println(Vmax);
		}
	}
}

void cmd_setPrintAll() {
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		val = atol( arg );
		printAll = val;
		if (printAll) {
			Serial.print(F("printAll set to "));
			Serial.println(printAll);
		}
	}
}


// #### End of document #################################################################
// ######################################################################################