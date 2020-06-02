"""
Implement ssid scanner with the wifi library
Uses iwlist and must be run as root
"""
from wifi import Cell, Scheme


# Scan network for all visible BSSIDs
# Return a list of ('SSID', 'Mac Address', 'Signal Strength')

def getSSIDs():
    cells = Cell.all('wlp1s0') # Specify interface to scan on

    wifi_list = []
    for cell in cells:
        wifi_list.append((cell.ssid, cell.address, cell.signal))
    return wifi_list


# Given a config containing SSIDs
# List all BSSIDs under those SSIDs

def listBSSIDs(config):
    # @TODO implement config

    ssids = []
    valid_bssids = []
    for network in config:
        ssids.append(network)

    # Get all BSSIDs
    con_list = getSSIDs()
    for ssid in con_list:
        # Check for valid BSSIDs
        if ssid[0] in ssids:
            valid_bssids.append(ssid)

    return valid_bssids


# Display all visible BSSIDs
def main():
    for ap in getSSIDs():
        print(ap)


main()
