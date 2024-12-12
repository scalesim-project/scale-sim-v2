import numpy as np 
import numba
import pandas as pd
import os
import multiprocessing as mp
import argparse
from tqdm import tqdm

mp.set_start_method('spawn',True)

rootPath= os.getcwd()
resultsPath = rootPath+"/results/"

class dram_latency():
    def __init__(self,
                ramulatorFile='',
                ):
        self.ramulatorFile = ramulatorFile
        self.ifmapLatency  = []
        self.filterLatency = []
        self.ofmapLatency  = []
        self.filterOffset  = 10000000
        self.ofmapOffset   = 20000000
        self.metaOffset    = 30000000
        self.fakeOffset    = 40000000
        self.bw = 10
    
    def latencyExtraction(self, layerNo, topo,shaper):
        print("starting to read file " + str(self.ramulatorFile))
        df = pd.read_csv(self.ramulatorFile,header=None,skipfooter=1,delimiter=' ',engine='python')
        print("file read")
        #df = df.sort_values(by=1,ignore_index=True)
        df = df.sort_values(2)
        print("sorting")
        latency = df[3]-df[2]
        print("latency")
        count=0
        flag=0
        lastIndex = 'ifmap'
        iterate=100000
        print(df.shape[0])
        while count < df.shape[0]:
            endIndex = count+self.bw - 1
            if count+self.bw > df.shape[0]:
                endIndex = df.shape[0] - 1
            if count > iterate:
                print("Iteration {} of {}".format(count,df.shape[0]))
                iterate+=100000
