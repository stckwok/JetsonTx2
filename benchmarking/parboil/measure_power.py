"""
Module: measure_power.py
This module perform the actual power measurement for the selected bechmark by user

# external power measurement
#sudo ./wattsup ttyUSB0 watts volts amps > spmv_large_30_345600_ext.csv

# internal power measurement (preferred method)
# sudo ./pwr -h
# Reads the power information from the INA3221 device on the Jetson TX2 board.
# option '-f <csv file>' writes a CSV file. If the file already exists the values will be appended at the end.
# option '-c <number>' loops 'number' times, can be used with -t.
# option '-t <period>' takes a sample every 'period' miliseconds, can be used with -c.

Usages:
    Fix GPU frequency and varies CPU freq

    When -c <cpu_number> is used, power measurement is performed to that CPU core over
    each available GPU freq against all availabe CPU freq.

    This must be executed in root mode because setting frequency on the device is required
    to be in root mode "sudo su"
    Example:
            $ sudo su
            # python measure_power.py -a spmv -d large -n 1 -p 0 -c 1
"""
import os
import time
import sys, getopt
import shutil
import run_parboil as rp
import nvp_freq_scaling as nfs
fullpath = os.path.join

POWER_MEASURE_PERIOD = "100"  # msec
POWER_FOLDER = "POWER"
PWR_EXEC = "/WorkDir/00_measurement/jetsonTX2Power/c/pwr"
HOME_DIR = "/home/sam"   # os.environ['HOME']

def start_power_meter(csv_file, dev_max_freq, cpu_freq, cpu_num, period):
    f0 = csv_file.split(".")[0]
    #pfile = '{0}_power_gpu_{1}_{2}_{3}.csv'.format(f0, dev_max_freq, cpu_num, cpu_freq)
    pfile = '{0}_power_{1}_{2}.csv'.format(f0, cpu_freq, dev_max_freq)
    p0 = str(period)
    pmeter_cmd = 'sudo {0}{1} -f {2} -t {3} &'.format(HOME_DIR, PWR_EXEC, pfile, p0)
    print("START >>> Power Meter Cmd : ", pmeter_cmd)
    os.system(pmeter_cmd)


def stop_power_meter():
    print("STOP >>> Power Meter...")
    kill_cmd = 'sudo pkill -9 pwr'
    os.system(kill_cmd)

def test_fix_DEV_var_CPU_freq(dev_max_freq, cmd, bm_dict, csv_outfile, iteration, powermode, algo):
    """
    Fix GPU frequency and varies CPU freq
    When -c <cpu_number> is used, power measurement is performed to that CPU core over
    each available GPU freq against all availabe CPU freq.
    """

    if "-c " in cmd:
       # run just one CPU
       print("One CPU used")
       cpu_num = 'cpu{0}'.format(cmd[-1:])
       print("CPU number is :", cpu_num)
       #start_power_meter(csv_outfile, dev_max_freq, cpu_freq, cpu_num, POWER_MEASURE_PERIOD)
       for dev_freq in nfs.DEV_FREQ:
          nfs.setting_dev_max_frequency(dev_freq)
          nfs.getting_dev_frequency(nfs.DEV_MAX)
          dev_max_freq = dev_freq

          for cpu_freq in nfs.CPU_FREQ:
             nfs.setting_cpu_frequency(cpu_num, cpu_freq)
             nfs.getting_cpu_frequency(cpu_num)
             start_power_meter(csv_outfile, dev_max_freq, cpu_freq, cpu_num, POWER_MEASURE_PERIOD)
             try:
                rp.exe_command(bm_dict, csv_outfile, int(iteration), powermode)
             except ValueError:
                print("\n>>>> Please use command for usages : python run_parboil.py -h \n ")
                sys.exit(2)
             # print("\n> Test stop at {0} ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
             # clean up parboil folder by moving all csv files to project folder
             print("\nMoving csv file to project folder. Please check your result there...")
             print("> GPU max feq = ", dev_max_freq)
             print("> CPU feq = ", cpu_freq)
             rp.move_csvfile_to_project(powermode, dev_max_freq, cpu_num, cpu_freq)
             time.sleep(3)
             stop_power_meter()

             os.system("chmod a+r out_*")
             time.sleep(1)
             if not os.path.exists(POWER_FOLDER):
                os.makedirs(POWER_FOLDER)

             power_folder = POWER_FOLDER+"/"+algo
             print("Power folder : ", power_folder)
             rp.make_dir(power_folder)
             cwd = os.getcwd()

             source = os.listdir(cwd)
             for filename in source:
                if "_power_" in filename and algo in filename:
                   shutil.move(fullpath(cwd, filename), fullpath(power_folder, filename))

             print("----------------")

    else:
       #for each GPU fixed one frequency:
       for cpu_num in nfs.CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
          print("CPU number is :", cpu_num[-1:])
          nfs.setting_cpu_userspace(cpu_num)
          for cpu_freq in nfs.CPU_FREQ:
             nfs.setting_cpu_frequency(cpu_num, cpu_freq)
             nfs.getting_cpu_frequency(cpu_num)
             # Start power Meter 
             start_power_meter(csv_outfile, dev_max_freq, cpu_freq, cpu_num, POWER_MEASURE_PERIOD)
             # Execute workload 
             try:
                rp.exe_command(bm_dict, csv_outfile, int(iteration), powermode)
             except ValueError:
                print("\n>>>> Please use command for usages : python run_parboil.py -h \n ")
                sys.exit(2)
             # print("\n> Test stop at {0} ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
             # clean up parboil folder by moving all csv files to project folder
             print("\nMoving csv file to project folder. Please check your result there...")
             print("> GPU max feq = ", dev_max_freq)
             print("> CPU feq = ", cpu_freq)
             rp.move_csvfile_to_project(powermode, dev_max_freq, cpu_num, cpu_freq)
             time.sleep(3)
             stop_power_meter()
 
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
    #for cpu_num in nfs.CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
    #    print("cpu_num = ", cpu_num)
    (algo, dset, itrs, pmode, cpunum) = get_input_options(argv)
    if cpunum == '':
       command = 'python run_parboil.py -a {0} -d {1} -n {2} -p {3}'.format(algo, dset, itrs, pmode)
    else:
       command = 'python run_parboil.py -a {0} -d {1} -n {2} -p {3} -c {4}'.format(algo, dset, itrs, pmode, cpunum)
    print("command = ", command)

    csv_outfile = "out_"+algo+"_"+dset+".csv"
    #csv_outfile = algo+"_"+dset+".csv"
    bm_dict = rp.create_benchmark_dictionary(rp.COMMANDS_FILES)
    dev_max_freq = nfs.getting_dev_frequency(nfs.DEV_MAX)
    #print("GPU Max Freq: ", dev_max_freq)
    test_fix_DEV_var_CPU_freq(dev_max_freq, command, bm_dict, csv_outfile, int(itrs), pmode, algo)


if __name__ == "__main__":
   main(sys.argv[1:])
