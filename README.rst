ascend
======

AutoScale group, policy, webhook, and launch configuration setup program

Requirements
------------

ascend requires the requests package to make API calls to Rackspace

Details
-------

ascend sets default values for multiple options that can be specified, in
order to ensure that sane values are set when omitted from the call.

Based on the change value (Default is 1 server) the script will create a
matching negative policy as well. For example if you specify the change value
to add 5 servers, then a corresponding webhook will be created that removes 5
servers as well. If the change value specified however is negative, then no
corresponding webhook will be created to add that same number of server(s) back.

You can specify multiple custom networks by using the --networks flag and
listing all network UUIDs seperated by spaces. Public and ServiceNet will
automatically be added unless the --no-public or --no-service flags are
provided in the call.

Multiple metadata key=value pairs can also be specified as well. Using the
--meta flag you can specify up to the maxServerMeta absolute limit on the
account. If the metadata key=value pair is formatted incorrectly a warning
will be displayed and the metadata item will not be added to the Launch
Configuration section for the Autoscaling group.

A --dry-run option can be specified in order to view the URLs and corresponding
data objects that will be created for not only the autoscale group, but also
for the anonymous webhook(s) as well.

Verbose (-v) will show all data objects created, instructions and code to
execute the anonymous webhooks, but also links to the documentation as well.

Usage
-----

::

    usage: ascend [-h] -u <username> -k <api-key> -r <data-center> -n
                 <group_name> --flavor <flavor_id> --image <image_uuid>
                 [--server-name <server_name>] [--meta <key=value>]
                 [--no-public] [--no-service]
                 [--networks [<network-uuid> [<network-uuid> ...]]]
                 [--group-cooldown <group-cooldown>]
                 [--group-min <min-servers>] [--group-max <max-servers>]
                 [--policy-cooldown <policy-cooldown>]
                 [--policy-change <policy-change>]
                 [--policy-name <policy-name>] [--webhook-name <webhook-name>]
                 [--dry-run] [-v]

    AutoScale group, policy, webhook, and launch configuration setup program

    optional arguments:
      -h, --help            show this help message and exit
      -u <username>, --username <username>
                            Cloud account user name
      -k <api-key>, --api-key <api-key>
                            Cloud users API key
      -r <data-center>, --region <data-center>
                            Data center region to create the autoscale group in
      -n <group_name>, --name <group_name>
                            Name for the auto scale group being created
      --flavor <flavor_id>  Flavor ID for to be used for all servers created under
                            this auto scale group
      --image <image_uuid>  Image UUID used to create every server under this auto
                            scale group
      --server-name <server_name>
                            Server name to prepend to the auto generated server
                            name when a server is created
      --meta <key=value>    Meta key/value pair to set on each created server
      --no-public           Do not connect new servers to Public Net
      --no-service          Do not connect new servers to Service Net
      --networks [<network-uuid> [<network-uuid> ...]]
                            Connect to additional networks by listing the network
                            UUIDs
      --group-cooldown <group-cooldown>
                            Group cooldown in seconds to wait for the next action
                            : Default is 60 seconds
      --group-min <min-servers>
                            Minimum number of servers that can be in the group :
                            Default is 0
      --group-max <max-servers>
                            Maximum number of servers that can be created for the
                            current group : Default is 10
      --policy-cooldown <policy-cooldown>
                            Number of seconds for cooldown on policy : Default is
                            60 seconds
      --policy-change <policy-change>
                            Number of servers to change either positive or
                            negative when the policy is executed : Default is 5
      --policy-name <policy-name>
                            Name of the default policy to be created : Defaults to
                            "Default Policy"
      --webhook-name <webhook-name>
                            Name of the default webhookto use : Defaults to
                            "Default Webhook"
      --dry-run             Display URLs and data objects for group and webhooks
      -v, --verbose         Show all information


Examples
--------

The example below use $OS_USERNAME to represent the Rackspace Cloud account 
username, and $OS_PASSWORD to represent the users specified API-KEY

To create an autoscale group called my-group, using performance 1 flavor,
and Ubuntu 12.10 servers in DFW
::

    ascend -u $OS_USERNAME -k $OS_PASSWORD -n my-group --flavor performance1-1 --image d45ed9c5-d6fc-4c9d-89ea-1b3ae1c83999 -r dfw

To create the same autoscale group but now with all information output
to the terminal using verbose
::

    ascend -u $OS_USERNAME -k $OS_PASSWORD -n my-group --flavor performance1-1 --image d45ed9c5-d6fc-4c9d-89ea-1b3ae1c83999 -r dfw -v

Dry run to show data objects and URLs that would be created
::

    ascend -u $OS_USERNAME -k $OS_PASSWORD -n my-group --flavor performance1-1 --image d45ed9c5-d6fc-4c9d-89ea-1b3ae1c83999 -r dfw --dry-run

Additional Information
----------------------

Autoscale API documentation:
http://docs.rackspace.com/cas/api/v1.0/autoscale-devguide/content/Overview.html

maxServerMeta absolute limit for servers:
http://docs.rackspace.com/servers/api/v2/cs-devguide/content/Create_or_Replace_Metadata-d1e5358.html
