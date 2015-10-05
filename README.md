##osprofiler

##Questions to consider

* What kind of information do we want to gather?
    * System
    * Process
    * MySQL
    * RabbitMQ
    * RabbitMQ Events

* Where do we want to send it?
    * ElasticSearch
    * Blueflood

##Design Description
The profilier will run as a daemon. The configured probes will collect sample every [x] seconds, and will push notifications out to an appropriate backend every [y] seconds.

