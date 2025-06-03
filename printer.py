import socket
from escpos.printer import Usb

BACKLOG_FILE = "print_backlog.txt"

def save_to_backlog(text):
    with open(BACKLOG_FILE, "a") as file:
        file.write(text + "\nEOF\n")

def load_backlog():
    try:
        with open(BACKLOG_FILE, "r") as file:
            return file.read().split("\nEOF\n")[:-1]
    except FileNotFoundError:
        return []

def clear_backlog():
    with open(BACKLOG_FILE, "w") as file:
        file.truncate(0)

def attempt_print(printer, text):
    try:
        print_text_line_by_line(printer, text)
        printer.cut()
        return True
    except Exception as e:
        print(f"Printing failed: {e}")
        return False

def print_backlog(printer):
    backlog = load_backlog()
    new_backlog = []
    for job in backlog:
        success = attempt_print(printer, job)
        if not success:
            new_backlog.append(job)  # Re-add to backlog if it fails
        else:
            clear_backlog()  # Clear existing backlog if any job succeeds
    save_backlog(new_backlog)  # Save any remaining jobs

def save_backlog(jobs):
    with open(BACKLOG_FILE, "w") as file:
        for job in jobs:
            file.write(job + "\nEOF\n")

def print_text_line_by_line(printer, text, line_length=48):
    lines = text.split('\n')
    for line in lines:
        current_line = ""
        index = 0
        while index < len(line):
            if len(current_line) + 1 > line_length:
                printer.text(current_line + '\n')
                current_line = ""
            current_line += line[index]
            index += 1
        if current_line:
            printer.text(current_line + '\n')

def start_server(ip, port):
    VENDOR_ID = 0x04b8
    PRODUCT_ID = 0x0e27

    try:
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
                    data = client_socket.recv(4096).decode('utf-8')
                    if 'EOF' in data:
                        data = data.replace('EOF', '')
                        buffer.append(data)
                        break
                    buffer.append(data)

                full_text = ''.join(buffer)
                if full_text:
                    try:
                        printer = Usb(VENDOR_ID, PRODUCT_ID)

                        # Attempt to print backlog
                        print_backlog(printer)

                        # Attempt to print the new message
                        if not attempt_print(printer, full_text):
                            save_to_backlog(full_text)

                    except Exception as e:
                        print(f"An error with printer: {e}")
                        save_to_backlog(full_text)

            except Exception as e:
                print(f"An error occurred during communication: {e}")
            finally:
                client_socket.close()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    LISTEN_IP = "0.0.0.0"
    LISTEN_PORT = 9100

    start_server(LISTEN_IP, LISTEN_PORT)