import os
import time
import sys, getopt
import run_parboil as rp
import nvp_freq_scaling as nfs 

# external power measurement
#sudo ./wattsup ttyUSB0 watts volts amps > spmv_large_30_345600_ext.csv

# internal power measurement (preferred method)
# sudo ./pwr -h
# Reads the power information from the INA3221 device on the Jetson TX2 board.
# option '-f <csv file>' writes a CSV file. If the file already exists the values will be appended at the end.
# option '-c <number>' loops 'number' times, can be used with -t.
# option '-t <period>' takes a sample every 'period' miliseconds, can be used with -c.



def test_fix_DEV_var_CPU_freq(dev_freq, cmd):

    if "-c " in cmd:
       # run just one CPU
       print("One CPU used")
    else:
       #for each GPU fixed one frequency:
       for cpu_num in nfs.CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
          setting_cpu_userspace(cpu_num)
          for cpu_freq in nfs.CPU_FREQ:
             setting_cpu_frequency(cpu_num, cpu_freq)
             getting_cpu_frequency(cpu_num)
             # Start power Meter 
             # wait 5 seconds
             # Execute workload 
             # python run_parboil.py -a spmv -d large -n 2 -p 0
 
def test_fix_CPU_var_DEV_freq(cpu_freq, cmd):
    for dev_freq in nfs.DEV_FREQ:
       setting_dev_max_frequency(dev_freq)
       getting_dev_frequency(nfs.DEV_MAX)
       # Start power Meter 
       # wait 5 seconds
       # Execute workload 

def get_input_options(argv):
   #create_command_file()
   algo = 'spmv'
   dset = 'large'
   itrs = '1'
   pmode = '0' 
   cpunum = '0'
   try:
      opts, args = getopt.getopt(argv,"ha:d:n:p:c:",["ifile=","ofile=","lfile","pfile","cfile"])
   except getopt.GetoptError:
      print("test.py -a <algorithm> -d <dataset> -n <iteration> -p <powermode> -c <cpunumber>")
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print_usages()
         sys.exit()
      elif opt in ("-a", "--ifile"):
         algo = arg
      elif opt in ("-d", "--ofile"):
         dset = arg
      elif opt in ("-n", "--lfile"):
         itrs = arg
      elif opt in ("-p", "--pfile"):
         pmode = arg
      elif opt in ("-c", "--cfile"):
         cpunum = arg
   print("Algorithm = ", algo)
   print("Dataset = ", dset)
   print("Iteration = ", itrs)
   print("PowerMode = ", pmode)
   print("CPU_Number = ", cpunum)
   return (algo, dset, itrs, pmode, cpunum)


def main(argv):
    print("----------------")
    for cpu_num in nfs.CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
        print("cpu_num = ", cpu_num)
    (algo, dset, itrs, pmode, cpunum) = get_input_options(argv)
    command = 'python run_parboil.py -a {0} -d {1} -n {2} -p {3} -c {4}'.format(algo, dset, itrs, pmode, cpunum)
    print("command = ", command)
    #os.system("python run_parboil.py -a spmv -d large -n 2 -p 0")
    #os.system("python run_parboil.py -a bfs -d UT -n 1 -p 0")

    #test_fix_DEV_var_CPU_freq()
    #test_fix_CPU_var_DEV_freq()
    print(nfs.get_list_cpu_freq())
    print("----------------")


if __name__ == "__main__":
   main(sys.argv[1:])
