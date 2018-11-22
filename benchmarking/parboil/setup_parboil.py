import subprocess
import os
import csv 
import re
import sys 

COMMANDS_FILES = "benchmark_commands_files.txt"
PARBOIL_LIST = "/parboil list"
PARBOIL_DESCRIBE = "/parboil describe"
PARBOIL_RUN = "/parboil run"
SUDO = "sudo "

def get_algorithm_list():
    bmlist = []
    cwd = os.getcwd()
    command = SUDO + cwd + PARBOIL_LIST 
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    #print(output.stdout) 
    line = output.stdout.split('\n')
    while '' in line:
       line.remove('') 
    bmlist = line[2:]
    #print(bmlist)
    return bmlist


def get_data_set(algo): 
    cwd = os.getcwd()
    command = SUDO + cwd + PARBOIL_DESCRIBE + algo 
    output2 = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    line2 = output2.stdout.split('\n')
    #print(line2)
    dataset = None  
    for i in line2:
       if "Data sets:" in i:
           dataset = i
           break
    #print(dataset) 
    dsize = dataset.split(":")
    #print(dsize[1]) 
    darray = dsize[1].lstrip().split(' ')
    #print(darray) 
    return darray

def create_command_file():
    print("In create_command_file....\n")
    bmlist = get_algorithm_list()
    #print(bmlist)
    cwd = os.getcwd()
    with open(COMMANDS_FILES, 'w') as fp:
       for bm in bmlist: 
          dataset = get_data_set(bm)  
          print("=>", bm)
          print(dataset)
          for ds in dataset: 
             cmd = SUDO + cwd + PARBOIL_RUN + bm + " cuda " + ds
             #print(cmd)
             fname = "out_"+bm.lstrip()+"_"+ds+".csv"
             print(fname)
             fp.write("".join('{} : {} \n'.format(fname, cmd)))
          print("\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
       if sys.argv[1] == "help":
          print(" Help text 1 \n")
          print(" Help text 2 \n")
          exit(0)
    create_command_file()

