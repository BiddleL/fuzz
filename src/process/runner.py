import sys
from pwn import process

class Manager:
    
    def __init__(self, count):
        if "./"  != sys.argv[1][1:2]:
            self.process_name = f"./{sys.argv[1]}"
        else:
            self.process_name = f"./{sys.argv[1]}"
        self.stop_flag = False

    def in
 
    
    def run(self, inputStr):
        p = process(self.process_name)
        
        p.sendline(inputStr)
        p.shutdown()
        exit_code = p.poll(block = True)
        p.stderr.close()
        p.stdout.close()
        

        return exit_code
    
    def result(self, exit, input):
        if exit == 0:
            # No vulnerabilties
            print("No vuln")
        else:
            
            fp = open("bad_input.txt", "w+")
            fp.write(input)
            fp.close()


        
        