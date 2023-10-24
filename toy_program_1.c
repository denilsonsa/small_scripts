#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 15

typedef enum RuleType {
	Static, ShiftLeft, ShiftRight, Life, Sierpinski, Random, Flood
} RuleType;

typedef struct Pair {
	int x, y;
} Pair;

typedef struct Layer {
	RuleType rule;
	unsigned char brush;
	unsigned char bytes[SIZE][SIZE];
} Layer;

Layer evolve(Layer old) {
	Layer ret = old;
	int i, j;
	switch (old.rule) {
		case Static:
			break;
		case Random:
			for (i = 0; i < SIZE; i++) {
				for (j = 0; j < SIZE; j++) {
					ret.bytes[i][j] = (rand() < RAND_MAX / 32);
				}
			}
			break;
		case ShiftLeft:
			for (i = 0; i < SIZE; i++) {
				for (j = 0; j < SIZE; j++) {
					ret.bytes[i][j] = old.bytes[i][(j + 1) % SIZE];
				}
			}
			break;
		case ShiftRight:
			for (i = 0; i < SIZE; i++) {
				for (j = 0; j < SIZE; j++) {
					ret.bytes[i][j] = old.bytes[i][(j + SIZE - 1) % SIZE];
				}
			}
			break;
		case Sierpinski:
			for (i = 0; i < SIZE; i++) {
				int is_line_all_blank = 1;
				for (j = 0; j < SIZE; j++) {
					is_line_all_blank &= !old.bytes[(i + SIZE - 1) % SIZE][j];
				}
				if (is_line_all_blank) {
					/* Let's not propagate all blanks. */
					continue;
				}
				for (j = 0; j < SIZE; j++) {
					ret.bytes[i][j] =
						old.bytes[(i + SIZE - 1) % SIZE][(j + SIZE - 1) % SIZE] ^
						old.bytes[(i + SIZE - 1) % SIZE][(j + SIZE + 0) % SIZE];
				}
			}
			break;
		case Flood:
			for (i = 0; i < SIZE; i++) {
				for (j = 0; j < SIZE; j++) {
					ret.bytes[i][j] =
						old.bytes[(i + SIZE + 0) % SIZE][(j + SIZE + 0) % SIZE] |
						old.bytes[(i + SIZE - 1) % SIZE][(j + SIZE + 0) % SIZE] |
						old.bytes[(i + SIZE + 1) % SIZE][(j + SIZE + 0) % SIZE] |
						old.bytes[(i + SIZE + 0) % SIZE][(j + SIZE - 1) % SIZE] |
						old.bytes[(i + SIZE + 0) % SIZE][(j + SIZE + 1) % SIZE];
				}
			}
			break;
		case Life:
			Pair offsets[] = {
				{-1, -1},
				{-1,  0},
				{-1, +1},
				{ 0, -1},
				{ 0, +1},
				{+1, -1},
				{+1,  0},
				{+1, +1},
			};
			int k;
			for (i = 0; i < SIZE; i++) {
				for (j = 0; j < SIZE; j++) {
					int alive = 0;
					for (k = 0; k < 8; k++) {
						int x = j + offsets[k].x;
						int y = i + offsets[k].y;
						if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) {
							continue;
						}
						if (old.bytes[y][x]) {
							alive++;
						}
					}
					ret.bytes[i][j] = (old.bytes[i][j] && alive >= 2 && alive <= 3) || (!old.bytes[i][j] && alive == 3);

				}
			}
			break;
	}
	return ret;
}

void print_layers(Layer layers[], int length) {
	int i, j, k;
	for (i = 0; i < SIZE; i++) {
		for (k = 0; k < length; k++) {
			if (k > 0) {
				putchar('|');
			}
			for (j = 0; j < SIZE; j++) {
				putchar(layers[k].bytes[i][j] ? layers[k].brush : ' ');
			}
		}
		putchar('\n');
	}
}

void randomize_layer(Layer* layer, double probability) {
	int i, j;
	for (i = 0; i < SIZE; i++) {
		for (j = 0; j < SIZE; j++) {
			double value = rand() * 1.0 / RAND_MAX;
			layer->bytes[i][j] = value < probability;
		}
	}
}

void reset_layers(Layer layers[], int length) {
	randomize_layer(&layers[0], 1.0 / 2);
	randomize_layer(&layers[1], 1.0 / 8);
	randomize_layer(&layers[2], 1.0 / 16);
	randomize_layer(&layers[3], 0.0);
	randomize_layer(&layers[4], 1.0 / 4);
	randomize_layer(&layers[5], 1.0 / (SIZE * SIZE / 2));
	layers[3].bytes[0][0] = 1;
}

int main(int argc, char *argv[]) {
#define LAYERS_TOTAL 7
	Layer layers[LAYERS_TOTAL] = {
		{ .brush = '.', .rule = Static },
		{ .brush = '<', .rule = ShiftLeft },
		{ .brush = '>', .rule = ShiftRight },
		{ .brush = '^', .rule = Sierpinski },
		{ .brush = '#', .rule = Life },
		{ .brush = 'O', .rule = Flood },
		{ .brush = '?', .rule = Random }
	};

	srand(time(NULL));

	printf(
		"This is a simple toy program written in C in about one hour or less.\n"
		"It consists of several \"layers\" that have %dx%d binary cells.\n"
		"Each layer has a different rule, and a different character used to represent the active cells.\n"
		"\n"
		"Each newline in the input will \"evolve\" the layers according to their rules.\n"
		"The letter r/R will reset the layers (i.e. re-randomize their contents).\n"
		"The letter q/Q will quit this program.\n"
		"Have fun!\n"
		, SIZE, SIZE
	);

	reset_layers(layers, LAYERS_TOTAL);
	print_layers(layers, LAYERS_TOTAL);

	while (1) {
		int c = getchar();
		switch (c) {
			case EOF:
			case '\0':
			case 'q':
			case 'Q':
				return 0;
				break;
			case 'r':
			case 'R':
				reset_layers(layers, LAYERS_TOTAL);
				print_layers(layers, LAYERS_TOTAL);
				break;
			case '\n':
				int k;
				for (k = 0; k < LAYERS_TOTAL; k++) {
					layers[k] = evolve(layers[k]);
				}
				print_layers(layers, LAYERS_TOTAL);
				break;
		}
	}

	return 0;
}
