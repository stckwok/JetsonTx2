import subprocess
import os
import time
import csv 
import re
import sys, getopt
import shutil
import setup_parboil as sp 

TEMP_OUTFILE = "temp_result.txt"
COMMANDS_FILES = "benchmark_commands_files.txt"
PROJECT_FOLDER = "project"
EXTENSION_CSV = "csv"
START_DIR = "./"
fullpath = os.path.join


def get_nv_power_mode():
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

def set_nv_power_mode(mode):
    """
    Jetson TX2 Development Kit new command line interface nvpmodel tool to set
    the new power modes.

    5 different Mode are : from 0 to 4, to set CPU cores used, and the maximum
    frequency of the CPU and GPU being used.

    Reference:
    see section "Usage" under table "nvpmodel mode definition"
    https://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/
    """
    mode_value = int(mode)
    if mode_value < 0 or mode_value > 4:
       print("Invalid value : ", mode_value , "must be between 0 to 4")
       return
    command = "sudo nvpmodel -m " + mode
    print(command)
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(output.stdout)


def make_dir(dirName):
    # Create target Directory if don't exist
    if not os.path.exists(dirName):
       os.mkdir(dirName)
       print("Directory " , dirName ,  " Created ")
    else:
       print("Directory " , dirName ,  " already exists")

def move_csvfile_project(mode):
    power_mode = PROJECT_FOLDER+"/"+mode
    print("NV Power Mode folder : ", power_mode)
    #make_dir(PROJECT_FOLDER)
    make_dir(power_mode)
    for dirname, dirnames, filenames in os.walk(START_DIR):
        for filename in filenames:
            source = fullpath(dirname, filename)
            if filename.endswith(EXTENSION_CSV):
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
    header = [] 
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
    print("header = \n", header)
    #print("------------------------------------------------------\n")

    time.sleep(2)
    with open(csvFileName, 'w') as csvFile:
       writer = csv.writer(csvFile)
       if os.path.getsize(csvFileName) == 0:
          writer.writerow(tuple(header))
    os.remove(filename)
                

def run_command(command, filename, csvFileName):
    #command = "sudo " + cwd + "/parboil run spmv cuda medium" + " > " + tmp
    #print(command)
    os.system(command)
    values = [] 
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
             values.append(float(val[1]))
    print("values = ", values)

    time.sleep(1)
    with open(csvFileName, 'a') as csvFile:
       writer = csv.writer(csvFile)
       if os.path.getsize(csvFileName) != 0:
          writer.writerow(tuple(values))
    os.remove(filename)
                

def create_benchmark_dictionary(filename):
    benchmark_dict = {}
    with open(filename) as f:
        for line in f:
           (key, val) = line.split(" : ")
           benchmark_dict[key] = val.splitlines()[0]
           print(key)
    return benchmark_dict

def exe_command(bm_dict, key, iters=3):
    command = bm_dict[key] + " > " + TEMP_OUTFILE 
    # if os.path.exists(csvFileName): return
    create_csvOutFileHeader(command, TEMP_OUTFILE, key)
    #print(key)
    print(command)
    for i in range(iters):
        run_command(command, TEMP_OUTFILE, key)

def print_usages():
   print("CSV ouput file format")
   print("Example :  out_spmv_large.csv ")
   print("where :")
   print("     algorithm = spmv") 
   print("     dataset = large\n")
   print("Usage: python exe_parboil.py -a <algorithm> -d <dataset> -n <iteration>")
   print("Example :  python exe_parboil.py -a spmv -d large -n 30 \n")
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
      print("Command File = " , COMMANDS_FILES ,  " Created ")
   else:
      print("Command File =  " , COMMANDS_FILES ,  " already exists")


def main(argv):
   create_command_file()
   algorithm = ''
   dataset = ''
   iteration = ''
   try:
      opts, args = getopt.getopt(argv,"ha:d:n:",["ifile=","ofile=","lfile" ])
      #opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","lfile" ])
   except getopt.GetoptError:
      print("test.py -a <algorithm> -d <dataset> -n <iteration>")
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
   print("Algorithm = ", algorithm)
   print("Dataset = ", dataset)
   print("Iteration = ", iteration)
   #create_command_file()

   csv_outfile = "out_"+algorithm+"_"+dataset+".csv"
   print(csv_outfile) 
   
   bm_dict = create_benchmark_dictionary(COMMANDS_FILES)
   #exe_command(bm_dict, "out_spmv_large.csv", 3)
   exe_command(bm_dict, csv_outfile, int(iteration))
   
   # clean up parboil folder by moving all csv files to project folder
   print("Moving csv file to project folder. Please check your result there...")
   time.sleep(2) 
   power_mode = get_nv_power_mode()
   print("Current Mode is: ", power_mode)
   move_csvfile_project(power_mode)


if __name__ == "__main__":
   main(sys.argv[1:])

