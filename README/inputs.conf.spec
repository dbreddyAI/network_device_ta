[network_device://<name>]

hostname = <string>
* IP or hostname of the device you would like to connect to

username = <string>
* The Username to connect with

password = <string>
* The password for the username

telnet = <value>
* Telnet

commands = <string>
* Commands

ena_pass = <string>
* Enable Password

interval = auto|<relative time expression>|<cron expression>
* Use to configure the schedule for the given database monitor.
* Schedule types:
* - auto - The scheduler automatically runs when a CONFIG-T trap is received 
* - relative time expression - The number of seconds or a relative time expression.
*   Examples:
*           interval = 60 (run every 60 seconds)
*           interval = 1h (run every hour)
* - cron expression
*   Examples:
*           interval = 0/15 * * * *       (run every 15 minutes)
*           interval = 0 18 * * MON-FRI * (run every weekday at 6pm)

