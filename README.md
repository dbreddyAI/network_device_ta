### Splunk Network Device Modular Input 

### Overview
This is a Splunk modular input add-on for running commands on network devices.  The
Python script uses pexpect to interact with devices.  

The modular input is designed to work with the sdiff App.

While the App was designed to work with network devices, it really can be used to 
gather data from any device.  The tricky part is writting a proper "login driver"
to support the expected prompts and be wary of fatal splash screens.

If you have a requirement to have Splunk gather data from unsupported OSs, collect 
data WITHOUT and agent / forwarder, or have devices that you cannot install software
on... then this is the perfect App for you.

### Features
* Simple UI based configuration via Splunk Manager
* The output of each command is a single multiline Splunk event
* Blank commands are skipped over
* Error trapping for know error types - send me screen shots of any new ones!
* Recommended command sets to capture:
  - Running configs
  - Startup configs
  - Route tables
  - Connected VPN users
  - Interface statuses
  - Interface throughput & errors

### Dependencies
I have only tested this on Splunk 6.0+

### Logging and Troubleshooting
Any modular input errors will get written to $SPLUNK_HOME/var/log/splunk/splunkd.log

### Contact
This project was initiated by James Donn
<table>
  <tr>
    <td><em>Email</em></td>
    <td>jim@splunk.com</td>
  </tr>
</table>
