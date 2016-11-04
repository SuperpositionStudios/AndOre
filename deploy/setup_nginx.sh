#!/bin/bash
# $1 = number of server blocks, (1 or 2, sleipnir only needs 2)
# $2 = port for server block 1.
# $3 = domain for server block 1
# $4 = port for server block 2
# $5 = domain for server block 2
echo -e "\nBacking up nginx config...\n"

cd /etc/nginx/sites-enabled/;
sudo touch default;
sudo mv default default.backup;
sudo touch default;

echo -e "Writing nginx files...\n"

echo -e "Setting up nginx with $1 server blocks.\n"

if [ $1 == 1 ]
then
	echo -e "First server block port: $2 domain: $3.\n";

	echo -e "server {" >> default;
	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $3" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tlocation / {" >> default;
	echo -e "\t\tproxy_pass http://127.0.0.1:$2;" >> default;
	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	echo -e "\t\tproxy_connect_timeout 300;" >> default;
	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;
else
	echo -e "\nFirst server block port: $2 domain: $3.";
	echo -e "server {" >> default;
	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $3" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tlocation / {" >> default;
	echo -e "\t\tproxy_pass http://127.0.0.1:$2;" >> default;
	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	echo -e "\t\tproxy_connect_timeout 300;" >> default;
	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;

	echo -e "\nSecond server block port: $4 domain: $5.\n";
	echo -e "\n" >> default;

	echo -e "server {" >> default;
	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $5" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tlocation / {" >> default;
	echo -e "\t\tproxy_pass http://127.0.0.1:$4;" >> default;
	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	echo -e "\t\tproxy_connect_timeout 300;" >> default;
	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;

	echo -e "Finished setting up nginx config :D\n";
	
fi
