import argparse
#!/usr/bin/python3


# class for page table using fifo 
class TLB:
    def __init__(self):
        self.num_max = 5
        self.dict = {}
        self.order = [] # queue used to keep track of FIFO

    def find(self, page_num):
        try:
            frame = self.dict.get(page_num)
            return frame
        except:
            return None
    
    def insert(self, page_num, frame_num):
        if frame_num in self.dict.values(): 
            for key, value in self.dict.items():
                if value == frame_num:
                    self.dict.pop(key)
                    self.order.remove(key)
                    break

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
            res = self.dict.get(page_num)
            if res[0] == 1:
                return res[1]
            else:
                return None
        except:
            return None
    
    def insert(self, page_num, frame_num):
        # check for (1,frame_num)
        if (1,frame_num) in self.dict.values(): 
            for key, value in self.dict.items():
                if value == (1,frame_num): 
                    self.dict[key] = (0,frame_num)
                    break
        self.dict[page_num] = (1,frame_num)       

class Memory:
    # class for the physical memory it will map frame number to the actual data 
    def __init__(self, frames, pra):
        self.dict = {}
        self.num_frames = frames
        self.order = [] # queue used to keep track of FIFO
        self.backing = "BACKING_STORE.bin"
        self.cur_frame = -1
        self.pra = pra
    
    
    def find(self, frame, offset):
        try:
            page = self.dict.get(frame)
            val = ((page[offset] + 128) & 0xFF) - 128
            return page, val
        except:
            return None, None
    
    def insert(self, frame, data):
        self.dict[frame] = data 
        if len(self.order) < self.num_frames:
            self.order.append(frame)
    
    def update_order(self,remove,insert):
        self.order.remove(remove)
        self.order.append(insert)

    ## sets the order to default order if frames filled
    def default_order(self):
        if len(self.order) >= self.num_frames:
            self.order = [i for i in range(self.num_frames)]

    def load_from_backing(self, page_num):
        with open(self.backing, "rb") as backing:
            backing.seek(256 * page_num)
            data = backing.read(256)
            backing.close()

        # if self.pra == "FIFO":
        #     if self.cur_frame >= self.num_frames:
        #         self.cur_frame = 0
        # elif self.pra == "LRU":
        if len(self.order) >= self.num_frames:
            self.cur_frame = self.order.pop(0)
            self.order.append(self.cur_frame)
        else:
            self.cur_frame += 1

        # elif self.pra == "OPT":
        #     if len(self.order) >= self.num_frames:
        #         self.cur_frame = self.order[0]
        self.insert(self.cur_frame, data)
        #print(self.order)

        return self.cur_frame
        


def main():
    parser = argparse.ArgumentParser(description="Virtual Memory Simulator")
    parser.add_argument("refseqfile", type=argparse.FileType(), help="Reference sequence file")
    parser.add_argument("frames", type=int, default=256, help="Number of Frames")
    parser.add_argument("pra", type=str, choices=["FIFO", "LRU", "OPT"], default="FIFO", help="Page Replacement Algorithm")

    args = parser.parse_args()
    frames = args.frames
    pra = args.pra
    file = args.refseqfile

    # frames = 5
    # file = "addresses.txt"
    # pra = "OPT"

    addresses = file.read().split("\n")
    for i, address in enumerate(addresses):
        try:
            addresses[i] = int(address)
        except:
            addresses.remove(address)

    # with open(file, "r") as f:
    #     for line in f:
    #         line = line.strip(("\n"))
    #         address = int(line)
    #         addresses.append(address)
    #     f.close()

    tlb = TLB()
    page_table = PageTable(frames)
    memory = Memory(frames, pra)

    tlb_hits = 0
    tlb_miss = 0
    page_fault = 0
    num_addresses = 0

    for index, address in enumerate(addresses):
        # calculate the page number and offset stuff
        page_num = (address >> 8) & 0xFF
        offset_num = address & 0xFF
        
        num_addresses += 1
        # look up in tlb
        frame_num = tlb.find(page_num)
    
        if frame_num is None:
            #if not in tlb look at the page table
            frame_num = page_table.find(page_num) 
            tlb_miss += 1   
            if frame_num is None:
                # if not in page table load from backing and put it in memory
                if pra == "OPT":
                    # check the next couple of address locations for the order we want
                    memory.default_order()
                    for a in reversed(addresses[index+1:]):
                        page_num_opt = (a >> 8) & 0xFF
                        # look up in tlb
                        frame_num_opt = page_table.find(page_num_opt)
                        if frame_num_opt is not None:
                            # this would be a hit, put at end of order
                            memory.update_order(frame_num_opt,frame_num_opt)

                frame_num = memory.load_from_backing(page_num)
                frame, val = memory.find(frame_num, offset_num)

                #print("PAGE_FAULT")
                page_table.insert(page_num, frame_num)
                tlb.insert(page_num, frame_num)
                page_fault += 1
            else :
                frame, val = memory.find(frame_num, offset_num)
                tlb.insert(page_num, frame_num)
        else :
            #print(frame_num, "HIT")
            if pra == "LRU":
                memory.update_order(frame_num,frame_num)
            frame, val = memory.find(frame_num, offset_num)
            tlb_hits += 1

       
        # print out all of the stats and everything needed.
        print(address, val, frame_num, frame.hex().upper(), sep=", ", end="\n")
        #print(frame)
        #print("\n")

    print("Number of Translated Addresses =", num_addresses)
    print("Page Faults =", page_fault)
    print("Page Fault Rate = {:.3f}".format(round(page_fault/num_addresses,3)))
    print("TLB Hits =", tlb_hits)
    print("TLB Misses =", tlb_miss)
    print("TLB Hit Rate = {:.3f}".format(round(tlb_hits/num_addresses,3)))

main()