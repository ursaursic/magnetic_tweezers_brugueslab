/* 
 * Part of Magnetic tweezers project on CBG
 * Voltage control with Arduino using Adafruit ADC and DAC boards 
 * (ADC Adafruit ADS1115, DAC: Adafruit_MCP4728)
 * 
 * Program meant to be used as an interface between python and constant current generator.
 * Pins Vin and Vsense are named to match the labeled names on the current generator. Vin 
 * is an output signal that goes to the Vin of the current generator. 
 *
 * by Erik Plesko
 * September 2023
 * 
 * Voltage units: mV
 * Time units: ms
 *
 */


// -- Include --------------------------------------------------------------------------
// -------------------------------------------------------------------------------------
// For serial communication
#include <SerialCommand.h>
// For LEDs on the PCB (and sync LED)
#include <FastLED.h>
// For Adafruit boards on the PBC (ADC and DAC)
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_MCP4728.h>

// -- Define ---------------------------------------------------------------------------
// -------------------------------------------------------------------------------------
// Pins 5, 6 with frequency 980 Hz
#define VinPin 5        // Output voltage, but labeled as on the current generator: Vin
#define VLEDPin 6       // LED, used to visualize Vin value
#define VsensePin A0

// ADC - DAC pins
#define T1_VIN_PIN_NUMBER MCP4728_CHANNEL_A     // mcp pin number for the tip 1 Vin pin
#define T2_VIN_PIN_NUMBER MCP4728_CHANNEL_B     // mcp pin number for the tip 2 Vin pin
#define T1_VS_PIN_NUMBER 0                      // ads pin number for the tip 1 VS pin
#define T2_VS_PIN_NUMBER 1                      // ads pin number for the tip 2 VS pin
// LEDs numbers:
#define T1_VIN_LED_NUMBER 0
#define T1_VS_LED_NUMBER 1
#define T1_VIN_LED_NUMBER 2
#define T1_VS_LED_NUMBER 3

// TODO: legacy, from before the pcb board:
#define LED_PIN     2  // Pin for LEDs on the PCB
#define NUM_LEDS    4  // Number of LEDs on the PCB

// TODO: Use those values in the functions 
#define VCC 4710 // mv
#define N_BITS_ADC 32768 // 16 bit signed value
#define N_BITS_DAC 4095 // 12 bit

// -- Prepare --------------------------------------------------------------------------
// -------------------------------------------------------------------------------------

bool autoTimeoutOn = true;              // Output voltage is set to zero if there are no commands received for time of autoTimeoutTime
unsigned int autoTimeoutTime = 200;     // milliseconds
unsigned long autoTimeoutTimer_1 = 0;     // Timer for tip 1. it is reset every time voltage command is received for tip 1
unsigned long autoTimeoutTimer_2 = 0;     // Timer for tip 2. it is reset every time voltage command is received for tip 2

int Vmax = 2000;    // Max voltage to be set on the output pin VinPin


// Serial Command:
SerialCommand scmd;
// ADC:
Adafruit_ADS1115 ads1115;
// DAC:
Adafruit_MCP4728 mcp4728;
// LEDs
CRGB leds[NUM_LEDS];

// Debugging:
bool printAll = true;


void setup() {
    // LEDs
   	FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
    LEDsRGB(0, 100, 0);

	Serial.begin(19200);

	scmd.addCommand("!VI", cmd_set_voltage);            // _ #voltageIn [mV]   // Set voltage In (it goes out, but the signal goes to V-in on the current generator)
	scmd.addCommand("?VS", cmd_get_voltage);            // _ /                 // Read the voltage (connected to V-sense)
	scmd.addCommand("!TT", cmd_set_auto_timeout_time);  // _ #autoTimeoutTime
	scmd.addCommand("!TO", cmd_set_auto_timeout_on);    // _ #autoTimeoutOn (0 or 1)
    scmd.addCommand("!VM", cmd_set_voltage_max);        // _ #Vmax (in range 0 to 3000)

	// General:
	scmd.addCommand("!PA", cmd_setPrintAll);            // _ #printAll (0 or 1)
	scmd.addCommand("Test", cmd_test);                  // _ (#a #b #c #d ...)
	scmd.addDefaultHandler(unrecognized);


	// TODO: legacy
	pinMode(LED_BUILTIN, OUTPUT);   // Builtin LED


    // D-ADCs:
    // TODO: check the i2c addresses and select them here in the code (even if we know that boards have defaults)
    ads1115.begin();
    ads1115.setGain(GAIN_ONE); 

    mcp4728.begin();
    // TODO now: set the voltage based on the serial command
    mcp4728.setChannelValue(MCP4728_CHANNEL_A, 0);
    mcp4728.setChannelValue(MCP4728_CHANNEL_B, 0);
    mcp4728.setChannelValue(MCP4728_CHANNEL_C, 0);
    mcp4728.setChannelValue(MCP4728_CHANNEL_D, 0);


	Serial.println(F("Setup done."));
	Serial.println(F("File: V02_pcb_hotfix.ino, 2 tips version"));
	turnOff();
}


