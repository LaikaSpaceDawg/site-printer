import socket
from escpos.printer import Usb
from threading import Thread

BACKLOG_FILE = "print_backlog.txt"
TOKEN_FILE = "key"

def load_token():
    try:
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Token file not found.")
        return None

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
        printer.close()
        return True
    except Exception as e:
        print(f"Printing failed: {e}")
        printer.close()
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

def start_http_server(ip, port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(5)
        print(f"HTTP server listening on {ip}:{port}")
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                request = client_socket.recv(1024).decode('utf-8')
                # Parse HTTP request
                if request.startswith('GET / '):
                    # Respond with HTTP 200 OK
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Access-Control-Allow-Origin: *\r\n"  # CORS header
                        "Content-Length: 2\r\n"
                        "\r\n"
                        "OK"
                    )
                    client_socket.sendall(response.encode('utf-8'))
                else:
                    # Respond with HTTP 404 Not Found for other requests
                    response = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Length: 9\r\n"
                        "\r\n"
                        "Not Found"
                    )
                    client_socket.sendall(response.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                client_socket.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()

def start_printer_server(ip, port, expected_token):
    VENDOR_ID = 0x04b8
    PRODUCT_ID = 0x0e27
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
        print(f"Printer server listening on {ip}:{port}")
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print(f"Connection from {client_address}")
                received_data = client_socket.recv(4096).decode('utf-8')

                # Extract token from headers
                headers, _, body = received_data.partition('\r\n\r\n')
                token = None
                header_lines = headers.split('\r\n')
                new_header_lines = []
                
                for line in header_lines:
                    if line.startswith('Authorization:'):
                        _, token = line.split(" ", 1)
                        token = token.strip()
                    else:
                        new_header_lines.append(line)
                
                sanitized_data = body

                # Ensure token is valid
                if token != expected_token:
                    print(f"Invalid token received from {client_address}")
                    client_socket.close()
                    continue

                # Process data
                buffer = []
                while True:
                    if 'EOF' in body:
                        body = body.replace('EOF', '')
                        buffer.append(body)
                        break
                    buffer.append(body)
                    body = client_socket.recv(4096).decode('utf-8')
                
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
    # Load the token from the file
    token = load_token()
    if token is None:
        print("Exiting because the token could not be loaded.")
        exit(1)

    # Start HTTP server for status checks
    http_thread = Thread(target=start_http_server, args=('0.0.0.0', 8080))
    http_thread.start()

    # Start printer server
    start_printer_server('0.0.0.0', 9100, token)