# Systolic CNN AcceLErator Simulator (SCALE Sim) v3 #
# Integration of DRAM interface with the systolic array simulator #

SCALE-sim v3 integrates a detailed memory model with the systolic array computation. 
Users can evaluate the stall cycles due to data load from memory, bank conflicts and can experiment with different memory types (DDR3,DDR4 etc.) and configurations (channel, row etc.).
Currently we integrate Ramulator [Link] DRAM simulator in this design. 
The memory interface can be easily evaluated by performing the following steps:

### * Step 1a: Installing the dev-ramulator branch of the SCALE-Sim repository*
Follow the steps to get the SCALE-Sim source from github and then switch to the dev-ramulator branch
git checkout dev-ramulator

### * Step 1b: Installing the ramulator package*

# Get the latest source from ramulator github
cd submodules
git clone https://github.com/CMU-SAFARI/ramulator.git

# Copy the patch files to the ramulator codebase 
cp ../scripts/ramulator_patch ./ramulator

# Build ramulator
cd ramulator
make -j <num_jobs>

### Step 2: Run the SCALE-Sim simulator with cycle-accurate memory requests

After this step, you will have a ramulator executable in the ./ramulator folder which will be used to simulate the memory.
The ramulator integration is a multi-step process, where we need to first generate the demand trace by running the SCALE-Sim without any memory stalls. 
Next, the demand trace is fed to the Ramulator. Each memory request is tagged with an arrival time, based on when the request is sent to the Ramulator.
The Ramulator reports the response time of each individual requests. The memory round-trip time is saved in a numpy file.
SCALE-Sim is rerun with the memory round-trip latency for each request, capturing realistic pipeline stalls caused by memory delays and reporting the resulting execution time.
Below are the steps to run the SCALE-Sim simulator with the memory component.

source run_ramulator.sh 
OR
source run_ramulator_mnk.sh

### * Step 3: Plot the graphs to showcase the execution impact of memory components*

# Step 3a:  Impact of DRAM channels on memory throughput 

python scripts/plots/mem_bw_plot.py

# Step 3b: Report the stall cycles for different benchmarks

python scripts/plot/stall_plot.py