void loop() {
	// Manage serial commands:
	scmd.readSerial();

	if (autoTimeoutOn) {
		if (millis() > autoTimeoutTimer_1 + autoTimeoutTime) {
			set_voltage_pin(0);
		}

        if (millis() > autoTimeoutTimer_2 + autoTimeoutTime) {
			// TODO: set voltage of tip 2
            // set_voltage_pin(0);
		}
	}
	
}

// -------------------------------------------------------------------------------------
// -- Functions ------------------------------------------------------------------------

int mV_2_DA(long mV) {
	long val;
	int DA;

	val = mV*4095/4710;  // 4095 (12 bit DAC) scale is 4700 mV

	if (val > 4095) {
		DA = 4095;
	} else if (val < 0) {
		DA = 0;
	} else {
		DA = val;
	}

	return DA;
}


int16_t read_adc(int pin_number) {
    int16_t adc;
    adc = ads1115.readADC_SingleEnded(pin_number);
    return adc;
}


long AD_2_mV(long AD) {
    // TODO: make the led for reading a bit nicer, and maybe read every 100 ms or so, not just when read is called.
    leds[T1_VS_LED_NUMBER] = CRGB(0, 255*AD/32768, 0);  // green - Brightness as percent of "Vcc"
    FastLED.show();
	return AD*4710/32768; // 4700 mV is 32768 analog read value
}


void set_voltage_pin(int voltage) {
	int DA;    // value to set to DAC
    long computation_var;
    long long_type_one = 1;

	// TODO:
	// Do it nicer: Limit the output voltage yo Vmax (3V - or whatever)
    if (voltage > Vmax) {
        voltage = Vmax;
    }


	DA = mV_2_DA(voltage);


	// analogWrite(VinPin, DA);    
	// analogWrite(VLEDPin, DA);
    mcp4728.setChannelValue(T1_VIN_PIN_NUMBER, DA);
    
    // Set led:
    // TODO: make the 5200 mV down here as a parameter somewhere on top.
    computation_var = long_type_one*DA*255;
    leds[T1_VIN_LED_NUMBER] = CRGB(0, computation_var/4095, 0);  // green - Brightness as percent of "Vcc"
    FastLED.show();

	autoTimeoutTimer_1 = millis();   
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


void turnOff() {
	for(int i = 0; i<NUM_LEDS; i++){
		leds[i] = CRGB(0, 0, 0);
	}
	FastLED.show();
}


void LEDsRGB(int R, int G, int B) {
	// Turns all leds to white with set brightness
	for(int i = 0; i<NUM_LEDS; i++){
		leds[i] = CRGB(R, G, B);
	}
	FastLED.show();
}

// -------------------------------------------------------------------------------------
// -- SerialCommand functions: ---------------------------------------------------------

void unrecognized() {
	Serial.println(F("Unrecognized command."));

    LEDsRGB(50, 0, 0);
    delay(50);
    turnOff();
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

    LEDsRGB(0, 50, 0);
    delay(400);
    LEDsRGB(50, 0, 50);
    delay(100);
    turnOff();

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


  Serial.print(F("#VS ")); Serial.println(AD_2_mV(read_adc(T1_VS_PIN_NUMBER)));
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
