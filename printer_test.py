from escpos.printer import Usb

def print_text_line_by_line(printer, filename, line_length=48):
    with open(filename, 'r') as file:
        for line in file:
            words = line.split(' ')
            current_line = ""
            
            for word in words:
                # Check if adding the next word would exceed the line length
                if len(current_line) + len(word) + 1 > line_length:
                    # Print the current line and start a new line with the current word
                    printer.text(current_line.strip() + '\n')
                    current_line = word + ' '
                else:
                    current_line += word + ' '

            # Print any remaining words in the current line
            if current_line:
                printer.text(current_line.strip() + '\n')

def main():
    VENDOR_ID = 0x04b8  # Common vendor ID for Epson
    PRODUCT_ID = 0x0e27  # The correct product ID for your printer
  
    try:
        # Create a Usb printer instance
        printer = Usb(VENDOR_ID, PRODUCT_ID)

        # File name to read and print
        file_name = 'print.txt'
        
        # Print text from file, wrapped to the specified line length
        print_text_line_by_line(printer, file_name)

        # Cut the paper
        printer.cut()

        # Always ensure the printer is properly closed to release the USB interface
        printer.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()