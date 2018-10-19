#!/bin/pythin

# VDA model

import threading
import time
from enum import Enum
import random
import Queue

class Windows (threading.Thread):
   DC = 0  #disconnected
   C = 1   # connected
   
   def __init__(self, eevent, vdaconnection):
      threading.Thread.__init__(self)
      self.users = [self.DC,self.DC,self.DC, self.DC, self.DC]
      self.exit_event = eevent
      self.connection = vdaconnection

   def run(self):
      print "WIN: starting"
      while self.exit_event.is_set():
          delay = random.randint(1,10)
          user_id = random.randint(0,4)
          user = "user{}".format(user_id)
          time.sleep(delay)
          if self.users[user_id] == self.DC:
              print "WIN: {} logging in".format(user)
              self.users[user_id] = self.C
              self.connection.put(("login", user))
          else:
              print "WIN: {} logging out".format(user)
              self.users[user_id] = self.C
              self.connection.put(("logout", user))
      print "WIN: stopping"

class Ise (threading.Thread):
    def __init__(self, eevent, from_vda, to_vda):
        threading.Thread.__init__(self)
        self.exit_event = eevent
        self.to_vda = to_vda
        self.from_vda = from_vda

    def run(self):
       print "ISE: starting"
       while self.exit_event.is_set():
           time.sleep(0.1)
           if not self.from_vda.empty():
               ignore = random.choice([True,False])
               #ignore = False
               msg, user = self.from_vda.get();
               if msg == "auth_req":
                   print "ISE received: {} for user: {}, response sending {} ignored".format(msg, user, "will be" if ignore else "will not be")
                   if not ignore:
                       rsp = "auth_resp"
                       print "ISE sending: {} for user: {}".format(rsp, user)
                       self.to_vda.put((rsp, user))
               elif msg == "acc_start_req":
                   print "ISE received: {} for user: {}, response sending {} ignored".format(msg, user, "will be" if ignore else "will not be")
                   if not ignore:
                       rsp = "acc_start_resp"
                       print "ISE sending: {} for user: {}".format(rsp, user)
                       self.to_vda.put((rsp, user))
               elif msg == "acc_stop_req":
                   print "ISE received: {} for user: {}, response sending {} ignored".format(msg, user, "will be" if ignore else "will not be")
                   if not ignore:
                       rsp = "acc_stop_resp"
                       print "ISE sending: {} for user: {}".format(rsp, user)
                       self.to_vda.put((rsp, user))
               else:
                   print "ISE: unknow message received: {} for user: {}".format(msg, user)
       print "ISE: stopping"


class RDP_Session:
     def __init__(self, user_name):
         self.user_name = user_name
         self.state = "user_logged_out"
         self.timer = None


class VDA(threading.Thread):

    def __init__(self, eevent, from_win, from_ise, to_ise, from_timer):
        threading.Thread.__init__(self)
        self.exit_event = eevent
        self.to_ise = to_ise
        self.from_ise = from_ise
        self.from_win = from_win
        self.from_timer = from_timer
        self.rdp_sessions = { "user0": RDP_Session("user0"), "user1": RDP_Session("user1"), "user2" : RDP_Session("user2"), "user3": RDP_Session("user3"), "user4":  RDP_Session("user4")}

    def run(self):
       print "VDA: starting"
       while self.exit_event.is_set():
           time.sleep(0.1)
           if not self.from_win.empty():
               msg, user = self.from_win.get();
               print "VDA received: {} for user: {}".format(msg, user)
               session = self.rdp_sessions[user]
               if msg == "login":
                   req = "auth_req"
                   print "VDA: sending {} for user {}".format(req, user)
                   self.to_ise.put((req, session.user_name))
                   session.state = "auth_pending"
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               elif msg == "logout":
                   req = "acc_stop_req"
                   print "VDA: sending {} for user {}".format(req,user)
                   self.to_ise.put((req, user))
                   session.state = "acc_stop_pending"
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               else:
                   print "VDA: unknow message received: {} for user: {} from WIN".format(msg, user)
           if not self.from_ise.empty():
               msg, user = self.from_ise.get();
               print "VDA received: {} for user: {}".format(msg, user)
               session = self.rdp_sessions[user]
               if msg == "auth_resp":
                   req = "acc_start_req"
                   print "VDA: sending {} for user {}".format(req, user)
                   self.to_ise.put((req, session.user_name))
                   session.state = "acc_start_pending"
                   session.timer.cancel()   # stop timer for authentication pending
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               elif msg == "acc_start_resp":
                   session.state = "user_authenticated"
                   session.timer.cancel()
               elif msg == "acc_stop_resp":
                   session.state = "user_logged_out"
                   session.timer.cancel()
               else:
                   print "VDA: unknow message received: {} for user: {} from ISE".format(msg, user)
           if not self.from_timer.empty():
               user = self.from_timer.get();
               print "VDA received timer event for user: {}".format(user)
               session = self.rdp_sessions[user]
               if session.state == "auth_pending":
                   req = "auth_req"
                   print "VDA: RESENDING {} for user {}".format(req, user)
                   self.to_ise.put((req, session.user_name))
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               elif session.state == "acc_start_pending":
                   req = "acc_start_req"
                   print "VDA: RESENDING {} for user {}".format(req, user)
                   self.to_ise.put((req, session.user_name))
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               elif session.state == "acc_stop_pending":
                   req = "acc_stop_req"
                   print "VDA: RESENDING {} for user {}".format(req, user)
                   self.to_ise.put((req, session.user_name))
                   session.timer = threading.Timer(3.0, timer_handler, args=[user])
                   session.timer.start()
               else:
                   print "VDA: unknow rdp session state: {}".format(session.state)

       for key,session in self.rdp_sessions.iteritems():
           if session.timer is not None:
               session.timer.cancel()
          
       print "VDA: stopping"


def timer_handler(user):
    print "TIMER: Timer expired for {}".format(user)
    timer_to_vda.put(user)
    
timer_to_vda = Queue.Queue()

def main():

    windows_to_vda = Queue.Queue()
    vda_to_ise = Queue.Queue()
    ise_to_vda = Queue.Queue()
    eevent = threading.Event()
    eevent.set()
    win = Windows(eevent, windows_to_vda)
    win.start()
    ise = Ise(eevent, vda_to_ise, ise_to_vda)
    ise.start()
    vda = VDA(eevent, windows_to_vda, ise_to_vda, vda_to_ise, timer_to_vda)
    vda.start()


    # FIXME Make proper arguments
    try:
        while True:
            time.sleep(1)
            #print "main loop"
    except KeyboardInterrupt:
        print "Stopping ....."

    print "exit set"
    eevent.clear()
    print "waiting threads"
    win.join()
    ise.join()


if __name__ == "__main__":
     main()

