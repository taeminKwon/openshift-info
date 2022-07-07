#!/usr/bin/python
# -*- coding: utf-8 -*-
import json 
from ast import literal_eval
import subprocess
import shlex
import sys
from time import sleep

# 다음 자료에서 참고 하여 수정됨
# https://wikidocs.net/14350
# 사용법 : python checkTask.py [Namespace] > namespace.info

# 문자열 명령어 실행
def subprocess_open(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

def subprocess_open_stdout(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    
    return stdoutdata
    
def subprocess_open_stdout_list(command):
    #python subprocess output to an array
    #https://stackoverflow.com/questions/45193068/python-subprocess-output-to-an-array
    
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = popen.stdout.readlines()
    
    return result

# 출력 구분 문자 
def print_header(header_name):

    header_name = header_name
    space_num = 50
    
    print "=" * space_num
    print header_name
    print "=" * space_num
    
def print_header_sub(header_name):

    header_name = header_name
    space_num = 50
    
    print "-" * space_num
    print header_name
    print "-" * space_num

# namespace 기본 정보 
def check_namespace(namespace):

    print_header(namespace + " Info")

    print_header_sub( namespace + " name")
    command = "oc get namespace -o yaml " + namespace
    print subprocess_open_stdout(command)
    
    print_header_sub(namespace + " node-selector")
    command = "oc get namespace -o yaml " + namespace + "| grep node-selector"
    print subprocess_open_stdout(command)
    
    print_header_sub(namespace + " EgressIP")
    command = "oc get netnamespace " + namespace + " -o jsonpath='{.egressIPs}'"
    #command = "oc get netnamespace " + namespace + " -o jsonpath='{.egressIPs}{\"\\n\"}'"
    print subprocess_open_stdout(command)

    #egressIpJsonList = subprocess_open_stdout_list(command)
    #egressIpList = json.loads(egressIpJsonList)
    #
    #for egressIp in egressIpList:
    #    #개행 제거
    #    egressIp = egressIp.strip()
    #    
    #    print "Egress IP : " + egressIp
    #    command = "oc get hostsubnet " + "| grep " + egressIp
    #    print subprocess_open_stdout(command)
    
# namespace 할당된 resource 기본 정보 
def check_resources(namespace):

    namespace = namespace 

    print_header(namespace + " resources" )

    print_header_sub(namespace + " resourcequota")
    command = "oc get resourcequota -o yaml -n " + namespace
    print subprocess_open_stdout(command)
    
    print_header_sub(namespace + " limitrange")
    command = "oc get limitrange -o yaml -n " + namespace
    print subprocess_open_stdout(command)

    print_header_sub(namespace + " object")
    command = "oc get deployment,deploymentconfig,daemonset,statefulset,cronjob,buildconfig -n " + namespace
    print subprocess_open_stdout(command)

# workload 기준 각각 정보 확인 
def check_workload(namespace, workload, workload_type):

    namespace = namespace
    workload = workload
    workload_type = workload_type

    print_header(namespace + " " + workload + " " + workload_type)

    print_header_sub(workload + " resources")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 10 resources: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " strategy")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 10 strategy: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " readinessProbe")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 10 readinessProbe: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " livenessProbe")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 10 livenessProbe: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " replicas")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep replicas: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " node selector")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 2 -i node"
    print subprocess_open_stdout(command)

    print_header_sub(workload + " env")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 30 env: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " triggers")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 15 triggers: "

    print subprocess_open_stdout(command)

    print_header_sub("Pods Run")
    command = "oc get pods -n " + namespace + " | grep Run | grep " + workload
    print subprocess_open_stdout(command)

    return


