# cloud_infrastructure_profiler(CIP)


##Questions to consider

* What kind of information do we want to gather?

* Where do we want to send it?

* How do we configure it?

* What tools are we going to use to gather this information?


##Design Description
The profilier will run as a daemon that will push notifications out to a backend every [x] seconds, where x is configurable through the configuration files.

###Gathering information on system resources
CIP will gather information using a python library or maybe some other tool. This is still under consideration. Options so far are:
  * OProfile - use python exec to gather output
  * psutils - python library for gathering info on system resources and process information.

####CPU utilization overrall and per process

####Memory utilization overall and per process

####Number of connections open overall and per process

####Network I/O stats system wide