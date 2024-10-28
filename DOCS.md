Omnidialer(OMD) is a dialer software meant to be a FLOSS component for Omnileads (OML) that can be used as a drop in alternative to Wombat dialer.

It is implemented in Python and use components such as Docker, docker-compose, Postgres, Redis and Gearman.

The use of Gearman allows to easily horizontal scale the system by adding Gearman workers dedicated to the most time & memory consuming resources.

The system is designed to run on every GNU/Linux system that supports bash, docker & docker-compose.

It can run in the same host OML is running or on an external host by configuring the environment variables present in the _env_ file.
The relevant environment variables are in this case: *REDIS_OML_SERVER*, *REDIS_OML_PORT*, *ASTERISK_APP*, *ASTERISK_USER*, *ASTERISK_PASS*, *ASTERISK_HOST*, *ASTERISK_PORT, *DIALER_ACD_HOST*, *POSTGRES_OML_PASSWORD*, *POSTGRES_OML_SERVER* and *POSTGRES_OML_PORT*.