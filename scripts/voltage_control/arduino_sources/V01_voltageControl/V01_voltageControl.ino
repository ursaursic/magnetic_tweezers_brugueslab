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
 *
 *
 *
 *
 *
*/









#include <SerialCommand.h>


// pins 5, 6 with frequency 980 Hz
#define VinPin 5        // Output voltage, but labeled as on the current generator: Vin
#define VLEDPin 6       // LED, used to visualise Vin value
#define VsensePin A0


bool autoTimeoutOn = true;              // Output voltage is set to zero if there are no commands received for time of autoTimeoutTime
unsigned int autoTimeoutTime = 200;     // milliseconds
unsigned long autoTimeoutTimer = 0;     // Timer. it is reset every time voltage command is received

int Vmax = 2000;    // Max voltage to be set on the output pin VinPin

// Serial Command:
SerialCommand scmd;


// Debuging:
bool printAll = true;




void setup() {
	Serial.begin(19200);

	scmd.addCommand("!VI", cmd_set_voltage);            // _ #voltageIn [mV]   // Set voltage In (it goes out, but the signal goes to V-in on the current generator)
	scmd.addCommand("?VS", cmd_get_voltage);            // _ /                 // Read the voltage (connected to V-sense)
	scmd.addCommand("!TT", cmd_set_auto_timeout_time);  // _ #autoTimeoutTime
	scmd.addCommand("!TO", cmd_set_auto_timeout_on);    // _ #autoTimeoutOn (0 or 1)

	// General:
	scmd.addCommand("!PA", cmd_setPrintAll);            // _ #printAll (0 or 1)
	scmd.addCommand("Test", cmd_test);                  // _ (#a #b #c #d ...)
	scmd.addDefaultHandler(unrecognized);


	// I/O
	pinMode(LED_BUILTIN, OUTPUT);   // Builtin LED

	Serial.println(F("Setup done."));
	Serial.println(F("File: V01_voltageControl.1"));

}


void loop() {
	// Serial commands
	scmd.readSerial();

	if (autoTimeoutOn) {
		if (millis() > autoTimeoutTimer + autoTimeoutTime) {
			set_voltage_pin(0);
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


void set_voltage_pin(int voltage) {
	byte DA;    // value to set to DAC

	// TODO:
	// Do it nicer: Limit the output voltage yo Vmax (3V - or whatever)
    if (voltage > Vmax) {
        voltage = Vmax;
    }


	DA = mV_2_DA(voltage);

	analogWrite(VinPin, DA);    
	analogWrite(VLEDPin, DA);

	autoTimeoutTimer = millis();   
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
	char * arg;
	int val;

	arg = scmd.next();
	if ( arg != NULL) {
		val = atol( arg );

		set_voltage_pin(val);

    Serial.print(F("#VI ")); Serial.println(val);
		
		if (printAll) {
			Serial.print(F("voltage set to "));
			Serial.println(val);
		}
	}


}

void cmd_get_voltage () {
	// TODO:


  Serial.print(F("#VS ")); Serial.println(AD_2_mV((analogRead(VsensePin))));
	if (printAll) {
		Serial.println(F("That was VsensePin [mV] "));
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









// void cmd_moveJ() {
// 	char * arg;
// 	long steps1;
// 	long steps2;
// 	int servoValOld;

// 	arg = scmd.next();
// 	if ( arg != NULL) {
		
// 		steps1 = atol( arg );

// 		arg = scmd.next();
// 		if (arg != NULL) {
			
// 			steps2 = atol( arg );

// 			stepper1.moveTo(steps1);
// 			stepper2.moveTo(steps2);

// 			// Move servo:
// 			arg = scmd.next();
// 			if (arg != NULL) {
// 				servoValOld = servo3.read();
// 				servo3.write(atol( arg ));
// 				delay(2*abs(servoValOld-servo3.read()));
// 			}

// 			targetReached = false;
// 			runMotorsBySpeed = false;

// 			if (printAll) {
// 				Serial.print("steps1: "); Serial.println(steps1);
// 				Serial.print("steps2: "); Serial.println(steps2);
// 			}
// 		}
		
// 	}

// }
