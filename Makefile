# Copyright (C) 2022 Ben Tilley <targansaikhan@gmail.com>
# Distributed under terms of the MIT license.

# Usage:
# make		# <effect>

.PHONY: all

all: test

test:
	pytest
