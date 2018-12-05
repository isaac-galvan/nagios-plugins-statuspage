# nagios-plugins-statuspage

## Overview

This package contains Nagios plugins for getting status of components on a page hosted by Statuspage.io

## Installation

Install dependancies from `requirements.txt` and place the plugins where they can be executed by the Nagios user.

## Plugins

### check-statuspage-components

This plugin reads the status of a component on a Statuspage.io page and returns status to Nagios.

Inspect the JSON of your Statuspage to get the page id for your page and the id of any components you'd like to monitor.
The components JSON file is typically at `https://status.example.com/api/v2/components.json`

You can define custom variable macros in the Nagios configuration files to associate your page with a host and the component with services.

Define a host with the _PAGEID variable macro:
```
define host {
    host_name        status.example.com
    _PAGEID          208q92hckwws
}
```

Define a service with the command and _COMPONENTID variable macro:
```
define service {
    host_name                status.example.com
    service_description      Service Name
    _COMPONENTID             lp2y8210101z
    check_command            check_statuspage_component
}
```

Define a command object in your Nagios configuration which references the custom variable macros specified in the host and service entries.

```
define command {
    command_name    check_statuspage_component
    command_line    $USER1$/check-statuspage-component.py $_HOSTPAGEID$ $_SERVICECOMPONENTID$
}
```

### check-statuspage-incidents

This plugin reads the unresolved incidents on a Statuspage.io page and returns status to Nagios.  Long output is included with status, names, and short URL to incidents.

Example output:
```
CRITICAL: 1 unresolved issue(s) reported
Monitoring: Resnet router issues ~1500 on 12/05 (http://stspg.io/2e2b5d855)
```

See above to define a host with the _PAGEID custom variable macro.

Define a service with the command:
```
define service {
    host_name                status.example.com
    service_description      Unresolved Incidents
    check_command            check_statuspage_incidents
}
```

Define a command object in your Nagios configuration which references the custom variable macros specified in the host and service entries.

```
define command {
    command_name    check_statuspage_incidents
    command_line    $USER1$/check-statuspage-incidents.py $_HOSTPAGEID$
}
```