  This project is a smart Electric Vehicle (EV) charging and monitoring system designed to automate and enhance the EV charging process. It uses sensors and microcontrollers to detect vehicles, authenticate users via RFID, and manage charging through a relay-controlled mechanism. The system measures voltage, current, and energy consumption in real time, storing the data in Firebase for cloud-based tracking. 
  Users can monitor and control the process remotely through the Blynk app, while an LCD displays charging details on-site. Additionally, SMS notifications with charging session summaries are sent to users via the Twilio API. 
  This project ensures secure, efficient, and user-friendly EV charging management, suitable for personal or small-scale EV infrastructure setups.

Workflow of the Electric Vehicle Charging and Monitoring System
1.Initialization: System powers on, connects to Wi-Fi, and initializes hardware components.
2.Vehicle Detection: Ultrasonic sensor detects a vehicle and prompts for RFID authentication.
3.User Authentication: RFID card is scanned, verified via Firebase, and access is granted.
4.Start Charging: Relay activates, and the system begins charging while monitoring voltage, current, and energy consumption.
5.Monitoring and Control: Charging stops automatically if the vehicle is removed or no current is detected.
6.Data Logging and Notifications: Energy usage and cost are logged in Firebase, and an SMS is sent to the user with session details.
7.Remote Access: Users monitor charging status and energy data via the Blynk app.








