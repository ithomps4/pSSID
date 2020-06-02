from wifi import Cell, Scheme

wifi_list =  Cell.all('wlp1s0')

con_to = 0

for item in wifi_list:
    if item.ssid == 'ASUS_30_2G':
        con_to = item

print (con_to)

schemes = Scheme.all()
for scheme in schemes:
    scheme.delete()

passkey = 'M0d9!XdEnM9a'
scheme = Scheme.for_cell('wlp1s0', 'test', con_to, passkey)
scheme.activate()
