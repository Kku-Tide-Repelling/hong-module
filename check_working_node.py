import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))
from LoRaRF import SX127x
import time


# Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
busId = 0; csId = 0
resetPin = 22; irqPin = 4; txenPin = -1; rxenPin = -1;
LoRa = SX127x()
#print("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

# Set frequency to 915 Mhz
#print("Set frequency to 915 Mhz")
LoRa.setFrequency(920900000)

# Set RX gain to boosted gain
#print("Set RX gain to boosted gain")
LoRa.setRxGain(LoRa.RX_GAIN_BOOSTED, LoRa.RX_GAIN_AUTO)

# Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
#print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
LoRa.setSpreadingFactor(7)
LoRa.setBandwidth(125000)
LoRa.setCodeRate(5)

# Configure packet parameter including header type, preamble length, payload length, and CRC type
#print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)
LoRa.setPreambleLength(12)
LoRa.setPayloadLength(15)
LoRa.setCrcEnable(True)

# Set syncronize word for public network (0x34)
#print("Set syncronize word to 0x34")
LoRa.setSyncWord(0x34)

packetData = ()

def getReceiveData() :

    global packetData
    # Store received data
    packetData = LoRa.read(LoRa.available())

# Register callback function to be called every RX done
LoRa.onReceive(getReceiveData)

# Request for receiving new LoRa packet in RX continuous mode
LoRa.request(LoRa.RX_CONTINUOUS)
# Receive message continuously
recall = "1"
data = f"{recall}"
encode_data = data.encode('utf-8')
data_list = list(encode_data)

while True:
    if packetData:
        # Print received message
        received_data = "".join([chr(packetData[i]) for i in range(len(packetData))])
        print(f"Received message from Node: {received_data}")

        if received_data == "1":
            LoRa.beginPacket()
            LoRa.write(data_list, len(data_list))
            LoRa.endPacket()
            LoRa.wait()
            print("Recall Complete")
            packetData = ""
        
        else:
            print("not found")
            packetData = ""

        time.sleep(5)