# 동작중인 Pod 정보 확인 
def check_pod(namespace, workload):

    namespace = namespace
    workload = workload
    workload_type = "pod"

    print_header(namespace + " " + workload + " " + workload_type)

    print_header_sub("Pods Run")
    command = "oc get " + workload_type + " -n " + namespace + " | grep Run | grep " + workload + " | head -n 1 | awk '{print $1}'"

    pod_name=subprocess_open_stdout(command)

    # 개행 문자 제거
    #https://www.delftstack.com/ko/howto/python/python-remove-newline-from-string/
    pod_name=pod_name.strip()

    print_header_sub(pod_name + " process")

    # 변수 확인
    ## https://pytutorial.com/check-if-variable-is-not-null-in-python
    ## https://pytutorial.com/check-if-variable-is-empty-in-python

    if pod_name is not None and pod_name !="":

        pod_command = "oc exec -n " + namespace + " " + pod_name + " -- /bin/bash -c 'ps -eo pid,cmd > /tmp/ps.info'"
        print pod_command
        print subprocess_open_stdout(pod_command)

        pod_command = "oc exec -n " + namespace + " " + pod_name + " -- /bin/bash -c 'head -c 500 /tmp/ps.info'"
        print pod_command
        print subprocess_open_stdout(pod_command)

        pod_command = "oc exec -n " + namespace + " " + pod_name + " -- /bin/bash -c 'netstat -lntp'"
        print pod_command
        print subprocess_open_stdout(pod_command)
    else:
        print "Running Pod is not exist."

    return

# buildconfig 정보 확인 
def check_buildconfig(namespace, workload):

    namespace = namespace
    workload = workload
    workload_type = "buildconfig"

    print_header(namespace + " " + workload + " " + workload_type)

    print_header_sub(workload + " sourceStrategy and env")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 10 sourceStrategy: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " label")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 5 label: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " output")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 5 output: "
    print subprocess_open_stdout(command)

    print_header_sub(workload + " source")
    command = "oc get " + workload_type + " -o yaml -n " + namespace + " " + workload + "| grep -A 5 source: "
    print subprocess_open_stdout(command)

    return

# workerload 대상 list 정보 확인 
def check_workload_list(namespace, workload_type):

    namespace = namespace
    workload_type = workload_type

    print_header(namespace + " " + workload_type)

    command = "oc get " + workload_type + " -o wide -n " + namespace 
    print subprocess_open_stdout(command)

    return

# workerload 대상 list 정보 확인 
def check_rolebinding_user(namespace):

    namespace = namespace

    print_header(namespace + " User rolebinding Info")

    command = "oc get rolebinding -o wide -n " + namespace 
    print subprocess_open_stdout(command)

    return

def check_task(namespace):

    namespace = namespace

    # namespace
    check_namespace(namespace)
    check_resources(namespace)

    # deploymentconfig
    command = "oc get deploymentconfig -n " + namespace + " --no-headers | awk '{print $1}'"
    deploymentconfig_list=subprocess_open_stdout_list(command)
    
    for app in deploymentconfig_list:
        #개행 제거
        app = app.strip()
        
        check_workload(namespace, app, "deploymentconfig")
        check_pod(namespace,app)
        
        sleep(1)

    # buildconfig
    command = "oc get buildconfig -n " + namespace + " --no-headers | awk '{print $1}'"
    buildconfig_list=subprocess_open_stdout_list(command)
    
    for app in buildconfig_list:
        #개행 제거
        app = app.strip()
        
        check_buildconfig(namespace, app)
        
        sleep(1)

    # service
    check_workload_list(namespace, "service")

    # route 
    check_workload_list(namespace, "route")

    # persistentvolumeclaim 
    check_workload_list(namespace, "persistentvolumeclaim")

    # horizontalpodautoscaler
    check_workload_list(namespace, "horizontalpodautoscaler")

    # configmap
    check_workload_list(namespace, "configmap")
    print_header_sub( namespace + " configmap with deploymentconfig")
    command = "oc get deploymentconfig -n " + namespace + " -o yaml | grep -i configmap "
    print subprocess_open_stdout(command)

    # secret
    check_workload_list(namespace, "secret")
    print_header_sub( namespace + " secret with deploymentconfig")
    command = "oc get deploymentconfig -n " + namespace + " -o yaml | grep -i secret"
    print subprocess_open_stdout(command)

    # user
    check_rolebinding_user(namespace)

    return

def main():

    namespace = str(sys.argv[1])
    
    if namespace is not None:
        #check_namespace(namespace)
        check_task(namespace)
    else:
        print "Arguments is " + namespace

        
if __name__ == "__main__":
    main()
    
    
