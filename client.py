from time import sleep

def run():
    fifo = open('/tmp/db', 'r')
    print(fifo.readline())
    fifo.close()
    print('sleeping 5 s')
    sleep(5)

if __name__ == '__main__':
    run()
