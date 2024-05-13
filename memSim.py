import argparse


# class for page table using fifo 
class TLB:
    def __init__(self):
        self.num_max = 16
        self.dict = {}
        self.order = [] # queue used to keep track of FIFO

    def find(self, page_num):
        try:
            page = self.dict.get(page_num)
            return page
        except:
            return None
    
    def insert(self, page_num, frame_num):
        self.dict[page_num] = frame_num
        self.order.append(page_num)

        if len(self.dict) > self.num_max:
            pn = self.order.pop(0)
            self.dict.pop(pn)

class PageTable:
    def __init__(self, frames):
        self.num_frames = frames
        self.dict = {}

    def find(self, page_num):
        try:
            page = self.dict.get(page_num)
            return page
        except:
            return None
    
    def insert(self, page_num, frame_num):
        self.dict[page_num] = frame_num       

class Memory:
    # class for the physical memory it will map frame number to the actual data 
    def __init__(self, frames):
        self.dict = {}
        self.num_frames = frames
        self.order = [] # queue used to keep track of FIFO
        self.backing = "BACKING_STORE.bin"
        self.cur_frame = -1
    
    
    def find(self, frame):
        try:
            page = self.dict.get(frame)
            return page
        except:
            return None
    
    ## this uses FIFO I think
    def insert(self, frame, data):
        self.dict[frame] = data 
        self.order.append(frame)

        if len(self.dict) > self.num_frames:
            fr = self.order.pop(0)
            self.dict.pop(fr)
    
    def load_from_backing(self, page_num):
        with open(self.backing, "rb") as backing:
            backing.seek(256 * page_num)
            data = backing.read(256)
            backing.close()
        self.cur_frame += 1

        self.insert(self.cur_frame, data)
        return self.cur_frame


def main():
    # parser = argparse.ArgumentParser(description="Virtual Memory Simulator")
    # parser.add_argument("refseqfile", type=argparse.FileType(), help="Reference sequence file")
    # parser.add_argument("frames", type=int, default=256, help="Number of Frames")
    # parser.add_argument("pra", type=str, default="FIFO", help="Page Replacement Algorithm")

    # args = parser.parse_args()
    # frames = args.frames
    # pra = args.pra
    # file = args.refseqfile
    frames = 256
    file = "addresses.txt"
    pra = "FIFO"

    addresses = []
    with open(file, "r") as f:
        for line in f:
            line = line.strip(("\n"))
            address = int(line)
            addresses.append(address)
        f.close()

    tlb = TLB()
    page_table = PageTable(frames)
    memory = Memory(frames)

    tlb_hits = 0
    tlb_miss = 0
    page_fault = 0
    num_addresses = 0

    for address in addresses:
        # calculate the page number and offset stuff
        page_num = (address >> 8) & 0xFF
        
        num_addresses += 1
        # look up in tlb
        frame_num = tlb.find(page_num)
    
        if frame_num is None:
            #if not in tlb look at the page table
            frame_num = page_table.find(page_num) 
            tlb_miss += 1   
            if frame_num is None:
                # if not in page table load from backing and put it in memory and 
                frame_num = memory.load_from_backing(page_num)
                frame = memory.find(frame_num)

                page_table.insert(page_num, frame_num)
                tlb.insert(page_num, frame_num)
                page_fault += 1
            else :
                frame = memory.find(frame_num)
        else :
            frame = memory.find(frame_num)
            tlb_hits += 1

       
        # print out all of the stats and everything needed.
        
        # i need to figure out what the value is 
        print(address, frame_num, frame)

    print("Number of Translated Addresses: ", num_addresses)
    print("Page Faults: ", page_fault)
    print("Page Fault Rate: ", page_fault/num_addresses)
    print("TLB Hits: ", tlb_hits)
    print("TLB Misses: ", tlb_miss)
    print("TLB Hit Rate: ", tlb_hits/num_addresses)


main()