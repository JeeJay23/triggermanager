import socket, sys, threading, struct
from triggers import trigger_t
from time import sleep
from threading import Thread

# opcodes
OP_START    = 0x1
OP_STOP     = 0x2
OP_EXIT     = 0x3
OP_GET      = 0x4
OP_SET      = 0x5
OP_TSET     = 0x6
OP_TSTART   = 0x7
OP_TSTOP    = 0x8
OP_FD       = 0x9
OP_TCLEAR   = 0xa

# trigger activation msg code
TR_A = 0xa

CONF_PORT   = 8081
BUF_SIZE    = 32

callbacks   = {}
sock        = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
cb_i = 0

class Receiver (Thread):
    def __init__ (self, sock):
        Thread.__init__(self)
        self._stop = 0
        self._tr_cb = lambda a: "trigger callback not bound"
        self.events = []
        self.sock = sock

        self.frame = 0
        self.focus = 0
        self.iris  = 0
        self.zoom  = 0
    
    def run (self):
        while (not self.stop == 1):
            if (not self.sock._closed):
                data = self.sock.recv (1) # read packet length
            else:
                return

            if (len (data) == 0):
                break
            _len = data[0] - 1
            data = self.sock.recv (_len) # read rest of packet

            if (data[0] == TR_A): # trigger fire message
                tr_id = (data[1] << 8) | data[2]
                self._tr_cb (tr_id)
            elif (data[0] == OP_GET):
                self.frame = (data[1] << 8) | data [2]
                self.focus = (data[3] << 8) | data [4]
                self.iris  = (data[5] << 8) | data [6]
                self.zoom  = (data[7] << 8) | data [8]
            else:
                opc = data[0]
                add = data[1:]
                e = (opc, add)
                self.events.append (e)

    def pop (self):
        if (len (self.events) != 0):
            return self.events.pop (len (self.events) - 1)
        else:
            return

    def stop (self):
        self._stop = 1

    # blocks until an event is added to list
    def wait_for_event (self):
        while (len (self.events) == 0):
            sleep (.1)
    
    def register_tr_cb (self, func = None):
        if (func):
            self._tr_cb = func

thr = Receiver (sock)

def construct_packet (opc, **kwargs):
    packstr = ">B B "
    plen = 2
    vals = [plen, opc]

    if 'cat_set' in kwargs:
        slen = len(kwargs['cat_set'])
        plen += slen
        packstr += (str (slen) + "s ")
        vals.append (kwargs['cat_set'].encode())

    if 'tr_id' in kwargs:
        if not 'tr_afr' in kwargs:
            print ("conman: incomplete arguments. tr_afr missing")
            return
        plen += 4       
        packstr += "H H "
        vals.append (kwargs['tr_id'])
        vals.append (kwargs['tr_afr'])

    vals[0] = plen
    packer = struct.Struct (packstr)
    data = packer.pack (*vals)
    return data

def send_opc (opc):
    print ('sending opc: %s' % str(opc))
    data = construct_packet (opc)
    try:
        sock.send (data)
    except BrokenPipeError:
        print ("conman: socket broken")

def connect (addr):
    global sock, thr
    try:
        sock.connect   ((addr, CONF_PORT))
    except OSError:
        print ('conman: socket already connected')
    else:
        thr.start ()

# sends all triggers
def send_trigger (triggers):
    global sock
    send_opc (OP_TCLEAR)
    for t in triggers:
        data = construct_packet (OP_TSET, tr_id=t.id, tr_afr=t.activation_frame)
        sock.send (data)
        sleep (.1)

def bind_id (id, callback = None):
    global callbacks
    if callback:
        callbacks[id] = callback

def on_fire_trigger (tr_id):
    global callbacks
    if tr_id in callbacks:
        print ('on_fire_trigger: trigger %i fired' % tr_id)
        callbacks[tr_id] (tr_id)
    else:
        print ('on_fire_trigger: key %i not bound to a callback' % tr_id)