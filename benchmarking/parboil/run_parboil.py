"""
Module: run_parboil.py
interfaces to execute parboil benchmark and capture results to csv file for post analysis

    (1) Jetson TX2 Development Kit new command line interface nvpmodel tool to set
    the new power modes.

    5 different Mode are : from 0 to 4, to set CPU cores used, and the maximum
    frequency of the CPU and GPU being used.

    Reference:
    see section "Usage" under table "nvpmodel mode definition"
    https://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/

    (2) Create csv file with header extracted from executing benchmark commmand
     #  python measure_power.py -a spmv -d medium -n 1 -p 0 -c 0
     ('Algorithm = ', 'spmv')
     ('Dataset = ', 'medium')
     ('Iteration = ', '1')
     ('PowerMode = ', '0')
     ('CPU_Number = ', '0')
     ('command = ', 'python run_parboil.py -a spmv -d medium -n 1 -p 0 -c 0')

    Input:
        command - parboil executable with input arguments

    Output:
        filename - temp file containing the command output as following
        csvFileName - csv file (.csv) for a particular algorithm and dataset with following header and
                      the values row for each iteration
        'header = ', ['Start', 'IO', 'Kernel', 'Copy', 'Driver', 'CPU/KernelOverlap', 'TimerWallTime']
        'values = ', ['21:54:43', 0.871207, 0.55561, 0.561676, 0.560539, 0.560865, 2.135917])
"""


import subprocess
import os
import time
import csv
import re
import sys, getopt
import shutil
import setup_parboil as sp   # create_command_file
import nvp_freq_scaling as nfs

TEMP_OUTFILE = "temp_result.txt"
COMMANDS_FILES = "benchmark_commands_files.txt"
PROJECT_FOLDER = "project"
EXTENSION_CSV = "csv"
START_DIR = "./"
fullpath = os.path.join


def subprocess_run(cmd):
    output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    return output

def get_nv_power_mode():
    """
    Need file in order to save the output buffer from os.system("sudo nvpmodel -q")

    Can not run subprocess.run(cmd) in root (sudo su), which is required for changing
    CPU frequency with command
          # sudo echo 345600 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed
    """
    output = os.system("sudo nvpmodel -q > mfile.txt")
    last = "0"
    if not output:
       f = open("mfile.txt", "r")
       lines = f.read().splitlines()
       last = lines[-1]
       f.close()
    mode = "Mode-"+last
    print("mode is : ", mode)
    os.remove("mfile.txt")
    return mode

def set_nv_power_mode(mode):
    mode_value = int(mode)
    if mode_value < 0 or mode_value > 4:
       print(">>> Invalid value : ", mode_value , "Valid range is between 0 to 4 - Mode not changed ! ")
       return
    power_mode = get_nv_power_mode()
    if int(power_mode.split("-")[1]) == mode_value:
       print("> Current mode is already :", mode_value , " Mode not changed ! ")
       return

    command = "sudo nvpmodel -m " + mode
    print(command)
    #output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = os.system(command)
    print(" Change Mode Completed !")


