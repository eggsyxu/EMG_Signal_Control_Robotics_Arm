# EMG-Controlled Robotic Arm

This is the final project for **BIOMEDE 458** at the University of Michigan. We built a custom EMG acquisition circuit and used six-channel EMG signals to control a 4-DOF robotic arm in real-time.

## Project Description
- Six EMG channels are read through a custom-built amplifier circuit.
- Signals are filtered, analyzed, and used to trigger specific movements of a robotic arm.
- The software is developed in Python with a real-time GUI built using **PyQt5** and **PyQtGraph**.

## Project Structure
```
.
├── test
│   ├── *.py (signal reading and spike detection tests)
│   ├── *.csv (simulated and recorded EMG signals)
├── Workflow
│   └── Final_Test.py (main testing pipeline)
├── EMG_Control_Robotics_Arm (Run in Arduino IDE)
```


## Main Program
The core visualization and control script is a PyQt5-based serial signal viewer:

### Features:
- Real-time plotting of 6 EMG channels
- Spike detection with elbow-priority logic
- Threshold-based triggering
- Serial communication with Arduino

### To Run:
Make sure the correct serial port is specified (default is `/dev/cu.usbserial-2120` on macOS).
```bash
pip install -r requirements.txt
python Final_Test.py
```

## EMG Channel Mapping
| Channel | Label          | Action Sent |
|---------|----------------|-------------|
| A0      | Left Wrist     | L           |
| A1      | Right Wrist    | R           |
| A2      | Left Elbow     | F           |
| A3      | Right Elbow    | B           |
| A4      | Left Leg       | G           |
| A5      | Right Leg      | O           |

## Contact
For questions, please contact: **Guangxuan Xu**  
Email: [eggsyxu@umich.edu]



