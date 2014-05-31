# err-nagios

Interfaces [errbot](https://github.com/gbin/err) with
[Nagios](http://www.nagios.org/).


## Installation

```
!repos install https://github.com/jwm/err-nagios.git
```


## Commands

* !nagios ack HOST REASON
  Acknowledges a Nagios alert for HOST.

* !nagios ack HOST:SERVICE REASON
  Acknowledges a Nagios alert for SERVICE on HOST.

* !nagios recheck HOST:SERVICE
  Forces an immediate recheck of SERVICE on HOST.