#            k=count
#            for i in range(count,count+self.bw):
#                a= df[2][k]
#                b=df[2][i]
#                m = a<self.ofmapOffset
#                n= b<self.ofmapOffset
#                ifmapAddress = df[2][k] < self.filterOffset and df[2][i] < self.filterOffset
#                filterAddress = df[2][k] < self.ofmapOffset and df[2][i] < self.ofmapOffset
#                ofmapAddress = not df[2][k] < self.ofmapOffset and not df[2][i] < self.ofmapOffset
#                if(ifmapAddress + filterAddress + ofmapAddress) == 0:
#                    if counter == 0:
#                        counter=1
#                    else:
#                        print("ERROR")
#                        print(df[2][count:count+10])
#                        print(k)
#                        print(i)
#                    k=i
            startAddress = int(df[1][count].split('x')[1],16)
            endAddress   = int(df[1][endIndex].split('x')[1],16)
            if shaper == 1:
                ifmapAddress =  startAddress < self.filterOffset
                filterAddress = startAddress < self.ofmapOffset
                ofmapAddress =  startAddress < self.metaOffset
            else:
                ifmapAddress =  startAddress < self.filterOffset and endAddress < self.filterOffset
                filterAddress = startAddress < self.ofmapOffset and endAddress < self.ofmapOffset
                ofmapAddress =  startAddress < self.metaOffset and endAddress < self.metaOffset

            if shaper == 1:
                #a=[]
                #for i in range(count,count+self.bw):
                #    a.append(df[2][i])

                if ifmapAddress:
                    self.ifmapLatency.append(np.amax(latency[count:count+self.bw]))
                    lastIndex = 'ifmap'
                elif filterAddress:
                    self.filterLatency.append(np.amax(latency[count:count+self.bw]))   
                    lastIndex = 'filter'

                elif ofmapAddress:
                    self.ofmapLatency.append(np.amax(latency[count:count+self.bw]))  
                    lastIndex = 'ofmap' 
                else:
                    if lastIndex == 'ifmap':
                        self.ifmapLatency.append(np.amax(latency[count:count+self.bw]))
                    elif lastIndex == 'filter':
                        self.filterLatency.append(np.amax(latency[count:count+self.bw]))  
                    else:
                        self.ofmapLatency.append(np.amax(latency[count:count+self.bw]))  
                count+=self.bw
            
            else:
                if ifmapAddress:
                    self.ifmapLatency.append(np.amax(latency[count:count+self.bw]))
                    count+=self.bw
                    lastIndex = 'ifmap'
                elif filterAddress:
                    self.filterLatency.append(np.amax(latency[count:count+self.bw]))  
                    count+=self.bw 
                    lastIndex = 'filter'
                elif ofmapAddress:
                    self.ofmapLatency.append(np.amax(latency[count:count+self.bw]))  
                    count+=self.bw
                    lastIndex = 'ofmap'
                else:                       # ---- This is the padding case... Very rare; so not optimized; lousy code
                    ifmapPad=0
                    filterPad=0
                    ofmapPad=0
                    metaPad=0
                    flag=0

                    #a = []
                    #for i in range(count,count+self.bw):
                    #    a.append(df[2][i])

                    for i in range(count,count+self.bw):
                        #print(df[2][i])
                        address = int(df[1][count].split('x')[1],16)
                        if address <self.filterOffset:
                            if(filterPad + ofmapPad + metaPad >0):
                                flag=1
                            else:
                                ifmapPad=1
                        elif address <self.ofmapOffset:
                            if(ifmapPad + ofmapPad+ metaPad >0):
                                flag=1
                            else:
                                filterPad=1
                        elif address < self.metaOffset:
                            if(filterPad + ifmapPad + metaPad>0):
                                flag=1
                            else:
                                ofmapPad=1
                        elif address < self.fakeOffset:
                            if(filterPad + ifmapPad + ofmapPad>0):
                                flag=1
                            else:
                                metaPad=1
                            
                        if flag==1:
                            if (ifmapPad == 1):
                                self.ifmapLatency.append(np.amax(latency[count:i]))
                                lastIndex = 'ifmap'
                            elif (filterPad == 1):
                                self.filterLatency.append(np.amax(latency[count:i]))                            
                                lastIndex = 'filter'
                            elif (ofmapPad == 1):
                                self.ofmapLatency.append(np.amax(latency[count:i]))   
                                lastIndex = 'ofmap'
                            elif metaPad == 1:
                                if lastIndex == 'ifmap':
                                    self.ifmapLatency.append(np.amax(latency[count:count+i]))
                                elif lastIndex == 'filter':
                                    self.filterLatency.append(np.amax(latency[count:count+i]))  
                                else:
                                    self.ofmapLatency.append(np.amax(latency[count:count+i]))  
                            count+=(i -count)
                            break


        np.asarray(self.ifmapLatency)
        np.asarray(self.filterLatency)
        np.asarray(self.ofmapLatency)

        #print("-------------------------- IFMAP Latency -------------------------")
        #print(self.ifmapLatency)
        #print("-------------------------- Filter Latency -------------------------")
        #print(self.filterLatency)
        #print("-------------------------- OFMAP Latency -------------------------")
        #print(self.ofmapLatency)

        np.save(resultsPath+"/"+topo+'_ifmapFile'+layerNo+'.npy',self.ifmapLatency)
        np.save(resultsPath+"/"+topo+'_filterFile'+layerNo+'.npy',self.filterLatency)
        np.save(resultsPath+"/"+topo+'_ofmapFile'+layerNo+'.npy',self.ofmapLatency)

    def check_integrity_address(self,address):
        address = address - self.metaOffset
        address 

def worker(fileName, topology,shaper):
    #layerNo = fileName.split('.')[0][len(topology)+9:]
    layerNo = fileName.split('.')[0].split('_')[-1]
    latencyFunc = dram_latency(ramulatorFile=resultsPath+fileName)
    latencyFunc.latencyExtraction(layerNo, topology,shaper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-topology', metavar='Topology file', type=str,
                        default="test_runs",
                        help="Directory path for the layers"
                        )
    parser.add_argument('-parallel', metavar='Run sequential or parallel', type=bool,
                        default=False,
                        help="Runs script in parallel for all layers"
                        )
    
    parser.add_argument('-shaper', metavar='Presence of shaper', type=bool,
                        default=False,
                        help="Define if shaper is present"
                        )
    args = parser.parse_args()
    topology = args.topology
    parallel = args.parallel
    shaper = args.shaper

    tracefiles = []
    for file in os.listdir(resultsPath):
        if file.startswith(topology+"_RamulatorTrace") and file.endswith(".trace"):
            tracefiles.append(file)
    for tracefile in tracefiles:
        if parallel:
            p = mp.Process(target=worker, args=(tracefile, topology,shaper))
            p.start()
        else:
            worker(tracefile, topology, shaper)
