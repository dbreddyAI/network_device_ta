'''
Modular Input Script for Network Devices
James Donn
'''


### Import modules
import pexpect
import string
import datetime
import os,sys,logging
import xml.dom.minidom, xml.sax.saxutils
import time
from time import sleep
import threading


### Set up logging suitable for splunkd consumption
logging.root
#logging.root.setLevel(logging.DEBUG)
logging.root.setLevel(logging.ERROR)
formatter = logging.Formatter('%(levelname)s %(message)s')

### With zero args , should go to STD ERR
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)


### Define a scheme for introspection
SCHEME = """<scheme>
    <title>Network Devices</title>
    <description>Execute commands on network devices.</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>simple</streaming_mode>
    <use_single_instance>false</use_single_instance>
    <endpoint>
        <args>    
            <arg name="hostname">
                <title>Hostname</title>
                <description>IP or hostname of the device you would like to query</description>
                <required_on_edit>true</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>                  
            <arg name="username">
                <title>Username</title>
                <description>Username to access the device</description>
                <required_on_edit>true</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="password">
                <title>Password</title>
                <description>Password for username</description>
                <required_on_edit>true</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="ena_pass">
                <title>Enable password</title>
                <description>Enable Password</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="telnet">
                <title>Telnet</title>
                <description>Enable telnet access</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="commands">
                <title>Commands</title>
                <description>List of commands to be run against network device</description>
                <required_on_edit>true</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
        </args>
    </endpoint>
</scheme>
"""


### Validate the scheme, only required variables are tested
def do_validate():
    
    try:
        config = get_validation_config() 
        
        hostname = config.get("hostname")
        username = config.get("username")
        password = config.get("password")
        telnet   = config.get("telnet")
        commands = config.get("commands")

        validationFailed = False

        if not hostname:
            print_validation_error("Hostname must have a value")
            validationFailed = True
        if not username:
            print_validation_error("Username must have a value")
            validationFailed = True
        if not password:
            print_validation_error("Password must have a value")
            validationFailed = True
        if not hostname:
            print_validation_error("Hostname must have a value")
            validationFailed = True
        if not telnet and int(telnet) < 0 and int(telnet) > 2:
            print_validation_error("Telnet value must be 0 or 1")
            validationFailed = True
        if not commands:
            print_validation_error("Commands must have a value")
            validationFailed = True
        if validationFailed:
            sys.exit(2)
               
    except RuntimeError,e:
        logging.error("Looks like an error: %s" % str(e))
        sys.exit(1)
        raise   

