// create a  cicruclar buffer fifo

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#include <pthread.h>
#include "cbfifo.h"

cbfifo_t *cbfifo_c;

void cbfifo_init(cbfifo_t *cbfifo)
{
    cbfifo_c = cbfifo;
    cbfifo_c->head = 0;
    cbfifo_c->tail = 0;
    cbfifo_c->count = 0;

    // while (cbfifo_c != NULL)
    // {
    //     // remove all elements
    //     cbfifo_remove(cbfifo_c);
    // }
}

bool cbfifo_is_full()
{
    return cbfifo_c->count == MAX;
}

bool cbfifo_is_empty()
{
    return cbfifo_c->count == 0;
}

void cbfifo_insert(spi_pins_t spi_pins)
{
    if (cbfifo_is_full(cbfifo_c))
    {
        printf("cbfifo is full\n");
        return;
    }
    cbfifo_c->spi_pins_status[cbfifo_c->head].cs = spi_pins.cs;
    cbfifo_c->spi_pins_status[cbfifo_c->head].clk = spi_pins.clk;
    cbfifo_c->spi_pins_status[cbfifo_c->head].mosi = spi_pins.mosi;
    cbfifo_c->spi_pins_status[cbfifo_c->head].miso = spi_pins.miso;
    cbfifo_c->spi_pins_status[cbfifo_c->head].time_ns = spi_pins.time_ns;
    cbfifo_c->head = (cbfifo_c->head + 1) % MAX;
    cbfifo_c->count++;
}

spi_pins_t cbfifo_remove()
{
    spi_pins_t spi_pins;
    if (cbfifo_is_empty(cbfifo_c))
    {
        printf("cbfifo is empty\n");
        return spi_pins;
    }
    spi_pins.cs = cbfifo_c->spi_pins_status[cbfifo_c->tail].cs;
    spi_pins.clk = cbfifo_c->spi_pins_status[cbfifo_c->tail].clk;
    spi_pins.mosi = cbfifo_c->spi_pins_status[cbfifo_c->tail].mosi;
    spi_pins.miso = cbfifo_c->spi_pins_status[cbfifo_c->tail].miso;
    spi_pins.time_ns = cbfifo_c->spi_pins_status[cbfifo_c->tail].time_ns;
    cbfifo_c->tail = (cbfifo_c->tail + 1) % MAX;
    cbfifo_c->count--;
    return spi_pins;
}

// get the number of elements in the cbfifo
int cbfifo_count()
{
    return cbfifo_c->count;
}