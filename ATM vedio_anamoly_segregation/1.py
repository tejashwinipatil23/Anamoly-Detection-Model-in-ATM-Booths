import socket
import struct

def ip_to_custom_hex(ip):
    # Convert the IP address to a 32-bit packed binary format
    packed_ip = socket.inet_aton(ip)
    
    # Unpack the binary format to a long integer
    unpacked_ip = struct.unpack("!L", packed_ip)[0]
    
    # Format the IP as a hexadecimal string
    hex_ip = format(unpacked_ip, '08X')
    
    # Extract the last two parts of the IP address in hexadecimal format
    third_part_hex = hex_ip[4:6]
    fourth_part_hex = hex_ip[6:8]
    
    # Combine to form the custom hexadecimal representation
    custom_hex_ip = f"::FFFF:CD{third_part_hex}{fourth_part_hex}"
    
    return custom_hex_ip

# Example IP address
ip_address = '192.168.10.92'
custom_hex_ip = ip_to_custom_hex(ip_address)

print(f"The custom hexadecimal representation of {ip_address} is {custom_hex_ip}")
