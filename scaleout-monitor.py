import os
import datetime
import time
import copy

WORK_DIR="/tmp/health/"
SCRIPT_DIR="/tmp/health/scripts/"
AGING=60
START_INIT=True


#################################################3
#Functios
#################################################3

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def search(list, key, value):
    return [element for element in list if element[key] == value]

def search_temp(list, key, value):
    for item in list:
#        print item, item[key]
        if item[key] == value:
           return item, list.index(item)

def read_files(list):
    nodes=[]
    for NAME in list:
      SO_NODES={}

      FILE=os.path.join(WORK_DIR, NAME)
      SO_NODES["container"]=NAME
      SO_NODES["name"]=FILE
      SO_NODES["id"]=int(NAME.lstrip('thunder-'))+1
      SO_NODES["ip"] = ""

      while SO_NODES["ip"] == "":
        with open(FILE, 'rt') as inputs:
          SO_NODES["ip"]=inputs.readline().strip()
      inputs.close()

      modification_time = modification_date(FILE)
      current_time = datetime.datetime.now()
      diff_date = (current_time - modification_time)
      SO_NODES["age"]=diff_date.seconds

      nodes.append(SO_NODES)

    return nodes

def Diff_list(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

def Diff(li1, li2):
    for li in li1:
      li.pop("age")
    for li in li2:
      li.pop("age")
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

#################################################3

if __name__ == "__main__":

  FILE_LIST = [x for x in os.listdir(WORK_DIR) if x.startswith("thunder-")]
  LIST_NODES=read_files(FILE_LIST)
  if START_INIT:
    OLD_LIST_NODES=LIST_NODES
  else:
    OLD_LIST_NODES=[]

  for Z in range(1, 3600):

    FILE_LIST = [x for x in os.listdir(WORK_DIR) if x.startswith("thunder-")]
    LIST_NODES=read_files(FILE_LIST)

##################################################
#Delete stale ID from active nodes

    for node in OLD_LIST_NODES:
      if node['age'] > AGING:
        print "Node ", node['container'], " has been scaled-in and is removing from the A10 Scaleout configuration...."
        (item,i)=search_temp(LIST_NODES, "container", node['container'])
#        print "index ", i
        LIST_NODES.pop(i)
        for active_node in LIST_NODES:
          print('removing ' + str(node['container']) + ' from ' +active_node['container'] + '.......')
#          print SCRIPT_DIR + '/config_del.py -d ' , active_node['ip'] , ' -i ' , node['id'] , ' -a ' , node["ip"]
#          print 'rm -rf ' + str(node["name"])
          os.system('python ' + SCRIPT_DIR + '/config_del.py -d ' + str(active_node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
          os.system('rm -rf ' + str(node["name"]))
##################################################

##################################################
#check if a new nodes is active
    if len(LIST_NODES)>len(OLD_LIST_NODES):
       print "Found a new node in K8s cluster "
       copy_LIST_NODES = copy.deepcopy(LIST_NODES)
       copy_OLD_LIST_NODES = copy.deepcopy(OLD_LIST_NODES)
       NEW_NODES=Diff(copy_LIST_NODES, copy_OLD_LIST_NODES)
       print "new node to add:"
       print NEW_NODES
       for node in NEW_NODES:
#         print('python ' + SCRIPT_DIR + '/config_init.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
#         print('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
         print('Initialising the  A10 Scaleout configration for new node ' + str(node['container']) + ' ...')
         os.system('python ' + SCRIPT_DIR + '/config_init.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
         os.system('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
         for old_node in OLD_LIST_NODES:
           print('adding A10 Scaleout configration into the new node ' + str(node['container']) + ' the address of existinig node ' + str(old_node['container'])+ ' ...')
#           print('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(node['ip']) + ' -i ' + str(old_node['id']) + ' -a ' + str(old_node["ip"]))
#           print('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(old_node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
           os.system('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(node['ip']) + ' -i ' + str(old_node['id']) + ' -a ' + str(old_node["ip"]))

           print('adding A10 Scaleout configration for new node ' + str(node['container']) + ' into exiting nodes ' + str(old_node['container']) + ' ...')
           os.system('python ' + SCRIPT_DIR + '/config_add.py -d ' + str(old_node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))

#         print('python ' + SCRIPT_DIR + '/config_init_enable.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))
         os.system('python ' + SCRIPT_DIR + '/config_init_enable.py -d ' + str(node['ip']) + ' -i ' + str(node['id']) + ' -a ' + str(node["ip"]))

    OLD_LIST_NODES=copy.deepcopy(LIST_NODES)

#    for node in LIST_NODES:
#      for p,v in node.items():
#        print p,v
    print "List of active containers...."
    for node in LIST_NODES:
      print node['container'], node['ip']

    print "***************"

    time.sleep(15)
