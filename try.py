from ctypes import *
from threading import Thread
from time import sleep

import matplotlib.pyplot as plt
import numpy

# import matplotlib
# matplotlib.rcParams['interactive'] == True

# print(plt.get_backend())

ret_spi_transfer = 0

MAX = 512

so_file = "./main.so"
c_lib = CDLL(so_file)

# https://stackoverflow.com/questions/54888242/passing-nested-ctypes-structure-with-array-to-c-library-function-not-as-expected


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
                ("miso", c_int),
                ("time_ns", c_uint64)]


SPI_PINS_MAX = SPI_PINS * MAX


class CBFIFO(Structure):
    _fields_ = [("spi_pins_status", SPI_PINS_MAX),
                ("head", c_int),
                ("tail", c_int),
                ("count", c_int)]

    def __init__(self, data):
        self.spi_pins_status = SPI_PINS_MAX()
        self.head = 0
        self.tail = 0
        self.count = 0
        for i in range(len(data)):
            self.spi_pins_status[i].cs = data[i][0]
            self.spi_pins_status[i].clk = data[i][1]
            self.spi_pins_status[i].mosi = data[i][2]
            self.spi_pins_status[i].miso = data[i][3]
            self.spi_pins_status[i].time_ns = data[i][4]
            self.count = 0


# def circular_buffer():
#     class CBFIFO(Structure):
#         _fields_ = [("spi_pins_status", SPI_PINS * MAX),
#                     ("head", c_int),
#                     ("tail", c_int),
#                     ("count", c_int)]
#     return CBFIFO
# reference: https://www.digitalocean.com/community/tutorials/calling-c-functions-from-python
sleep(1)


cs_list = []
clk_list = []
mosi_list = []
miso_list = []
time_stamps_list = []

# function to create threads

# cbfifo_gen_c = c_uint64 * 8
# cbfifo_gen = CBFIFO(SPI_PINS(0, 0, 0, 0, 0), 0, 0, 0)

spi_pins_list = [[-1 for i in range(5)] for j in range(MAX)]
cbfifo_gen_c = CBFIFO(spi_pins_list)


c_lib.cbfifo_init(cbfifo_gen_c)


def get_spi_from_c():
    global ret_spi_transfer

    print("Getting parameters")
    c_lib.get_spi.restype = POINTER(SPI_PINS)
    while True:
        ret_spi_transfer = c_lib.get_spi(cbfifo_gen_c)
        if ret_spi_transfer:
            cs_list.append(ret_spi_transfer.contents.cs)
            clk_list.append(ret_spi_transfer.contents.clk)
            mosi_list.append(ret_spi_transfer.contents.mosi)
            miso_list.append(ret_spi_transfer.contents.miso)
            time_stamps_list.append(ret_spi_transfer.contents.time_ns)
            sleep(0.1)
        else:
            print("No more SPI transfer")
            break


spi_data_c = c_uint64 * 8
spi_data = spi_data_c(0xA5, 0xB0, 3, 4, 5, 6, 7, 8)


if __name__ == "__main__":
    mode = input("Enter required SPI mode (i.e, 0,1,2,3): ")
    print(mode)
    msb_first = input("MSB first? (enter True/False): ")
    print(msb_first)
    bits_per_word = input("Enter required bits per word (i.e., 8,16,32,64): ")
    print(bits_per_word)
    spi_config = SPI_CONFIG(500, 2000000, int(
        mode), msb_first, int(bits_per_word))
    c_lib.config_set(spi_config)
    sleep(1)
    c_lib.init_spi()

    print("Starting SPI generator")

# get number of elements in cbfifo from c_lib
    c_lib.cbfifo_count.restype = c_int
    cbfifo_count = c_lib.cbfifo_count(cbfifo_gen_c)
    print("cbfifo_count: ", cbfifo_count)

    ret_spi_transfer = c_lib.spi_transfer(spi_data, 1)
    print("SPI transfer finished...exiting")

    # get number of elements in cbfifo from c_lib
    c_lib.cbfifo_count.restype = c_int
    cbfifo_count = c_lib.cbfifo_count(cbfifo_gen_c)
    print("cbfifo_count: ", cbfifo_count)

    get_spi_from_c()

    # print("cs_list: ", cs_list)
    # print("clk_list: ", clk_list)
    # print("mosi_list: ", mosi_list)
    # print("miso_list: ", miso_list)
    # print("time_stamps_list: ", time_stamps_list)

    # modified timestamp starts from 0
    time_stamps_list = [x - time_stamps_list[0] for x in time_stamps_list]

    cs = numpy.array(cs_list)
    clk = numpy.array(clk_list)
    mosi = numpy.array(mosi_list)
    miso = numpy.array(miso_list)
    timestamp = numpy.array(time_stamps_list)

    # print cs, clk, mosi, miso, timestamp
    print("cs: ", cs)
    print("clk: ", clk)
    print("mosi: ", mosi)
    print("miso: ", miso)
    print("timestamp: ", timestamp)

    plt.plot([1, 2, 3])

    plt.show()
    # plt.show(block=True)

    # # plot the data in dfferent colors
    # plt.plot(timestamp, cs, color='r', label='cs')
    # plt.plot(timestamp, clk, color='g', label='clk')
    # plt.plot(timestamp, mosi, color='b', label='mosi')
    # plt.plot(timestamp, miso, color='y', label='miso')
    # plt.legend(loc='upper left')
    # plt.xlabel('Time (ns)')
    # plt.ylabel('SPI pins status')
    # plt.title('SPI pins status vs Time')
    # plt.show()

    print("Exiting")

    print("done")
