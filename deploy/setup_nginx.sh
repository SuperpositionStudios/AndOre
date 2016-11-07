#!/bin/bash
# $1 = 1 if websocket, 0 if normal http
# $2 = number of server blocks, (1 or 2, sleipnir only needs 2)
# $3 = port for server block 1.
# $4 = domain for server block 1
# $5 = port for server block 2
# $6 = domain for server block 2
echo -e "\nBacking up nginx config...\n"

cd /etc/nginx/sites-enabled/;
sudo touch default;
sudo mv default default.backup;
sudo touch default;

echo -e "Writing nginx files...\n"

echo -e "Setting up nginx with $2 server blocks.\n"

if [ $2 == 1 ]
then
	echo -e "First server block port: $3 domain: $4.\n";

	echo -e "server {" >> default;

	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $4" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tproxy_pass_header Server;" >> default;
    echo -e "\t" >> default;
	echo -e "\tlocation / {" >> default;

	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	#echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header X-Forward-Proto \$scheme;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	if [ $1 == 1 ]
	then
		echo -e "\t\tproxy_read_timeout  36000s;" >> default;
		echo -e "\t\t\n" >> default;
		echo -e "\t\tproxy_http_version 1.1;" >> default;
		echo -e "\t\tproxy_set_header Upgrade \$http_upgrade;" >> default;
		echo -e "\t\tproxy_set_header Connection \"upgrade\";" >> default;
		echo -e "\t\t\n" >> default;
	else
		echo -e "\t\tproxy_connect_timeout 300;" >> default;
	fi
	echo -e "\t\tproxy_pass http://127.0.0.1:$3;" >> default;

	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;
else
	echo -e "\nFirst server block port: $3 domain: $4.";

	echo -e "server {" >> default;

	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $4" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tproxy_pass_header Server;" >> default;
    echo -e "\t" >> default;
	echo -e "\tlocation / {" >> default;

	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	#echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header X-Forward-Proto \$scheme;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	if [ $1 == 1 ]
	then
		echo -e "\t\tproxy_read_timeout  36000s;" >> default;
		echo -e "\t\t\n" >> default;
		echo -e "\t\tproxy_http_version 1.1;" >> default;
		echo -e "\t\tproxy_set_header Upgrade \$http_upgrade;" >> default;
		echo -e "\t\tproxy_set_header Connection \"upgrade\";" >> default;
		echo -e "\t\t\n" >> default;
	else
		echo -e "\t\tproxy_connect_timeout 300;" >> default;
	fi
	echo -e "\t\tproxy_pass http://127.0.0.1:$3;" >> default;

	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;

	echo -e "\nSecond server block port: $5 domain: $6.\n";
	echo -e "\n" >> default;

	echo -e "server {" >> default;

	echo -e "\tclient_max_body_size 999M;" >> default;
	echo -e "\tlisten 80;" >> default;
	echo -e "\tserver_name $6" >> default;
	echo -e "\taccess_log off;" >> default;
	echo -e "\tproxy_pass_header Server;" >> default;
    echo -e "\t" >> default;
	echo -e "\tlocation / {" >> default;

	echo -e "\t\tproxy_set_header    Host            \$host;" >> default;
	echo -e "\t\tproxy_set_header    X-Real-IP       \$remote_addr;" >> default;
	#echo -e "\t\tproxy_set_header    X-Forwarded-for \$remote_addr;" >> default;
	echo -e "\t\tproxy_set_header X-Forward-Proto \$scheme;" >> default;
	echo -e "\t\tport_in_redirect off;" >> default;
	if [ $1 == 1 ]
	then
		echo -e "\t\tproxy_read_timeout  36000s;" >> default;
		echo -e "\t\t\n" >> default;
		echo -e "\t\tproxy_http_version 1.1;" >> default;
		echo -e "\t\tproxy_set_header Upgrade \$http_upgrade;" >> default;
		echo -e "\t\tproxy_set_header Connection \"upgrade\";" >> default;
		echo -e "\t\t\n" >> default;
	else
		echo -e "\t\tproxy_connect_timeout 300;" >> default;
	fi
	echo -e "\t\tproxy_pass http://127.0.0.1:$5;" >> default;

	echo -e "\t}" >> default;
	echo -e "\t" >> default;
	echo -e "\terror_page   500 502 503 504  /50x.html;" >> default;
	echo -e "\tlocation = /50x.html {" >> default;
	echo -e "\t\troot   /usr/local/nginx/html;" >> default;
	echo -e "\t}" >> default;
	echo -e "}" >> default;
	
fi

echo -e "Finished setting up nginx config :D\n";
echo -e "Now I'm going to restart nginx for you\n";
sudo nginx -t;
sudo service nginx restart;
echo -e "\nHave a nice day :D\n";
