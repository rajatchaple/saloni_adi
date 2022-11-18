#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>

pthread_mutex_t lk;

int square(int i)
{
	return i * i;
}

typedef struct spi_pins
{
	int cs;
	int clk;
	int mosi;
	int miso;
} spi_pins_t;

spi_pins_t spi_pins;

typedef struct spi_config
{
	uint32_t freq;
	float time_delay;
	uint8_t mode;
	bool is_msb_First;
	uint8_t bits_per_word;
} spi_config_t;

spi_config_t spi_config;

spi_config_t config_set(spi_config_t spi_config_from_gui)
{
	spi_config.freq = spi_config_from_gui.freq;
	spi_config.time_delay = spi_config_from_gui.time_delay;
	spi_config.mode = spi_config_from_gui.mode;
	spi_config.is_msb_First = spi_config_from_gui.is_msb_First;
	spi_config.bits_per_word = spi_config_from_gui.bits_per_word;

	// TODO: print all configs
	printf("Freq: %d, Mode: %d, MSB_First? = %d, Bits_per_word = %d\n", spi_config.freq, spi_config.mode, spi_config.is_msb_First, spi_config.bits_per_word);

	return spi_config;
}

void init_spi()
{
	spi_pins.cs = 1;
	spi_pins.clk = 0;
	spi_pins.mosi = 0;
	spi_pins.miso = 0;

	pthread_mutex_init(&lk, NULL);
}

struct timespec delay_time;

void delay_ns(uint32_t nanosec)
{
	delay_time.tv_sec = 0;
	delay_time.tv_nsec = nanosec;

	if (nanosleep(&delay_time, NULL) != 0)
	{
		printf("Error: delay failed");
	}
}

void spi_start()
{
	delay_ns(spi_config.time_delay);
	spi_pins.cs = 1;
	spi_pins.clk = 0;
	spi_pins.cs = 0;
	delay_ns(spi_config.time_delay / 4);
}

void spi_stop()
{
	spi_pins.cs = 1;
	spi_pins.clk = 0;
	delay_ns(spi_config.time_delay);
}

// end of transfer is -1
int spi_transfer(uint8_t *data, uint32_t size)
{
	static uint32_t curr_byte = 0;
	uint32_t rem_byte_index = 0;
	while (curr_byte < size)
	{
		// spi start
		spi_start();

		for (int i = 0; i < spi_config.bits_per_word; i++)
		{
			// TODO: implement different modes
			//	delay_ns(spi_config.time_delay / 4);

			pthread_mutex_lock(&lk);
			spi_pins.mosi = ((data[curr_byte] >> i) & 0x01);
			pthread_mutex_unlock(&lk);

			delay_ns(spi_config.time_delay / 4);

			pthread_mutex_lock(&lk);
			spi_pins.clk = 1;
			pthread_mutex_unlock(&lk);

			delay_ns(spi_config.time_delay / 2);

			pthread_mutex_lock(&lk);
			spi_pins.clk = 0;
			pthread_mutex_unlock(&lk);

			delay_ns(spi_config.time_delay / 4);
		}

		// spi stop
		spi_stop();
		curr_byte++;
	}
	return -1;
}

spi_pins_t spi_curr_pins;

spi_pins_t *get_spi()
{
	pthread_mutex_lock(&lk);
	spi_curr_pins.cs = spi_pins.cs;
	spi_curr_pins.clk = spi_pins.clk;
	spi_curr_pins.mosi = spi_pins.mosi;
	spi_curr_pins.miso = spi_pins.miso;
	pthread_mutex_unlock(&lk);
	return &spi_curr_pins;
}