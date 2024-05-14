#!/bin/bash

python3 memSim.py addresses.txt 10 "FIFO" > addressresult.txt
diff addressresult.txt addresscheck.txt
cmp addressresult.txt addresscheck.txt
# python3 memSim.py fifo1.txt 10 "FIFO" 
# python3 memSim.py fifo2.txt 5 "FIFO"
# python3 memSim.py fifo3.txt 5 "FIFO"
# python3 memSim.py fifo4.txt 5 "FIFO"
# python3 memSim.py fifo5.txt 8 "FIFO"
# python3 memSim.py lru1.txt 5 "LRU"
# python3 memSim.py lru2.txt 5 "LRU"
# python3 memSim.py lru3.txt 3 "LRU"
# python3 memSim.py opt1.txt 5 "OPT"
# python3 memSim.py opt2.txt 5 "OPT"

