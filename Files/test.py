import socket
import geocoder

# Define the domain name
domain = "hnm.xiaohouzi.club"

# Perform a DNS lookup to get the IP address of the domain
try:
    ip_address = socket.gethostbyname(domain)
    print(f"IP Address of {domain}: {ip_address}")
except socket.gaierror:
    print(f"Couldn't resolve the IP address for {domain}")
    exit()

# Use the IP address to determine the geo location
try:
    location = geocoder.ip(ip_address)
    print(f"Geo location of {ip_address}:")
    print(f"Latitude: {location.latlng[0]}")
    print(f"Longitude: {location.latlng[1]}")
    print(f"City: {location.city}")
    print(f"Country: {location.country}")
except Exception as e:
    print(f"Failed to retrieve geo location: {str(e)}")