def get_nv_power_mode2():
    """
    Jetson TX2 Development Kit new command line interface nvpmodel tool to get
    the current power modes.
    """
    output = subprocess.run("sudo nvpmodel -q", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    #print(output.stdout)
    line = output.stdout.strip().split('\n')
    print(line)
    #print(line[-1])
    mode = "Mode-"+line[-1]
    #print(mode)
    return mode

def set_nv_power_mode2(mode):
    """
    Jetson TX2 Development Kit new command line interface nvpmodel tool to set
    the new power modes.

    """
    mode_value = int(mode)
    if mode_value < 0 or mode_value > 4:
       print(">>> Invalid value : ", mode_value , "Valid range is between 0 to 4 - Mode not changed ! ")
       return
    power_mode = get_nv_power_mode()
    if int(power_mode.split("-")[1]) == mode_value:
       print(">>> Current mode is already: ", mode_value , "Mode not changed ! ")
       return

    command = "sudo nvpmodel -m " + mode
    print(command)
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(output.stdout)
    print(" Change Mode Completed !")


def make_dir(dirName):
    # Create target Directory if don't exist
    if not os.path.exists(dirName):
       os.mkdir(dirName)
       print("Directory " , dirName ,  " Created ")
    else:
       print("Directory " , dirName ,  " already exists")

def move_csvfile_to_project(mode, dev_freq, cpu, cpu_freq):
    power_mode = PROJECT_FOLDER+"/Mode-"+mode
    print("NV Power Mode folder : ", power_mode)
    #make_dir(PROJECT_FOLDER)
    make_dir(power_mode)
    cwd = os.getcwd()

    source = os.listdir(cwd)
    for filename in source:
       if filename.endswith(EXTENSION_CSV):
          print("filename = ", filename)
          f0 = filename.split(".")[0]
          #newfile = '{0}_{1}_{2}_{3}{4}{5}'.format(f0,cpu,cpu_freq,dev_freq,".",EXTENSION_CSV)
          newfile = '{0}_performance_{1}_{2}.{3}'.format(f0,cpu_freq,dev_freq,EXTENSION_CSV)
          print("newfile = ", newfile)
          if "power" not in newfile:
             shutil.move(fullpath(cwd, filename), fullpath(power_mode, newfile))

def walk_csvfile_project(mode):
    power_mode = PROJECT_FOLDER+"/"+mode
    print("NV Power Mode folder : ", power_mode)
    #make_dir(PROJECT_FOLDER)
    make_dir(power_mode)
    for dirname, dirnames, filenames in os.walk(START_DIR):
        for filename in filenames:
            source = fullpath(dirname, filename)
            if filename.endswith(EXTENSION_CSV):
                #shutil.move(source, fullpath(PROJECT_FOLDER, filename))
                shutil.move(source, fullpath(power_mode, filename))

def create_csvOutFileHeader(command, filename, csvFileName):
    """
    Create csv file with header extracted from executing benchmark commmand 
    Input:
        command - parboil executable with input arguments 
        filename - temp file containing the command output as following 
             IO        : 0.006263 
             Kernel    : 0.002121
             Copy      : 0.062402
             Driver    : 0.002118
             Compute   : 0.010395
             CPU/Kernel Overlap: 0.002143
             Timer Wall Time: 0.081228
        csvFileName - csv file (.csv) for a particular algorithm and dataset 
    """
    print(csvFileName)
    if os.path.exists(csvFileName):
        print("File already exist !!!.. \n") 
        return
 
    os.system(command)
    header = ["Start"]
    file = open(filename, 'r')
    
    for line in file:
       if (": " in line and "Allocating" not in line):
          if "IO" in line or \
             "Kernel" in line or \
             "Copy" in line or \
             "Driver" in line or \
             "CPU/Kernel Overlap:" in line or \
             "Timer Wall Time:" in line:
             val = re.sub(r'\s+', '', line).split(':') 
             header.append(val[0])
    print("header = ", header)

    #time.sleep(2)
    with open(csvFileName, 'w') as csvFile:
       writer = csv.writer(csvFile)
       if os.path.getsize(csvFileName) == 0:
          writer.writerow(tuple(header))
    os.remove(filename)
                

def run_command(command, csvFileName, start):
    #command = "sudo " + cwd + "/parboil run spmv cuda medium" + " > " + TEMP_OUTFILE
    os.system(command)
    values = []
    values.append(start) 
    file = open(TEMP_OUTFILE, 'r')
    
    for line in file:
       if (": " in line and "Allocating" not in line):
          if "IO" in line or \
             "Kernel" in line or \
             "Copy" in line or \
             "Driver" in line or \
             "CPU/Kernel Overlap:" in line or \
             "Timer Wall Time:" in line:
             val = re.sub(r'\s+', '', line).split(':') 
             values.append(float(val[1]))
    print("values = ", values)  # remove at runtime

    with open(csvFileName, 'a') as csvFile:
       writer = csv.writer(csvFile)
       if os.path.getsize(csvFileName) != 0:
          writer.writerow(tuple(values))
    os.remove(TEMP_OUTFILE)
                

def create_benchmark_dictionary(filename):
    benchmark_dict = {}
    with open(filename) as f:
        for line in f:
           (key, val) = line.split(" : ")
           benchmark_dict[key] = val.splitlines()[0]
           #print(key)   ## remove display of list at console
    return benchmark_dict

def exe_command(bm_dict, key, iters, powermode=None):
    command = bm_dict[key] + " > " + TEMP_OUTFILE 
    # if os.path.exists(csvFileName): return
    create_csvOutFileHeader(command, TEMP_OUTFILE, key)
    #print(key)
    #print(command)  # clean up console ouput

    # set powermode before executing
    if powermode is not None:
       set_nv_power_mode(powermode)
       time.sleep(1)

    #print(">>> ",time.strftime("%Y-%m-%d %H:%M:%S"))
    for i in range(iters):
        #run_command(command, TEMP_OUTFILE, key)
        #start = time.strftime("%Y-%m-%d %H:%M:%S")
        start = time.strftime("%H:%M:%S")
        #print("Iteration = {0} at {1} ".format(i, start))
        run_command(command, key, start)

    # capture end time to the last line of csv file.
    #endtime = time.strftime("%Y-%m-%d %H:%M:%S")
    endtime = time.strftime("%H:%M:%S")
    lastrow = []
    lastrow.append(endtime)
    for i in range(6):
       lastrow.append("0")

    with open(key, 'a') as csvFile:
       writer = csv.writer(csvFile)
       writer.writerow(lastrow)


def print_usages():
   print("CSV ouput file format")
   print("Example :  out_spmv_large.csv ")
   print("where :")
   print("     algorithm = spmv") 
   print("     dataset = large\n")
   print("Usage: python exe_parboil.py -a <algorithm> -d <dataset> -n <iteration> -p <powermode>")
   print("Example 1:  python exe_parboil.py -a spmv -d large -n 30 \n")
   print("Example 2:  python exe_parboil.py -a spmv -d large -n 50 -p 1")
   print("where : powermode valid range from 0 to 4")
   print(" Refer to Usage in table nvpmodel mode definition ")
   print(" https://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/ \n")
   print("-----------")
   print("Selections: ")
   print("-----------")
   benchmark_dict = {}
   with open(COMMANDS_FILES) as f:
      for line in f:
         (key, val) = line.split(" : ")
         benchmark_dict[key] = val.splitlines()[0]
         print(key)

def create_command_file():
   if not os.path.exists(COMMANDS_FILES):
      sp.create_command_file()
      print("Command File = " , COMMANDS_FILES,  " Created ")
   else:
      print("Command File = " , COMMANDS_FILES,  " already exists")


def main(argv):
   create_command_file()
   algorithm = ''
   dataset = ''
   iteration = ''
   powermode = '0'
   try:
      opts, args = getopt.getopt(argv,"ha:d:n:p:",["ifile=","ofile=","lfile","pfile"])
      #opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","lfile" ])
   except getopt.GetoptError:
      print("run_paraboil.py -a <algorithm> -d <dataset> -n <iteration> -p <powermode>")
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         #print("test.py -a <algorithm> -d <dataset> -n <iteration>")
         print_usages()
         sys.exit()
      elif opt in ("-a", "--ifile"):
         algorithm = arg
      elif opt in ("-d", "--ofile"):
         dataset = arg
      elif opt in ("-n", "--lfile"):
         iteration = arg
      elif opt in ("-p", "--pfile"):
         powermode = arg
   print("Algorithm = ", algorithm)
   print("Dataset = ", dataset)
   print("Iteration = ", iteration)
   print("PowerMode = ", powermode)

   csv_outfile = "out_"+algorithm+"_"+dataset+".csv"
   #print(csv_outfile)
   
   bm_dict = create_benchmark_dictionary(COMMANDS_FILES)
   #exe_command(bm_dict, csv_outfile, int(iteration), powermode)
   try:
      exe_command(bm_dict, csv_outfile, int(iteration), powermode)
   except ValueError:
      print("\n>>>> Please use command for usages : python run_parboil.py -h \n ")
      sys.exit(2)

   print("\n> Test stop at {0} ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
   # clean up parboil folder by moving all csv files to project folder
   print("\nMoving csv file to project folder. Please check your result there...")
   time.sleep(2) 
   power_mode = get_nv_power_mode()
   #print("Current Mode is: ", power_mode)
   #dev_max_freq = nfs.getting_dev_frequency("max_freq")
   #cpu0_freq = nfs.getting_cpu_frequency("cpu0")
   dev_max_freq = nfs.getting_dev_frequency(nfs.DEV_MAX)
   cpu0_freq = nfs.getting_cpu_frequency(nfs.CPU0)
   print("> GPU max feq = ", dev_max_freq)
   print("> CPU-0 feq = ", cpu0_freq)
   move_csvfile_to_project(power_mode, dev_max_freq, nfs.CPU0, cpu0_freq)


if __name__ == "__main__":
   main(sys.argv[1:])

