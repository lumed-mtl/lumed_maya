import seabreeze

seabreeze.use("cseabreeze")
from seabreeze.spectrometers import list_devices, Spectrometer


class MayaSpectrometer:

    def __init__(self):
        self.spectro: Spectrometer = None
        self.device = None
        self.spectro_id: str = None
        self.isconnected = False

    def find_spectros(self):
        """
        find_spectros finds available devices

        Returns
        -------
        available_spectros: list of available devices
        """
        available_spectros = list_devices()
        return available_spectros

    def is_spectro_available(self):
        """
        Checks if any spectrometers are available to be connected
        """
        if len(list_devices()) != 0:
            return True
        else:
            return False

    def connect(self):
        """
        Connect to requested spectrometer
        """
        self.spectro = Spectrometer(self.device)
        self.isconnected = True
        print(f"Connected to spectrometer: {self.spectro}")

    def spectrum_acquisition(self, exposure_time):
        """
        Initiates a spectrum acquisition for a set exposure time and returns the measured counts with their associated wavelengths.

        ## Parameters:
        exposure_time: `float`\n
        exposure time given in units of ms

        ## Returns:
        combined array of wavelengths and measured intensities
        """
        # Set exposure time
        self.spectro.integration_time_micros(
            exposure_time * 1000
        )  # *1000 because the exposure time is given in microseconds to the function
        # Get wavelengths and intensities
        return self.spectro.spectrum()

    def disconnect(self):
        """Disconnect spectrometer"""
        self.spectro.close()
        self.isconnected = False
        print(f"Disconnected from spectrometer: {self.spectro}")

    def get_max_intensity(self):
        return self.spectro.max_intensity

    def get_exposure_time_lims(self):
        """Returns the upper and lower bounds of exposure time possible with the current spectrometer self.spectro"""
        return (
            self.spectro.integration_time_micros_limits[0] / 1000,
            self.spectro.integration_time_micros_limits[1] / 1000,
        )

    def get_model(self):
        """Returns the connected spectrometer's model"""
        return self.spectro.model

    def get_serial_number(self):
        """Returns the connected spectrometer's serial number"""
        return self.spectro.serial_number


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    spectro = MayaSpectrometer()
    spectro.device = spectro.find_spectros()[0]
    print("available devices:", spectro.find_spectros())
    print("Maya available:", spectro.is_spectro_available())
    # spectro.connect2()
    # print(type(spectro.spectro))
    spectro.connect()
    print(type(spectro.spectro))
    print("Maya available2:", spectro.is_spectro_available())
    print("Maya spectro max count:", spectro.get_max_intensity())
    print("Maya exposure limits:", spectro.get_exposure_time_lims(), "ms")
    exposure = 100
    wavelengths, intensities = spectro.spectrum_acquisition(exposure)
    spectro.disconnect()
    plt.figure()
    plt.plot(wavelengths, intensities)
    plt.show()
