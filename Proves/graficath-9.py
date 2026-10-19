import serial
import matplotlib.pyplot as plt

device = 'COM7'
ser = serial.Serial(device, baudrate=9600)

plt.ion()
plt.axis([0,100,20,100])
temperaturas = []
humedades = []

eje_x = []
i = 0

try: 
   while True:
      if ser.in_waiting > 0:
         line = ser.readline().decode('utf-8').rstrip()
         print (line)
         trozos = line.split (':')
         eje_x.append (i) 
         temperatura = float(trozos[1])
         temperaturas.append(temperatura)
         humedad = float(trozos[3])
         humedades.append(humedad)
         plt.plot(eje_x,temperaturas)
         plt.plot(eje_x,humedades)

         plt.title(str(i))
         i = i+1
         plt.draw()
         plt.pause(0.5)

except KeyboardInterrupt:
   print ("Saliendo...")
finally:
   ser.close()



