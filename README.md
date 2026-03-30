# Sort Algorithm Visualizer

A fully interactive sorting algorithm visualizer built with Pygame.


## What it does

* Visualizes sorting algorithms in real time
* Displays bars representing values being sorted
* Animates comparisons, swaps, and partitions
* Tracks internal operations like comparisons and swaps
* Runs at ~60 FPS using a generator-based update loop

---

## Algorithms included

Currently has **22 algorithms**, including:

* Bubble Sort
* Insertion Sort
* Selection Sort
* Merge Sort
* Quick Sort
* Heap Sort
* Shell Sort
* Radix Sort
* Counting Sort
* Tim Sort ...

…and also some *questionable life choices* like:

* Bogosort
* Stooge Sort
* Sleep Sort

---

### Keybinds
* `SPACE` → Start / Pause
* `S` / `→` → Step mode
* `R` → Shuffle values
* `+ / -` → Change speed
* `H` → Toggle UI
* `I` → Toggle info panel
* `M` → Toggle sound
* `F11` → Fullscreen
* `ESC` → Back / Exit
  
---

## Extra info

The visualizer tracks:
* Comparisons
* Swaps
* Partitions

It also shows:
* Time complexity (best / average / worst)
* Space complexity
* Short code snippets
* Random facts abt each algorithm

Each operation can generate sound using **procedurally generated waveforms**
(no audio files cuz i love complex experimenting).

---

## Notes

This project wasnt originally published.
It was just a fun little experiment thingy,
going from a simpler implementation and somehow turning into this Pygame ver. (ported from Tkinter... *500+ lines to rewrite*)

The code is in a single file, obviously
UI and logic are somewhat chaotic (intentionally left as is for now)
Explore it yourself, there are some constants so have fun with that too if you want
**Requirement**:
```bash
py -m pip install pygame
```