### Run all of the necessary functions
def do_run():
    
    ### Get and set parameters
    config       = get_input_config() 
    hostname     = config.get("hostname")
    username     = config.get("username")
    password     = config.get("password")
    ena_pass     = config.get("ena_pass")
    telnet       = config.get("telnet")
    commands     = config.get("commands")
    command_list = string.split(commands, '\n')
    ssh_newkey   = r'Are you sure you want to continue connecting \(yes/no\)\?'
    prompt       = '[$#]'

    ### Login to the host
    logging.debug('EXP: Attempting to login...')
    child = pexpect.spawn('ssh -l %s %s'%(username, hostname))

    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'Could not resolve hostname', '[Pp]assword:'])

    ### Timeout
    if i == 0: 
        die(child, 'ERROR!\nSSH timed out. Here is what SSH said:')

    ### SSH does not have the public key. Just accept it.
    elif i == 1:
        child.sendline ('yes')
        child.expect ('[Pp]assword: ')

    ### Bad hostname
    elif i == 2: 
        die(child, 'ERROR!\nCold not resolve hostname:')

    ### Expect the password prompt
    elif i == 3: 
        logging.debug('EXP: Sending password')
        child.sendline(password)
        logging.debug('EXP: Sent password')

    ### We would like to see the prompt, but bail if we are asked for the password again
    child.sendline('')
    i = child.expect (['Permission denied', '[Pp]assword:', prompt])
    if i == 0:
        print 'Permission denied on host: ', hostname
        print child.before, child.after
        sys.exit (1)
    if i == 1:
        print 'Bad Password on host: ', hostname
        logging.error('EXP: Bad password on host - ' + hostname )
        sys.exit (1)
    if i == 2:
        child.expect (prompt)
    logging.debug('EXP: Logged into the host - ' + hostname)

    ### Learn the prompt
    child.sendline('')
    child.sendline('')
    i = child.expect(prompt)
    if i == 0:
        llprompt = child.before + child.after
        lprompt = llprompt.strip()
        logging.debug('EXP: Captured prompt --\"' + lprompt + '\"--')

    #### Now that we have a better prmpt, execute all the commands in the list
    for commando in command_list[0:]:
        commando = commando.rstrip()
        ### We will skip empty commands
        if len(commando) > 0:
            # child.delaybeforesend = 1
            # sys.stdout.write (child.before + child.after)
            # sys.stdout.flush()
            child.sendline(commando) 
            j = child.expect_exact ([pexpect.TIMEOUT, 'ermission denied', 'command not found', lprompt])
            if j == 0:
                print lprompt+child.before,child.after
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' command=\"' + commando + '\"'
                sleep(1)
                die(child, 'ERROR!\nCommand timed out:')
            if j == 1:
                print lprompt+child.before,child.after
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' command=\"' + commando + '\"'
                sleep(1)
                logging.debug('EXP: Permission denied on execute command --\"' + commando + '\"--')
            if j == 2:
                print lprompt+child.before,child.after
                print lprompt+child.before,child.after
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' command=\"' + commando + '\"'
                sleep(1)
                logging.debug('EXP: Could not find command --\"' + commando + '\"--')
            if j == 3:
                print lprompt+child.before,child.after
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' command=\"' + commando + '\"'
                sleep(1)
                logging.debug('EXP: Completed command - \"' + commando + '\"')
        else:
           logging.debug('EXP: Empty commands are skipped.')
    child.expect_exact(lprompt)
    child.sendline('')
    child.expect_exact(lprompt)
    ### This print statement is neccesary to capture the last command
    print lprompt+child.before,child.after
    child.sendline('exit')
 
### Define how you want to die
def die(child, errstr):
    print errstr

### Prints validation error data to be consumed by Splunk
def print_validation_error(s):
    print "<error><message>%s</message></error>" % xml.sax.saxutils.escape(s)
    
### Prints XML stream
def print_xml_single_instance_mode(s):
    print "<stream><event><data>%s</data></event></stream>" % xml.sax.saxutils.escape(s)
    
### Prints XML stream
def print_xml_multi_instance_mode(s,stanza):
    print "<stream><event stanza=""%s""><data>%s</data></event></stream>" % stanza,xml.sax.saxutils.escape(s)
    
### Prints simple stream
def print_simple(s):
    print "%s\n" % s
    
### If the --scheme flag is used, print the scheme
def usage():
    print "usage: %s [--scheme|--validate-arguments]"
    logging.error("Incorrect Program Usage")
    sys.exit(2)

### If the --scheme flag is used, print the scheme
def do_scheme():
    print SCHEME


### Read the XML configuration passed from splunkd, need to refactor to support single instance mode
def get_input_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        conf_node = root.getElementsByTagName("configuration")[0]
        if conf_node:
            logging.debug("XML: found configuration")
            stanza = conf_node.getElementsByTagName("stanza")[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    logging.debug("XML: found stanza " + stanza_name)
                    config["name"] = stanza_name

                    params = stanza.getElementsByTagName("param")
                    for param in params:
                        param_name = param.getAttribute("name")
                        logging.debug("XML: found param '%s'" % param_name)
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            logging.debug("XML: '%s' -> '%s'" % (param_name, data))

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
           checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            config["checkpoint_dir"] = checkpnt_node.firstChild.data

        if not config:
            raise Exception, "Invalid configuration received from Splunk."

        
    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config

### Read XML configuration passed from splunkd, need to refactor to support single instance mode
def get_validation_config():
    val_data = {}

    # read everything from stdin
    val_str = sys.stdin.read()

    # parse the validation XML
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug("XML: found items")
    item_node = root.getElementsByTagName("item")[0]
    if item_node:
        logging.debug("XML: found item")

        name = item_node.getAttribute("name")
        val_data["stanza"] = name

        params_node = item_node.getElementsByTagName("param")
        for param in params_node:
            name = param.getAttribute("name")
            logging.debug("Found param %s" % name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

    return val_data

if __name__ == '__main__':
      
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":           
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            do_validate()
        else:
            usage()
    else:
        do_run()
        
    sys.exit(0)
