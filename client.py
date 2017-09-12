#!/usr/bin/env python
import os
import socket
import thread
import time
import traceback

from optparse import OptionParser

buffer_size = 2048

up_buffer_size = 1024 * 1024
down_buffer_size = 1024 * 1024

def main(options):
    print 'starting client'
    upload_test(options)
    download_test(options)

def upload_test(options):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((options.server,options.port))
    s_time = time.time()
    s.send('upload_test')
    pkt_cmd = s.recv(buffer_size)
    if pkt_cmd == 'recv_ok':
        e_time = time.time()
        latency = e_time - s_time
        print 'network latency: %f ms'%(latency*1000)
    else:
        raise Exception('handshake failed')
    s.send(str(up_buffer_size))
    pkt_cmd = s.recv(buffer_size)
    if pkt_cmd == 'recv_buffer_ok':
        pass
    else:
        raise Exception('buffer size exchange failed')
    pkt_data = bytearray('a'*up_buffer_size)
    s.send(pkt_data)
    time_up_diff = float(s.recv(buffer_size))
    print 'time required for upload was %f sec' % time_up_diff
    print 'bw was %f MBps' % (((up_buffer_size/1048567.0)/time_up_diff))
    s.close()


def download_test(options):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((options.server,options.port))
    s_time = time.time()
    s.send('download_test')
    pkt_cmd = s.recv(buffer_size)
    if pkt_cmd == 'recv_ok':
        e_time = time.time()
        latency = e_time - s_time
        print 'network latency: %f ms'%(latency*1000)
    else:
        raise Exception('handshake failed')
    s.send(str(down_buffer_size))
    pkt_cmd = s.recv(buffer_size)
    if pkt_cmd == 'recv_buffer_ok':
        pass
    else:
        raise Exception('buffer size exchange failed')

    rec_len = down_buffer_size
    time_up_start = time.time()
    while rec_len:
        pkt_data = s.recv(buffer_size)
        rec_len  -=len(pkt_data)
    time_up_stop = time.time()
    time_up_diff = time_up_stop - time_up_start
    print 'time required for download was %f sec' % time_up_diff
    print 'bw was %f MBps' % (((up_buffer_size/1048567.0)/time_up_diff))
    s.close()

    

if __name__ == '__main__':
    usage = "usage: %prog [options] \nuse ctl+c to abort"
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--port', type='int', dest='port', help='port address', default=9000)
    parser.add_option('-s', '--server', dest='server', help='server address', default='127.0.0.1')
    (options, args) = parser.parse_args()
    main(options)
