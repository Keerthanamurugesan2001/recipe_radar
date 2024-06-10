# DJANGO PRODUCTION SETUP WITH NGINX FOR BOTH ASGI AND WSGI

### Create Instance.
#### Launch instance
Start by logging in to your AWS Management Console.
Navigate to the EC2 service and click on "Launch Instance."
Choose an Amazon Machine Image (AMI) for your instance. For example, select Ubuntu.
Follow the instance configuration steps, including choosing the instance type and configuring network settings.
#### Key pair
Key Pair for creating SSH client. The SSH client provides a secure environment in which to connect to a remote computer.
Download and save the private key file that will be generated. This file will be used for securely connecting to your instance via SSH.

Note:
if removing ssh from inbound rule we connect in future.
          
After the successful creation of an instance, connect it.

### To connect the remote server in the terminal

```
chmod 400 your-key-pair.pem
```
This command changes the permissions on the SSH key pair file to make it readable only by the file owner (you) and not accessible by others. 

```
ssh -i your-key-pair.pem ubuntu@public-ip-or-dns
```
 This command initiates an SSH connection to your EC2 instance. It uses the SSH key pair (your-key-pair.pem) for authentication.
Replace your-key-pair.pem with the actual path to your private key file.
Replace ubuntu with the appropriate username for the AMI you are using (e.g., "ubuntu" for Ubuntu-based AMIs).
Replace public-ip-or-dns with the public IP address or domain name of your EC2 instance.
ex:
```
ssh -i myapp.pem ubuntu@15.206.163.199
```
### To connect the remote server in the vscode:
Install extension remote ssh.
Open remote explorer. And create remote ssh
Add the SSH Host Configuration:

Host 15.206.163.199
    HostName 15.206.163.199
    User ubuntu
    IdentityFile /home/softsuave/myapp.pem
    
Host: This is a label for the host configuration. It's the name you will use to connect to the host.
HostName: The IP address or domain name of the remote host.
User: The username to use when connecting to the host (in this case, "ubuntu").
IdentityFile: The path to your private key file, which is used for authentication when connecting.


### Prerequisites
- Gunicorn
- Nginx &
Required packages for your project

_Note: Please make sure your project running correctly and 
Be sure to include localhost as one of the options in allowed hosts since you will be proxying connections through a local Nginx instance._ 

### settings.py

```
ALLOWED_HOSTS = ['your_server_domain_or_IP', 'second_domain_or_IP', . . ., 'localhost']

```
```
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
```
## Completing initial project setup
```
python manage.py makemigrations
python manage.py migrate
```
We can collect all of the static content into the directory location that you configured by typing:
```
python manage.py collectstatic
```
We will have to confirm the operation. The static files will then be placed in a directory called static within your project directory.

## Testing Gunicorn’s or Uvicorn's Ability to Serve the Project
We can test this by entering the project directory and using gunicorn to load the project’s WSGI module:
- `Gunicorn`
```
gunicorn --bind 0.0.0.0:8000 myproject.wsgi
```
(or)
- `Uvicorn`
```
uvicorn myproject.asgi:application
```

### Add Inbound rules:

In EC2, Open instance navigate to security, Click Security groups, Where you can see Inbound rules.

Edit inbound rule,

