#!/usr/bin/python -tt

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import logging.handlers
import os
import re
import shutil
import subprocess
import yaml
import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config')
args = parser.parse_args(sys.argv[1:])
directory = os.path.dirname(os.path.realpath(__file__))

if args.config != None:
    config_file = args.config
else:
    config_file = directory + '/' + 'config.yaml'

config_stream = open( config_file, 'r')
config = yaml.load(config_stream)

log = logging.getLogger('log')
log.setLevel(config['logs']['level'])
log_handler = logging.handlers.RotatingFileHandler(config['logs']['file'],
                                                   maxBytes=config['logs']['max_size'],
                                                   backupCount=4)
f = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s",
                      "%B %d %H:%M:%S")
log_handler.setFormatter(f)
log.addHandler(log_handler)


class webhookReceiver(BaseHTTPRequestHandler):

    def run_it(self, cmd, env):
        """
            runs a command
        """
        log.debug('Running: {0}'.format(cmd))
        log.debug('Environment: {0}'.format(env))
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, env=env)
        p.wait()
        out, err = p.communicate()

        if out != None:
            log.debug("STDOUT:\n" + out)

        if err != None:
            log.debug("STDERR\n" + err)

        if p.returncode != 0:
            log.critical("Non zero exit code:{0} executing: {1}".format(p.returncode, cmd))
        return p.stdout

    def do_POST(self):
        """
            receives post, handles it
        """
        log.debug('got post')
        message = 'OK'
        self.rfile._sock.settimeout(5)
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.send_header("Content-length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)
        log.debug('gitlab connection should be closed now.')
        # parse data
        data = json.loads(data_string)
        for hook in config['hooks']:
            log.debug('Testing {0}'.format(hook['name']))
            if data.has_key('repository') and data['repository'].has_key('name') and data['repository']['name'] == hook['repository']:
                log.debug('Repository matches')
                if data.has_key('ref') and data['ref'] == 'refs/heads/' + hook['branch']:
                    log.debug('Branch {0} matches'.format(hook['branch']))

                    if hook['script'][0] == '/':
                        hook_script = hook['script']
                    else:
                        hook_script = directory + '/' + hook['script']
                    self.run_it('{0} {1} {2}'.format(hook_script, hook['directory'], hook['branch']), hook['env'] if hook.has_key('env') else {})
                else:
                    log.debug('Branch {0} doesn\'t match {1}'.format(hook['branch'], data['ref']))

    def log_message(self, formate, *args):
        """
            disable printing to stdout/stderr for every post
        """
        return


def main():
    """
        the main event.
    """
    try:
        server = HTTPServer(('', 8000), webhookReceiver)
        log.info('started web server...')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('ctrl-c pressed, shutting down.')
        server.socket.close()

if __name__ == '__main__':
    main()
