import subprocess
import time

if __name__ == "__main__":
    commands = ["python main.py 1 producer"]
        #          ,"python main.py 2 producer","python main.py 3 producer",
        #         "python main.py 4 producer","python main.py 5 producer","python main.py 6 producer",
        #         "python main.py 7 producer","python main.py 8 producer"]
    #
    #commands = ["python main.py 1 producer"]
    processList=[]
    for cmd in commands:
        process = subprocess.Popen(cmd)
        print(process.args)
        processList.append(process)

    while True:
        time.sleep(2)
        for proc in processList:
            if proc.poll() is not None:
                processList.remove(proc)
                process = subprocess.Popen( proc.args)
                processList.append(process)





