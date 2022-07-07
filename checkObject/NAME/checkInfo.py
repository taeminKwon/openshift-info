#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import shlex
from time import sleep

# 다음 자료에서 참고 하여 수정됨
# https://wikidocs.net/14350
# 사용법 : python checkInfo.py > namespace.info

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

# 배치 파일 등 실행
def subprocess_open_when_shell_false(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

# 문자열 명령어 실행
# shell 변수를 false 로 줄경우(default가 false) 명령어를 shelx.split() 함수로 프로세스가 인식 가능하게 잘라 주어야 함
def subprocess_open_when_shell_false_with_shelx(command):
    popen = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

# 커맨드 리스트 처리
# 커맨드 리스트를 이전 처리의 결과(stdout)를 다음 처리의 입력(stdin)으로 입력하여 순차적으로 처리
def subprocess_pipe(cmd_list):
    prev_stdin = None
    last_p = None

    for str_cmd in cmd_list:
        cmd = str_cmd.split()
        last_p = subprocess.Popen(cmd, stdin=prev_stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prev_stdin = last_p.stdout

    (stdoutdata, stderrdata) = last_p.communicate()
    return stdoutdata, stderrdata

def check_deploymentconfig(namespace, deploymentconfig):

    namespace = namespace
    deploymentconfig = deploymentconfig
    
    print "=============================="
    
    print deploymentconfig + " resources"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 10 resources: "
    print subprocess_open_stdout(command)
    
    print deploymentconfig + " strategy"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 10 strategy: "
    print subprocess_open_stdout(command)
    
    print deploymentconfig + " readinessProbe"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 10 readinessProbe: "
    print subprocess_open_stdout(command)
    
    print deploymentconfig + " livenessProbe"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 10 livenessProbe: "
    print subprocess_open_stdout(command)
    
    print deploymentconfig + " env"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 30 env: "
    print subprocess_open_stdout(command)
    
    print deploymentconfig + " env"
    command = "oc get deploymentconfig -o yaml -n " + namespace + " " + deploymentconfig + "| grep -A 30 env: "
    print subprocess_open_stdout(command)
    
    print "Pods Run"
    command = "oc get pods -n " + namespace + " | grep Run | grep " + deploymentconfig
    print subprocess_open_stdout(command)
    
    print "=============================="
    
    return

def check_pod(namespace, deploymentconfig):
    print "Pods Run"
    command = "oc get pods -n " + namespace + " | grep Run | grep " + deploymentconfig + " | head -n 1 | awk '{print $1}'"
    
    pod_name=subprocess_open_stdout(command)

    # 개행 문자 제거
    #https://www.delftstack.com/ko/howto/python/python-remove-newline-from-string/
    pod_name=pod_name.strip()
        
    print pod_name + " process"
    
    # 변수 Null 확인
    # https://appia.tistory.com/417
    if pod_name is not None:
        
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
        print "No Pod"
        
    print "=============================="

def main():

    #check_deploymentconfig("Namespace", "DeploymentConfig")
    #check_pod("Namespace", "DeploymentConfig")
    
    namespace = "default"
    
    command = "oc get deploymentconfig -n " + namespace + " --no-headers | awk '{print $1}'"
    deploymentconfig_list=subprocess_open_stdout_list(command)
    
    #for app in deploymentconfig_list:
    #    print app
    
    for app in deploymentconfig_list:
        #개행 제거
        app = app.strip()
        
        check_deploymentconfig(namespace,app)
        check_pod(namespace,app)
        
        sleep(1)
        
if __name__ == "__main__":
    main()
    
    
