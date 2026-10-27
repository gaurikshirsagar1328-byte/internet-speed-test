
# NEXUS — Internet Speed Test

A desktop Internet Speed Test application built using Python and Tkinter, featuring an animated speedometer and real network speed measurements.

## Features

- Animated speedometer interface
- Download speed measurement (Mbps)
- Upload speed measurement (Mbps)
- Ping / latency measurement (ms)
- Background testing to keep the GUI responsive
- Progress updates and error handling
- Option to run the test again

## Technologies Used

- Python 3.11
- Tkinter
- speedtest-cli
- Threading and Queue

## Requirements

- Python 3.11 or compatible version
- Active internet connection

## Installation

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python main.py
   ```

## Project Structure

```text
internet-speed-test/
├── main.py
├── requirements.txt
└── README.md
```

## How It Works

The application uses speedtest-cli to find a suitable
test server and measure download speed, upload speed,
and latency. Tkinter displays the results in a desktop
GUI, while a background thread runs the network test.

## Future Improvements

- Speed test history
- Exportable test reports
- Dynamic speedometer scale
- Network information dashboard

## License

This project is licensed under the MIT License.
