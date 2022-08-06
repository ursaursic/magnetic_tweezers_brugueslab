/*
	Erik Plesko 26.7.22

	Arduino echoes the received string. if changeToAnswer is true it will
	mock the InjectMan in a very basic way - che command should start with 'c' or 'C'
	and then the echoed string will be the same just the c -> A (as answer).
	if the first char is not c, then tre return is E060 - as InjectMan would do.

	if changeToAnswer is false, then it echoes the string.

	InjectMan baudrate is 19200.

*/


const int maxBufferLen = 200;
char incomingStr[maxBufferLen]; // for incoming serial data

bool changeToAnswer = true;

void setup() {
	Serial.begin(19200); // opens serial port, sets data rate to 9600 bps

	delay(1000);
	Serial.println("string_echo");
}

void loop() {
	// reply only when you receive data:
	if (Serial.available() > 0) {
		int i = 0;
		while (Serial.available() > 0) {
			// read the incoming byte:
			incomingStr[i++]= Serial.read();

			if (i > maxBufferLen) {
				break;
			}
			delay(5);
		}
		incomingStr[i] = '\0';

		if (changeToAnswer) {
			if (incomingStr[0] == 'c' || incomingStr[0] == 'C'){
				incomingStr[0] = 'A';
				Serial.print(incomingStr);
			} else {
				Serial.println("E060");
			}
		} else {
			Serial.print(incomingStr);
			// Serial.println("---");
		}



	}
}