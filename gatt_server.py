import dbus
import dbus.service
import dbus.mainloop.glib
import dbus.exceptions
try:
  from gi.repository import GObject
except ImportError:
    import gobject as GObject
import array
import os
from bletools import BleTools

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
DBUS_OM_IFACE =      "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE =    "org.freedesktop.DBus.Properties"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE =    "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE =    "org.bluez.GattDescriptor1"

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"

class Application(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GObject.MainLoop()
        self.bus = BleTools.get_bus()
        self.path = "/"
        self.services = []
        self.next_index = 0
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature = "a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

    def register_app_callback(self):
        print("GATT application registered")

    def register_app_error_callback(self, error):
        print("Failed to register application: " + str(error))

    def register(self):
        adapter = BleTools.find_adapter(self.bus)

        service_manager = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                GATT_MANAGER_IFACE)

        service_manager.RegisterApplication(self.get_path(), {},
                reply_handler=self.register_app_callback,
                error_handler=self.register_app_error_callback)

    def run(self):
        self.mainloop.run()

    def quit(self):
        print("\nGATT application terminated")
        self.mainloop.quit()

class VideoCharacteristic(dbus.service.Object):
    def __init__(self, index, video_path):
        self.path = '/org/bluez/example/char' + str(index)
        self.bus = BleTools.get_bus()
        self.uuid = '0000ffff-0000-1000-8000-00805f9b34fb'
        self.flags = ['write']
        self.video_path = video_path
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        if 'write-auxiliaries' in self.flags:
            print('Write request received')
            try:
                with open(self.video_path, 'rb') as f:
                    while True:
                        chunk = f.read(128)  # Adjust the chunk  # Adjust the chunk size as needed
                        if not chunk:
                            break
                        self.PropertiesChanged(
                            GATT_CHRC_IFACE,
                            {'Value': dbus.ByteArray(chunk)},
                            [])
            except Exception as e:
                print(f'Error while sending video data: {str(e)}')
        else:
            print('Write request not permitted')
            raise NotPermittedException()

class VideoService(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, index, video_path):
        self.bus = BleTools.get_bus()
        self.path = self.PATH_BASE + str(index)
        self.uuid = '0000aaaa-0000-1000-8000-00805f9b34fb'
        self.primary = True
        self.characteristics = []
        self.next_index = 0
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.add_characteristic(VideoCharacteristic(self.next_index, video_path))

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

def main():
    app = Application()

    video_path = "/home/hyun/project/data.mp4"  # Adjust the video file path

    service = VideoService(0, video_path)
    app.add_service(service)

    app.register()
    app.run()

if __name__ == '__main__':
    main()

