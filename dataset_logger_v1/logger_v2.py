import serial
import os
import argparse
import time
import sys

def read_serial_data(port, baudrate, max_lines, output_file):
    try:
        # Initialize serial connection
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baud")
        time.sleep(2)  # Wait for serial connection to stabilize
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return
    
    line_count = 0
    
    # Start reading from serial port
    with open(output_file, "w") as f:
        # Write header
        f.write("time,410nm,435nm,460nm,485nm,510nm,535nm,560nm,585nm,610nm,645nm,680nm,705nm,730nm,760nm,810nm,860nm,900nm,940nm,label\n")
        
        print("\nPress Enter to capture a new reading...")
        
        while line_count < max_lines:
            try:
                # Wait for Enter key
                input("")  # Wait for Enter key press
                
                # Clear any old data in the serial buffer
                ser.reset_input_buffer()
                
                # Wait for new data
                print("Waiting for sensor data...")
                while ser.in_waiting == 0:
                    time.sleep(0.1)
                
                # Read the latest line
                line = ser.readline().decode('utf-8') #.strip()
                
                # Split the line and check format
                elements = line.split(",")
                
                # Validate data format (18 spectral values + timestamp)
                if len(elements) != 19:
                    print(f"Invalid data format. Expected 19 values, got {len(elements)}")
                    print("Press Enter to try again...")
                    continue
                
                # Validate that all elements are numbers
                try:
                    # Convert all elements except the last to float
                    [float(x) for x in elements]
                except ValueError:
                    print("Invalid numeric data, skipping line")
                    print("Press Enter to try again...")
                    continue
                
                # Print current values
                print(f"\nCurrent reading ({line_count + 1}/{max_lines}):")
                print(f"Time: {elements[0]}")
                print("Spectral values:", ", ".join(elements[1:]))
                
                # Get label input
                while True:
                    inp = input("Enter label (r=Ripe, u=Unripe, s=Skip): ").lower()
                    if inp in ['r', 'u', 's']:
                        break
                    print("Invalid input. Please enter 'r', 'u', or 's'")
                
                if inp == 's':
                    print("Skipping this reading...")
                    print("\nPress Enter to capture a new reading...")
                    continue
                
                # Assign label
                label = "Ripe" if inp == 'r' else "Unripe"
                
                # Write to file
                output_line = f"{line},{label}\n"
                f.write(output_line)
                line_count += 1
                
                print(f"Saved reading {line_count} with label: {label}")
                print("-" * 50)
                
                if line_count < max_lines:
                    print("\nPress Enter to capture a new reading...")
                
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
                break
            except KeyboardInterrupt:
                print("\nData collection interrupted by user")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Press Enter to try again...")
                continue
    
    # Close the serial port after reading
    try:
        ser.close()
        print(f"\nData collection complete. Data saved to {output_file}")
        print(f"Total readings collected: {line_count}")
    except Exception as e:
        print(f"Error closing serial port: {e}")

def main():
    # Setup argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Fetch data from serial port and save to log file.")
    parser.add_argument("--max_lines", type=int, default=10, 
                      help="Maximum number of lines to fetch and write to log file (default: 10).")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", 
                      help="Serial port to read from (default: /dev/ttyUSB0).")
    parser.add_argument("--baudrate", type=int, default=9600, 
                      help="Baud rate for serial communication (default: 9600).")
    parser.add_argument("--output_folder", type=str, default=".", 
                      help="Output folder (default: current directory).")
    parser.add_argument("--output", type=str, default="log.csv", 
                      help="Output log file (default: log.csv).")
    
    args = parser.parse_args()
    
    # Create output directory if needed
    path = args.output
    if args.output_folder != "." and len(args.output_folder) > 0:
        os.makedirs(args.output_folder, exist_ok=True)
        path = os.path.join(args.output_folder, args.output)
    
    # Run the main function
    read_serial_data(args.port, args.baudrate, args.max_lines, path)

if __name__ == "__main__":
    main()
