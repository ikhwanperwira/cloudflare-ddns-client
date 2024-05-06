# Google Compute Engine Startup Script
If you are creating Google Compute Engine Instance with ephemeral Public IP address, then you can add this startup script so that your DNS Record is updated automatically based on current Public IP address.
> **_NOTE:_** Currently, it's only supported for Linux-based OSes with systemd startup. It has been tested on Ubuntu 22.04 LTS minimal. I can't guarantee it's worked for another distro, but as long as OS startup is using Systemd, I think it's worked fine.


Here is how you can add custom metadata with the key `startup-script` so that the Cloudflare DDNS is installed and running on the first bootup or every reboot:
> **_NOTE:_** Please replace `<API_TOKEN>`, `<DOMAIN>`, `<SUBDOMAIN>`, `<TTL>`, `<IS_PROXIED: "false"|"true">` as your requirements!
> **_NOTE:_** For the `<API_TOKEN>` permission list, look at [README.md](https://github.com/ikhwanperwira/cloudflare-ddns-client/blob/main/README.md#prerequisites).

* Linux (Systemd)
```
#!/bin/bash

apt update
apt upgrade -y

wget https://raw.githubusercontent.com/ikhwanperwira/cloudflare-ddns-client/main/cf_ddns.py

chmod +x cf_ddns.py
mv cf_ddns.py /usr/bin/

ip addr show | awk '/inet.*e(n.*s|th|o|np)/ {print $2}' | cut -d '/' -f 1 | tr -d '\n' > ethernet_ip.txt
SOURCE_IP=$(cat /tmp/ethernet_ip.txt)

cat <<EOF > /etc/systemd/system/cf_ddns.service
[Unit]
Description=Cloudflare DDNS Client
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/cf_ddns.py <API_TOKEN> <DOMAIN> <SUBDOMAIN> <TTL> <IS_PROXIED: "false"|"true"> "$SOURCE_IP"

[Install]
WantedBy=multi-user.target
EOF

chown root:root /etc/systemd/system/cf_ddns.service
chmod 644 /etc/systemd/system/cf_ddns.service

systemctl enable cf_ddns.service
systemctl start cf_ddns.service
systemctl disable google-startup-scripts
```

> **_NOTE:_** It might be delay, you can see running output with `sudo journalctl -u google-startup-scripts.service -f`
