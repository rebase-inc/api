from time import sleep

def run():
    fifo = open('/tmp/db', 'r')
    print(fifo.read())

if __name__ == '__main__':
    run()