![image](https://github.com/Antony-M1/django-production-setup/assets/101241405/208678d2-baf0-4653-9678-495009881d8b)


This will start Gunicorn or Uvicorn on the same interface that the Django development server was running on. We can go back and test the app again in your browser

Example link: http://15.206.163.199:8000

_Note: The admin interface will not have any of the styling applied since **Gunicorn or Uvicorn does not know how to find the static CSS content** responsible for this_

## Creating systemd Socket and Service Files for Gunicorn or Uvicorn
We have tested that Gunicorn can interact with our Django application, but we should now implement a more robust way of starting and stopping the application server.
To accomplish this, We'll make [systemd](https://chat.openai.com/share/35085535-9f16-4ade-ad28-24371e24d94d) service and socket files

Start by creating and opening a systemd socket file for Gunicorn with sudo privileges:
```
sudo nano /etc/systemd/system/gunicorn.socket
```

Inside, We will create a [Unit] section to describe the socket, a [Socket] section to define the socket location, and an [Install] section to make sure the socket is created at the right time:

### gunicorn.socket
File name `gunicorn.socket` Same file for both ASGI & WSGI setup
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```
Save and close the file when you are finished

Next, Create and open a systemd service file for Gunicorn with sudo privileges in your text editor. The service filename should match the socket filename with exception of the extension
```
sudo nano /etc/systemd/system/gunicorn.service
```
### gunicorn.service for WSGI
File name `gunicorn.service`
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myprojectdir
ExecStart=/home/ubuntu/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```

### gunicorn.service for ASGI
File name `gunicorn.service`
```
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myprojectdir
ExecStart=/home/ubuntu/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          -k uvicorn.workers.UvicornWorker \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.asgi:application

[Install]
WantedBy=multi-user.target
```

1. Start with the [Unit] section, which is used to specify metadata and dependencies.
   - Put a description of the service here and tell the init system to only start this after the networking target has been reached.
   - Because your service relies on the socket from the socket file, you need to include a Requires directive to indicate that relationship
2. Next, you’ll open up the [Service] section
   - Specify the user and group that you want to process to run under.
   - You will give your regular user account ownership of the process since it owns all of the relevant files. You’ll give group ownership to the www-data group so that Nginx can communicate easily with Gunicorn.
   - Then you’ll map out the working directory and specify the command to use to start the service.
   - In this case, you have to specify the full path to the Gunicorn executable, which is installed within our virtual environment.
   - You will then bind the process to the Unix socket you created within the /run directory so that the process can communicate with Nginx.
   - You log all data to standard output so that the journald process can collect the Gunicorn logs. You can also specify any optional Gunicorn tweaks here. For example, you specified 3 worker processes in this case:
3. Finally, We’ll add an [Install] section.
   - This will tell systemd what to link this service to if you enable it to start at boot. You want this service to start when the regular multi-user system is up and running

With that, your systemd service file is complete. Save and close it now.

You can now start and enable the Gunicorn socket. This will create the socket file at /run/gunicorn.sock now and at boot. When a connection is made to that socket, systemd will automatically start the gunicorn.service to handle it:
```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```
You can confirm that the operation was successful by checking for the socket file.

## Checking for the Gunicorn socket file
Check the status of the process to find out whether it was able to start:
```
sudo systemctl status gunicorn.socket
```
You should receive an output like this:
```
Output
● gunicorn.socket - gunicorn socket
     Loaded: loaded (/etc/systemd/system/gunicorn.socket; enabled; vendor preset: enabled)
     Active: active (listening) since Mon 2022-04-18 17:53:25 UTC; 5s ago
   Triggers: ● gunicorn.service
     Listen: /run/gunicorn.sock (Stream)
     CGroup: /system.slice/gunicorn.socket

Apr 18 17:53:25 django systemd[1]: Listening on gunicorn socket.
```

Next, check for the existence of the gunicorn.sock file within the /run directory:
```
file /run/gunicorn.sock
```
```
Output
/run/gunicorn.sock: socket
```

## Testing Socket Activation
Currently, if you’ve only started the gunicorn.socket unit, the gunicorn.service will not be active yet since the socket has not yet received any connections. You can check this by typing:
```
sudo systemctl status gunicorn
```
You should receive output like this
```
Output
○ gunicorn.service - gunicorn daemon
     Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
     Active: inactive (dead)
TriggeredBy: ● gunicorn.socket
```
You can verify that the Gunicorn service is running by typing:
```
sudo systemctl status gunicorn
```
 
## Configure Nginx to Proxy Pass to Gunicorn or Uvicorn
Now that Gunicorn is set up, you need to configure Nginx to pass traffic to the process
Start by creating and opening a new server block in Nginx sites-available directory
```
sudo nano /etc/nginx/sites-available/<myproject>
```
Inside /etc/nginx/sites-available/<myproject>
```
server {
    listen 80;
    server_name server_domain_or_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/myprojectdir;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```
- In server block We're specifying that this should listen on the normal port 80 and it should response to our server's domain or IP address
server's domain or IP address:
ex:
```
server_name 15.206.163.199 django.erpnext.tech;
```
 First is the IP address, and second is the hostname.
  
- Next Step, We'll tell Nginx to ignore any problems with finding a favicon. We'll also tell it where to find the static assets that we've collected in our projectdir/static directory. All of these files have a standand URI prefix of "/static", So we can create a location block to match those requests.
- Finally, Create a location / {} block to match all other requests. Inside of this location, We'll include the standard proxy_params(Forwarding to app server) file included with the Nginx installation and then pass the traffic directly to the gunicorn socket



Save and close the file when We're finished. Now we can enable the file by linking it to the sites-enabled directory
```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
```

Test our Nginx configuration for syntax errors by typing
```
sudo nginx -t
```
If no errors are reported, go ahead and restart Nginx by typing:
```
sudo systemctl restart nginx
```


Finally, We will need to open up our firewall to normal traffic on port 80. Since we no longer need access to the development server, We can remove the rule to open port 8000 as well:
```
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

We should now be able to go to our server’s domain or IP address to view our application.


# certbot

SSH into the server running your HTTP website as a user with sudo privileges. Install using snapd.
## Prepare the Certbot command

```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
Execute the following instruction on the command line on the machine to ensure that the certbot command can be run.
## Choose how you'd like to run Certbot
```
sudo certbot --nginx
```

Run this command to get a certificate and have Certbot edit your nginx configuration automatically to serve it, turning on HTTPS access in a single step.

To confirm that your site is set up properly, visit https://yourwebsite.com/ in your browser and look for the lock icon in the URL bar.

# Hostinger

## create subdomain,
Navigate to DNS record and create new subdomain,
![image_2023_10_18T14_45_05_298Z](https://github.com/Antony-M1/django-production-setup/assets/101241405/848244cd-2871-49d1-baac-6b2381e22eda)

Where Type A -> To allow to certbot A is need, To Run in http we can use CNAME itself.

#### A Record:
An A record (Address Record) is used to map a domain or subdomain to an IP address.

#### CNAME Record:
A CNAME record (Canonical Name Record) is used to create an alias or shortcut for a domain or subdomain

name -> domain name, here it is django

point to -> Add the IP address

TTL -> TTL is measured in seconds, and it signifies the amount of time a DNS resolver should keep a record in its cache before checking for an updated version from the authoritative DNS server.


![image_2023_10_18T13_43_39_352Z](https://github.com/Antony-M1/django-production-setup/assets/101241405/6442568a-b2d3-40de-a767-d0d042877a6b)


# Reference Site
[How To Set Up an ASGI Django App with Postgres, Nginx, and Uvicorn on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-asgi-django-app-with-postgres-nginx-and-uvicorn-on-ubuntu-20-04)

[How To Set Up Django with Postgres, Nginx, and Gunicorn on Ubuntu 22.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04)

[Certbot](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal&tab=standard)
# Ref Youtube link:
[deploy the django in ec2](https://www.youtube.com/watch?v=uiPSnrE6uWE)
[ssh client](https://www.youtube.com/watch?v=jIxkbXB6-38)




