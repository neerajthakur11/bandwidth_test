#!/usr/bin/env python
import os
import socket
import thread
import time
import traceback

from optparse import OptionParser

buffer_size = 2048

def main(options):
    #using TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.bind((options.bind,options.port)) 
        s.listen(5)
        print 'server started at port %i'%options.port
    except Exception as e:
        print 'error starting server: %s'%str(e)
        os._exit(e.errno)

    while 1: 
        try:
            client, address = s.accept() 
            print 'received connection from : %s' % str(address)
            thread.start_new_thread(handle_request, (client, address))
        except Exception as e:
            print 'Exception at accept: %s'%str(e)

def handle_request(client, address):
    try:
        pkt_cmd = client.recv(buffer_size) 
        print 'recv: %s' %  pkt_cmd
        if pkt_cmd: 
            client.send('recv_ok')
            if pkt_cmd == 'upload_test':
                data_buffer_size = long(client.recv(buffer_size))
                print 'using buffer: %i Kb'%(data_buffer_size/1024)
                client.send('recv_buffer_ok')
                rec_len = data_buffer_size
                time_up_start = time.time()
                while rec_len:
                    pkt_data = client.recv(buffer_size)
                    rec_len  -=len(pkt_data)
                time_up_stop = time.time()
                time_up_diff = time_up_stop - time_up_start
                client.send(str(time_up_diff))
                print 'total time req for %i Kb for upload is %f sec'%(data_buffer_size/1024, time_up_diff)
                print 'upload bandwidth for %s is %f Mbps'%(address, (data_buffer_size/time_up_diff)/(1024*1024))
            elif pkt_cmd == 'download_test':
                data_buffer_size = long(client.recv(buffer_size)) 
                print 'using buffer: %i Kb'%(data_buffer_size/1024)
                client.send('recv_buffer_ok')
                pkt_data = bytearray('a'*data_buffer_size)
                client.send(pkt_data)
                pkt_cmd = client.recv(buffer_size)
                if pkt_cmd == 'finish_download':
                    print 'download test finished'
            else:
                raise Exception('invalid command received')
    except Exception as e:
        print 'got exception: %s'%str(e)
        traceback.print_exc()

if __name__ == '__main__':
    usage = "usage: %prog [options] \nuse ctl+c to abort"
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--port', type='int', dest='port', help='port address', default=9000)
    parser.add_option('-b', '--bind', dest='bind', help='IP address to bind', default='')
    (options, args) = parser.parse_args()
    main(options)
