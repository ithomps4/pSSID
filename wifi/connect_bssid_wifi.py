from wifi import Cell, Scheme

wifi_list =  Cell.all('wlp1s0')

con_to = 0

for item in wifi_list:
    if item.ssid == 'SSID_Name':
        con_to = item

print (con_to)

schemes = Scheme.all()
for scheme in schemes:
    scheme.delete()

passkey = 'Password123'
scheme = Scheme.for_cell('wlp1s0', 'test', con_to, passkey)
scheme.activate()
