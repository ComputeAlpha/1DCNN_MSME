import serial
import os
import argparse
import time

def read_serial_data(port, baudrate, max_lines, output_file):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # Open file for writing
    line_count = 0

    # Start reading from serial port
    with open(output_file, "+w") as f:
        while line_count < max_lines:
            if ser.in_waiting > 0:
                # Read a line from serial port
                line = ser.readline().decode('utf-8')
                elems = len(line.split(","))
                if elems != 19 and not line.endswith("\n"):
                    continue
                print(elems)
                print(line)
                inp = str(input("Label:"))[0]
                label = None

                if(inp.lower() == "o"):
                    label = "organic"
                elif(inp.lower() == "i"):
                    label = "inorganic"
                else:
                    label = "Undefined"

                line += label

                f.write(line + '\n')
                line_count += 1
        time.sleep(0.1)  # Small delay to allow data to be available

    # Close the serial port after reading
    ser.close()
    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    # Setup argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Fetch data from serial port and save to log file.")
    parser.add_argument("--max_lines", type=int, default=10, help="Maximum number of lines to fetch and write to log file (default: 500).")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port to read from (default: /dev/ttyUSB0).")
    parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate for serial communication (default: 9600).")
    parser.add_argument("--output_folder", type=str, default=".", help="Output folder (default: current directory).")
    parser.add_argument("--output", type=str, default="log.csv", help="Output log file (default: log.csv).")

    args = parser.parse_args()
    path = args.output
    if args.output_folder != "." and len(args.output_folder) > 0:
        os.makedirs(args.output_folder, exist_ok=True)
        path = os.path.join(args.output_folder, args.output)
    # Run the main function
    read_serial_data(args.port, args.baudrate, args.max_lines, path)
