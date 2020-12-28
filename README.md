# a10-kubernetes-scaleout
Set of files which helps to integrate A10 Scaleout function into Kubernetes. When K8s action scale up oe down A10 CGN container, the process will automatically update  ACOS configuration and appropriatly add or remove container IP address.
Currently the envinroment is running using NFS share mount point where python scripts and runtaime fiels are located. in the future version more "k8s" approach will be used. scipts will be integrated into  container.


1. set of python scripts should be place on a NFS share mount point: config_add.py, config_del.py, config_init.py config_init_enable.py
2. create PV and PVC which points to that NFS mount point using the manifest pv-pvc.yml
3. create a sidecar container using centos-health-1.yml manifest. it is monitoring the runtime infomration, created each ACOS container and is able to detect if a ACOS container has been created  or deleted. The scripts are running from the NFS share mount point
4. create Statefull set for A!0 CGN containers using cthunder_statefull_scale.yml manifest. Each A10 container will place and update a runtime file on the NFS mount point, which is read by sidecar container

eachtime a command "kubectl scale" is executed creating or deleting A10 container in that Statefull set, the sidecar will update the configuration on all running and active A10 container accordingly to keep CGN Scaleout  configuration consistent and updated.
