import socket

def send_data_to_esp(host, port, message):
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect the socket to the ESP32 or ESP8266
        sock.connect((host, port))
        
        # Send the message
        sock.sendall(message.encode())
        
        # Close the connection
        sock.close()
        print(f"Sent: {message}")
        
    except Exception as e:
        print(f"Failed to send data: {e}")

if __name__ == "__main__":
    # Example host IPs and port numbers (ESP IPs)
    esp32_host = "192.168.0.102"  # Replace with your ESP32's IP address
    esp8266_host = "192.168.0.103"  # Replace with your ESP8266's IP address
    port = 8080  # The port on which ESP32/ESP8266 is listening

    # Example data to send
    message = "temperature:28,power_status:0"
    
    # Send to both ESP32 and ESP8266
    send_data_to_esp(esp32_host, port, message)
    # send_data_to_esp(esp8266_host, port, message)
