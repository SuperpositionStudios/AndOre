#!/usr/bin/python2.7
# pip install sultan
# How to use:
# Run this from the command line
# Example Usage: sudo python nginx_setup.py -d sleipnir.iwanttorule.space -p 7100 -o ubuntu


from sultan.api import Sultan
import argparse
import sys

domain = None
port = None

try:
    ### Getting Command Line Options

    parser = argparse.ArgumentParser(description='This is a python script to overwrite your nginx config for deploying applications behind a nginx reverse proxy.')
    parser.add_argument('-d', '--domain', help='Domain for nginx', required=True)
    parser.add_argument('-p', '--port', help='Port of Application behind reverse proxy', required=True)
    parser.add_argument('-o', '--os', help='your os. ["ubuntu16", "ubuntux<16"]')
    args = parser.parse_args()

    domain = args.domain
    port = args.port
    operating_system = args.os
except:
    print("Somehow you caused me to crash")
    sys.exit()

if domain is not None and port is not None:
    s = Sultan()
else:
    print("You must specify a domain and a port")
    sys.exit()


def generate_nginx_config():
    config = []
    config.append('server {')
    config.append('\tclient_max_body_size 999M;')
    config.append('\tlisten 80;')
    config.append('\tserver_name {domain}'.format(domain=domain))
    config.append('\taccess_log off;')
    config.append('\tlocation / {')
    config.append('\t\tproxy_pass http://127.0.0.1:{port};'.format(port=port))
    config.append('\t\tproxy_set_header    Host            \$host;')
    config.append('\t\tproxy_set_header    X-Real-IP       \$remote_addr;')
    config.append('\t\tproxy_set_header    X-Forwarded-for \$remote_addr;')
    config.append('\t\tport_in_redirect off;')
    config.append('\t\tproxy_connect_timeout 300;')
    config.append('\t}')
    config.append('\t')
    config.append('\terror_page   500 502 503 504  /50x.html;')
    config.append('\tlocation = /50x.html {')
    config.append('\t\troot   /usr/local/nginx/html;')
    config.append('\t}')
    config.append('}')
    """
    config = server {
        client_max_body_size 999M;
        listen   80;
        server_name  {domain};
        access_log off;
        location / {
            proxy_pass http://127.0.0.1:{port};
            proxy_set_header    Host            $host;
            proxy_set_header    X-Real-IP       $remote_addr;
            proxy_set_header    X-Forwarded-for $remote_addr;
            port_in_redirect off;
            proxy_connect_timeout 300;
        }

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/local/nginx/html;
        }
    }.format(domain=domain, port=port)
    return config
    """
    return config


def write_nginx_config():
    s.cd("/etc/nginx/sites-enabled/").and_().sudo("touch default").run()
    s.cd("/etc/nginx/sites-enabled/").and_().sudo("mv default default.backup").run()
    s.cd("/etc/nginx/sites-enabled/").and_().sudo("touch default").run()
    config = generate_nginx_config()
    for line in config:
        s.sudo('echo "{}" >> /etc/nginx/sites-enabled/default'.format(line)).run()


def restart_nginx():
    s.sudo('service nginx restart')


def test_config_file():
    s.sudo('nginx -t')

write_nginx_config()
test_config_file()
restart_nginx()
