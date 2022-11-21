#include <stdint.h>
#include <time.h>
#include <stdbool.h>

#ifndef CB_FIFO_H
#define CB_FIFO_H

#define MAX 512

typedef struct spi_pins
{
    int cs;
    int clk;
    int mosi;
    int miso;
    uint64_t time_ns;
} spi_pins_t;

typedef struct cbfifo
{
    spi_pins_t spi_pins_status[MAX];
    int head;
    int tail;
    int count;
} cbfifo_t;

// extern cbfifo_t cbfifo;
extern cbfifo_t *cbfifo_c;

void cbfifo_init();
void cbfifo_insert(spi_pins_t spi_pins);
spi_pins_t cbfifo_remove();
bool cbfifo_is_empty();
bool cbfifo_is_full();

#endif