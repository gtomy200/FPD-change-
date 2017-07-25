from netmiko import ConnectHandler
from textfsm import *
import threading
import os
import datetime


def control(count, records):
    while count <= records:
        if router_info[count][1] == 'cisco':
            device_name = 'cisco_ios'
        else:
            count += 1
            continue
        device = {'device_type': device_name, 'ip': router_info[count][0], 'username': u_name, 'password': pwd}
        try:
            net_connect = ConnectHandler(**device)
        except:
            print ('Connection refused to ' + router_info[count][0])
            count += 1
            continue
#check if the router is core or provider edge router, router that starts with 'c' means core router which are cisco NCS series     
        if device_name == 'cisco_ios' and router_info[count][0][0].lower() == 'c':
            try:
                cmd_output = net_connect.send_command("show hw-module fpd | exclude CURRENT")
                output = file_operation_core(cmd_output)
                file_generation(output, router_info[count][0], 'c')
            except:
                print ('Command cant be executed on ' + router_info[count][0])

                count += 1
                continue
#check if the router is core or provider edge router, router that starts with 'p' means provider edge router which are cisco ASR series                 
        elif device_name == 'cisco_ios' and router_info[count][0][0].lower() == 'p':
            try:
                cmd_output = net_connect.send_command("show hw-module fpd location all | e CURRENT")
                output = file_operation_pe(cmd_output)
                file_generation(output, router_info[count][0], 'p')
            except:
                print ('Command cant be executed ' + router_info[count][0])
                count += 1
                continue
        count += 1


def router_list():
    fo = open("test.txt", 'r')
    temp_list = []
    str = fo.readline()
    while str:
        temp_list += re.findall("(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", str)
        str = fo.readline()
    fo.close()
    length = len(temp_list)
    return (temp_list, length)


def file_operation_core(data_parsing):
    re_table = TextFSM(open('hw_mod_fpa', 'r'))
    data = re_table.ParseText(data_parsing)
    temp_element = []
    for row in data:
        temp_element.append(row)
    return (temp_element)


def file_operation_pe(data_parsing):
    re_table = TextFSM(open('hw_mod_fpa_pe', 'r'))
    data = re_table.ParseText(data_parsing)
    temp_element = []
    for row in data:
        temp_element.append(row)
    return(temp_element)


def file_generation(output, router_name, router_type):
    os.chdir(string_current_date_time)
    filename = router_name+'.txt'
    fo = open(filename, 'w')
    rec_count = 0
    if router_type == 'c':
        fo.write('Location'+'\t\t'+'Card type'+'\t\t'+'FPD device'+'\t\t\t'+'Status'+'\n')
        for records in output:
            if records[-1].lower() == 'need upgd':
                fo.write(records[0]+'\t\t\t')
                fo.write(records[1]+'\t\t')
                fo.write(records[2]+'\t\t\t')
                fo.write(records[3]+'\n')
                rec_count += 1
            else:
                pass

    else:
         fo.write('Location'+'\t\t'+'Card_type'+'\t\t'+'Hw'+'\t\t'+'Type'+'\t\t\t'+'Subtype'+'\t\t\t'+'Inst'+'\t\t\t'+'Status'+'\n')
         for records in output:
            if records[-1].lower() == 'yes':
                fo.write(records[0]+'\t\t')
                fo.write(records[1]+'\t\t')
                fo.write(records[2]+'\t\t')
                fo.write(records[3]+'\t\t\t')
                fo.write(records[4]+'\t\t\t')
                fo.write(records[5]+'\t\t\t')
                fo.write(records[6]+'\n')
                rec_count += 1
            else:
                pass
    fo.flush()
    fo.close()
    if rec_count == 0:
        os.remove(filename)
    else:
        pass
    os.chdir("..")
    return()
router_info, records = router_list()
current_date_time = datetime.datetime.now()
string_current_date_time = str(current_date_time.year)+'_'+str(current_date_time.month)+'_'+str(current_date_time.day)+'_sh_hw_fpd'
try:
    os.makedirs(string_current_date_time)
except:
    pass
u_name = input('Enter the user name: ')
while u_name == '':
    print ('Enter a valid username')
    u_name = input("Enter the username: ")
pwd = input("Enter the password: ")
while pwd == '':
    print ('Enter a valid password')
    pwd = input("Enter the password: ")
threadcount = int(round(records**(0.5), 0))
no_of_elements = int(round(records/threadcount))
thread_call = 0
start_index = 0
end_index = no_of_elements - 1
obj = [None]*threadcount
while thread_call < threadcount:
    obj[thread_call] = threading.Thread(target=control, args=(start_index, end_index,), daemon=True)
    thread_call += 1
    start_index = end_index + 1
    if thread_call + 1 == threadcount:
        end_index = records-1
    else:
        end_index = start_index + no_of_elements - 1
thread_call = 0
while thread_call < threadcount:
    obj[thread_call].start()
    thread_call += 1
