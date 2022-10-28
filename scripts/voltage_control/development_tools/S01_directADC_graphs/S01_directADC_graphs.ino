 /*
  * Time the ADC frequency
  * 
  * 
  * At the time of measurement it was about: 21.03125 us for a single value
  * Which is 47.6 kHz
  * 
 */

#define buttonPin1 3


const byte adcPin = 0;  // A0
const int MAX_RESULTS = 1500;
const int timeToPrintAll = 5; // in seconds
volatile byte results [MAX_RESULTS];
volatile int resultNumber;


// Timer:
unsigned long timer1 = 0;

// ADC complete ISR
ISR (ADC_vect)
  {
  if (resultNumber >= MAX_RESULTS)
    ADCSRA = 0;  // turn off ADC
  else
    results [resultNumber++] = ADC/4;
  }  // end of ADC_vect
  
EMPTY_INTERRUPT (TIMER1_COMPB_vect);
 
void setup ()
  {
  Serial.begin(115200); // set baudrate
  Serial.println("S01_directADC_graphs");


  pinMode(buttonPin1, INPUT_PULLUP); 
  
  // reset Timer 1
  TCCR1A  = 0;
  TCCR1B  = 0;
  TCNT1   = 0;
  TCCR1B  = bit (CS11) | bit (WGM12);  // CTC, prescaler of 8
  TIMSK1  = bit (OCIE1B); 
  OCR1A   = 39;    
  OCR1B   = 39; // 20 uS - sampling frequency 50 kHz

  ADCSRA  =  bit (ADEN) | bit (ADIE) | bit (ADIF); // turn ADC on, want interrupt on completion
  ADCSRA |= bit (ADPS2);  // Prescaler of 16
  ADMUX   = bit (REFS0) | (adcPin & 7);
  ADCSRB  = bit (ADTS0) | bit (ADTS2);  // Timer/Counter1 Compare Match B
  ADCSRA |= bit (ADATE);   // turn on automatic triggering
}


void loop () {
  while (resultNumber < MAX_RESULTS) { }
//  Serial.print("time for N conversions [us]: "); Serial.println(micros() - timer1);



    
  for (int i = 0; i < MAX_RESULTS; i++)
  {
    Serial.println(results [i]);
    delay(1000*timeToPrintAll/MAX_RESULTS);
    
  }

  

  
  resultNumber = 0; // reset counter





  while (digitalRead(buttonPin1) == HIGH);
  
  // button pressed
//  Serial.println("Button pressed");

  while (digitalRead(buttonPin1) != HIGH);
  



  // Start timer:
  timer1 = micros();
  
  ADCSRA =  bit (ADEN) | bit (ADIE) | bit (ADIF)| bit (ADPS2) | bit (ADATE); // turn ADC ON


  
}
