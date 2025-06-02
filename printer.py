import socket
from escpos.printer import Usb


def print_text_line_by_line(printer, text, line_length=48):
    lines = text.split("\n")
    for line in lines:
        current_line = ""
        index = 0
        while index < len(line):
            # If adding the next character exceeds line length
            if len(current_line) + 1 > line_length:
                printer.text(current_line + "\n")
                current_line = ""
            # Add the current character to the current line
            current_line += line[index]
            index += 1
        # Print any remaining text in the current line
        if current_line:
            printer.text(current_line + "\n")


def start_server(ip, port):
    VENDOR_ID = 0x04B8  # Common vendor ID for Epson
    PRODUCT_ID = 0x0E27  # The correct product ID for your printer

    try:
        printer = Usb(VENDOR_ID, PRODUCT_ID)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
        print(f"Server listening on {ip}:{port}")
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print(f"Connection from {client_address}")
                buffer = []
                while True:
                    data = client_socket.recv(4096).decode("utf-8")
                    if "EOF" in data:
                        # Strip off the EOF marker
                        data = data.replace("EOF", "")
                        buffer.append(data)
                        break
                    buffer.append(data)
                full_text = "".join(buffer)
                if full_text:
                    print_text_line_by_line(printer, full_text)
                    printer.cut()
            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                client_socket.close()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        printer.close()
        server_socket.close()


if __name__ == "__main__":
    # Use the IP address and port you want to listen on
    LISTEN_IP = "0.0.0.0"  # Listen on all available interfaces
    LISTEN_PORT = 9100  # Choose an appropriate port number
    start_server(LISTEN_IP, LISTEN_PORT)
