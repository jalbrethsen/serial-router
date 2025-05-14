from machine import UART
import time

# define the UART pins and their port label
uarts = {
        0:{"tx":16,"rx":17}, # j5
        1:{"tx":19,"rx":18}, # j4
        2:{"tx":21,"rx":20}, # j3
        3:{"tx":23,"rx":22}  # j2
        }

def do_connect():
    '''
    Here we connect to the wifi, fill in the SSID and PASSWORD below.
    Use this if you want to use a webREPL, not necessary for the router to function
    '''
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ipconfig('addr4'))

def poll_uarts(to=50):
    '''
    We continuously poll each port to see if any of them are requesting a connection.
    We return the src port as well as the destination port (read from the UART of src)
    '''
    uart_keys = list(uarts.keys())
    while True:
        for uart in uart_keys:
            u = UART(1,tx=uarts[uart]["tx"],rx=uarts[uart]["rx"],timeout=to)
            data = u.readline()
            if data:
                if data.decode().isdigit():
                    if int(data.decode()) in uarts.keys():
                        return int(uart), int(data.decode())
        time.sleep_ms(to)

def connect_uarts(src_uart,dst_uart,to=50):
    '''
    We cannot have UART on all our pins, so we dynamically create a soft UART on the fly.
    Then we pipe the input and output of src UART to the dst and vice versa.
    To disconnect press ctl+d which gives the byte x04
    '''
    src = UART(1,tx=uarts[src_uart]["tx"],rx=uarts[src_uart]["rx"],timeout=to)
    dst = UART(0,tx=uarts[dst_uart]["tx"],rx=uarts[dst_uart]["rx"],timeout=to)
    src.write(b"\n\rconnected to uart {}!, ready to send\n\r".format(dst_uart))
    while True:
        src_dat = src.read(512)
        dst_dat = dst.read(512)
        if src_dat:
            dst.write(src_dat)
            if b"\x04" in src_dat:
                src.write(b"\n\rdisconnected from uart {}!, ready to send\n\r".format(dst_uart))
                time.sleep_ms(250)
                return    
        if dst_dat:
            src.write(dst_dat)



do_connect()
time.sleep(1)
while True:
    src,dst = poll_uarts(to=100)
    connect_uarts(src,dst,to=1)
