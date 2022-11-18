from ctypes import *
from threading import Thread
from time import sleep
import matplotlib.pyplot as plt
import numpy

ret_spi_transfer = 0


class SPI_CONFIG(Structure):
    _fields_ = [("freq", c_uint32),
                ("time_delay", c_float),
                ("mode", c_uint8),
                ("is_msb_First", c_bool),
                ("bits_per_word", c_uint8)]


class SPI_PINS(Structure):
    _fields_ = [("cs", c_int),
                ("clk", c_int),
                ("mosi", c_int),
                ("miso", c_int)]


# reference: https://www.digitalocean.com/community/tutorials/calling-c-functions-from-python
so_file = "./main.so"
c_lib = CDLL(so_file)


spi_config = SPI_CONFIG(1000000000, (100000000), 0, True, 8)


print(type(c_lib))

print(c_lib.config_set(spi_config))

sleep(1)


cs_list = []
clk_list = []
mosi_list = []
miso_list = []

# function to create threads


def get_spi_from_c():
    global ret_spi_transfer
    while (ret_spi_transfer != -1):
        # spi_pins = c_lib.get_spi()
        c_lib.get_spi.restype = c_void_p
        spi_pins = SPI_PINS.from_address(c_lib.get_spi())
        cs_list.append(spi_pins.cs)
        clk_list.append(spi_pins.clk)
        mosi_list.append(spi_pins.mosi)
        miso_list.append(spi_pins.miso)
        sleep(0.01)


spi_data_c = c_int * 8
spi_data = spi_data_c(0xA5, 2, 3, 4, 5, 6, 7, 8)


if __name__ == "__main__":
    c_lib.init_spi()
    thread = Thread(target=get_spi_from_c)
    print("starting thread")
    thread.start()
    ret_spi_transfer = c_lib.spi_transfer(spi_data, 1)
    thread.join()
    print("thread finished...exiting")
    cs = numpy.array(cs_list)
    clk = numpy.array(clk_list)
    mosi = numpy.array(mosi_list)
    miso = numpy.array(miso_list)

    x_samples = numpy.arange(0, len(clk_list))

    plt.plot(x_samples, cs, color='r', label='cs')
    plt.plot(x_samples, clk, color='g', label='clk')
    plt.plot(x_samples, mosi, color='b', label='mosi')
    plt.plot(x_samples, miso, color='y', label='miso')
    plt.show()

    print("done")
