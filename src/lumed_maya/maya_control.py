import seabreeze 
seabreeze.use('cseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer

class MayaSpectrometer:

    def __init__(self):
        self.spectro = None
        self.isconnected = False
    def isSpectroAvailable(self):
        """
        Checks if any spectrometers are available to be connected
        """
        if len(list_devices()) != 0:
            return True
        else:
            return False
    
    def connect(self):
        """
        Connect the first available spectrometer to computer
        """
        #Connect first available spectrometer
        self.spectro = Spectrometer.from_first_available()
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
        self.spectro.integration_time_micros(exposure_time*1000) # *1000 because the exposure time is given in microseconds to the function
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
        return self.spectro.integration_time_micros_limits[0]/1000, self.spectro.integration_time_micros_limits[1]/1000


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    spectro = MayaSpectrometer()
    print("Maya available:", spectro.isSpectroAvailable())
    spectro.connect()
    print("Maya available2:", spectro.isSpectroAvailable())
    print("Maya spectro max count:", spectro.get_max_intensity())
    print("Maya exposure limits:", spectro.get_exposure_time_lims(),"ms")
    exposure = 100
    wavelengths, intensities = spectro.spectrum_acquisition(exposure)
    spectro.disconnect()
    plt.figure()
    plt.plot(wavelengths, intensities)
    plt.show()

