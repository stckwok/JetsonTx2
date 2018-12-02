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


def test_fix_DEV_var_CPU_freq(dev_max_freq, cmd, bm_dict, csv_outfile, iteration, powermode):

    if "-c " in cmd:
       # run just one CPU
       print("One CPU used")
       print("Command is : ", cmd)
       cpu_num = 'cpu{0}'.format(cmd[-1:])
       print("CPU number is :", cpu_num)
       for cpu_freq in nfs.CPU_FREQ:
          nfs.setting_cpu_frequency(cpu_num, cpu_freq)
          nfs.getting_cpu_frequency(cpu_num)
          try:
             rp.exe_command(bm_dict, csv_outfile, int(iteration), powermode)
          except ValueError:
             print("\n>>>> Please use command for usages : python run_parboil.py -h \n ")
             sys.exit(2)
             print("\n> Test stop at {0} ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
          # clean up parboil folder by moving all csv files to project folder
          print("\nMoving csv file to project folder. Please check your result there...")
          time.sleep(2)
          print("> GPU max feq = ", dev_max_freq)
          print("> {0} feq = ".format(cpu_freq))
          rp.move_csvfile_to_project(powermode, dev_max_freq, cpu_num, cpu_freq)
 
    else:
       #for each GPU fixed one frequency:
       for cpu_num in nfs.CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
          nfs.setting_cpu_userspace(cpu_num)
          for cpu_freq in nfs.CPU_FREQ:
             nfs.setting_cpu_frequency(cpu_num, cpu_freq)
             nfs.getting_cpu_frequency(cpu_num)
             # Start power Meter 
             # wait 5 seconds
             # Execute workload 
             # python run_parboil.py -a spmv -d large -n 2 -p 0
             command = cmd + " -c " + cpu_num[-1:]
             print(command)
 
def test_fix_CPU_var_DEV_freq(cpu_freq, cmd):
    for dev_freq in nfs.DEV_FREQ:
       setting_dev_max_frequency(dev_freq)
       getting_dev_frequency(nfs.DEV_MAX)
       # Start power Meter 
       # wait 5 seconds
       # Execute workload 

def get_input_options(argv):
   #create_command_file()
   algo = ''
   dset = ''
   itrs = ''
   pmode = '0' 
   cpunum = ''
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
    if cpunum == '':
       command = 'python run_parboil.py -a {0} -d {1} -n {2} -p {3}'.format(algo, dset, itrs, pmode)
    else:
       command = 'python run_parboil.py -a {0} -d {1} -n {2} -p {3} -c {4}'.format(algo, dset, itrs, pmode, cpunum)
    print("command = ", command)
    #os.system("python run_parboil.py -a spmv -d large -n 2 -p 0")
    #os.system("python run_parboil.py -a bfs -d UT -n 1 -p 0")

    csv_outfile = "out_"+algo+"_"+dset+".csv"
    #print(csv_outfile)
    bm_dict = rp.create_benchmark_dictionary(rp.COMMANDS_FILES)
    #print("BM Dict: ", bm_dict)
    dev_max_freq = nfs.getting_dev_frequency(nfs.DEV_MAX)
    #print("GPU Max Freq: ", dev_max_freq)
    test_fix_DEV_var_CPU_freq(dev_max_freq, command, bm_dict, csv_outfile, int(itrs), pmode)


    #test_fix_CPU_var_DEV_freq()
    print(nfs.get_list_cpu_freq())
    print("----------------")


if __name__ == "__main__":
   main(sys.argv[1:])
