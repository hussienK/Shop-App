import cv2

def list_ports():
    # test the ports and return a tuple of avaliables ports

    dev_port = 0
    non_working_ports = []
    working_ports = []
    avaliable_ports = []

    while (len(non_working_ports) < 6): #if there is more than 5 none working ports stop
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print(f"port {dev_port} is not working")
        
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(f"Port {dev_port} is wokring and reads {h}, {w}")
            else:
                print(f"print {dev_port} for camera {h}, {w} is presnt but does not read")
                avaliable_ports.append(dev_port)
        dev_port += 1
    return avaliable_ports, working_ports, non_working_ports

list_ports()
