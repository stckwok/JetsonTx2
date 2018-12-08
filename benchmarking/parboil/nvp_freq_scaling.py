import os
import time

# CPU and GPU frequency scaling to get power measurements for different workloads
# https://elinux.org/Jetson/Performance

# Warning : All the commands on this page must be executed as root

CPU0 = "cpu0"
CPU1 = "cpu1"
CPU2 = "cpu2"
CPU3 = "cpu3"
CPU4 = "cpu4"
CPU5 = "cpu5"
#CPU_LIST = [CPU0, CPU1, CPU2, CPU3, CPU4, CPU5]
CPU_LIST = [CPU0]
CPU_LIST4 = [CPU4]
CPU_LIST5 = [CPU5]

NV_POWER_MODE = ["0", "1", "2", "3", "4"]

# CPU avaliable frequencies for scaling
# cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies
CPU_FREQ = [345600, 499200, 652800, 806400, 960000, 1113600, 1267200, 1420800, 1574400, 1728000, 1881600, 2035200]

# GPU DEV avaliable frequencies for scaling
# cat /sys/devices/17000000.gp10b/devfreq/17000000.gp10b/available_frequencies
DEV_FREQ = [140250000, 229500000, 318750000, 408000000, 497250000, 586500000, 675750000, 765000000, 854250000, 943500000, 1032750000, 1122000000, 1211250000, 1300500000]

DEV_MIN = "min_freq"
DEV_CUR = "cur_freq"
DEV_MAX = "max_freq"
DEV_FREQ_MODE = [DEV_MIN, DEV_CUR, DEV_MAX]

def get_list_cpu_freq():
    print("CPU available freq = ", CPU_FREQ)

def viewing_cpu_status(cpu):
    command = 'cat /sys/devices/system/cpu/online'
    os.system(command)
    time.sleep(1)

def setting_dev_max_frequency(freq):
    """
    """
    cmd = 'echo {0} > /sys/devices/17000000.gp10b/devfreq/17000000.gp10b/max_freq'.format(freq)
    os.system(cmd)
    print("Finished setting GPU device max frequency : {0}".format(freq))

def getting_dev_frequency(freq_mode):
    command3 = 'cat /sys/devices/17000000.gp10b/devfreq/17000000.gp10b/{0}'.format(freq_mode)
    output = os.system(command3 + " > gpu_freq.txt")
    time.sleep(1)
    last = "0"
    if not output:
       f = open("gpu_freq.txt", "r")
       lines = f.read().splitlines()
       last = lines[-1]
       f.close()
    #print("frequency is : ", last)
    os.remove("gpu_freq.txt")
    return last

def set_cpu_frequency_cmd(cpu, freq):
    """
    """
    cmd = 'sudo echo {0} > /sys/devices/system/cpu/{1}/cpufreq/scaling_setspeed'.format(freq, cpu)
    return cmd

def get_cpu_frequency_cmd(cpu):
    """
    """
    cmd = 'cat /sys/devices/system/cpu/{0}/cpufreq/scaling_cur_freq'.format(cpu)
    return cmd
 
def setting_cpu_userspace(cpu):
    """
    """
    cmd = 'echo "userspace" > /sys/devices/system/cpu/{0}/cpufreq/scaling_governor'.format(cpu)
    os.system(cmd)
    print("Finished setting userspace for CPU : {0}".format(cpu))

def setting_cpu_frequency(cpu, freq):
    command1 = set_cpu_frequency_cmd(cpu, freq)
    os.system(command1)
    print("just set, check your freq now...") 
    time.sleep(1)

def getting_cpu_frequency(cpu):
    command2 = get_cpu_frequency_cmd(cpu)
    #os.system(command2)
    #time.sleep(1)
    output = os.system(command2 + " > cpu_freq.txt")
    time.sleep(1)
    last = "0"
    if not output:
       f = open("cpu_freq.txt", "r")
       lines = f.read().splitlines()
       last = lines[-1]
       f.close()
    print("frequency is : ", last)
    os.remove("cpu_freq.txt")
    return last

    
def turning_cpu_cores_onoff():
    pass

def test_fix_DEV_var_CPU5_freq():
    #for each GPU fixed one frequency:
    for cpu_num in CPU_LIST5:  # [CPU0, CPU1, CPU2, CPU3]
       setting_cpu_userspace(cpu_num)
       for cpu_freq in CPU_FREQ:
          setting_cpu_frequency(cpu_num, cpu_freq)
          #getting_cpu_frequency(cpu_num)
          getting_cpu_frequency("cpu0")
          getting_cpu_frequency("cpu1")
          getting_cpu_frequency("cpu2")
          getting_cpu_frequency("cpu3")
          getting_cpu_frequency("cpu4")
          getting_cpu_frequency("cpu5")

def test_fix_DEV_var_CPU_freq():
    #for each GPU fixed one frequency:
    for cpu_num in CPU_LIST:  # [CPU0, CPU1, CPU2, CPU3]
       setting_cpu_userspace(cpu_num)
       for cpu_freq in CPU_FREQ:
          setting_cpu_frequency(cpu_num, cpu_freq)
          getting_cpu_frequency(cpu_num)
          # Start power Meter 
          # Execute workload 
 
def test_fix_CPU_var_DEV_freq():
    for dev_freq in DEV_FREQ:
       setting_dev_max_frequency(dev_freq)
       getting_dev_frequency(DEV_MAX)
       # Start power Meter 
       # wait 5 seconds
       # Execute workload 


def main():
    print("----------------")
    test_fix_DEV_var_CPU5_freq()
    #test_fix_DEV_var_CPU_freq()
    #test_fix_CPU_var_DEV_freq()

    print("----------------")


if __name__ == "__main__":
   main()

