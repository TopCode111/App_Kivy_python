PIP_USER=jhorak
PIP_PASSWD=YrUqdDs7Vios8QfLDtii

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

echo "---- CREATING RUN ALIAS IN .bashrc ----"
if [[ $(grep -c "tag_app" "/home/nsw/.bashrc") -eq 0 ]]
then
   echo "alias run=\"cd $(cd ../ && pwd)/tag_life && python3 tag_app/main.py\"" >> /home/nsw/.bashrc
else
   echo "alias already exists, skipping"
fi

# install dependencies
echo "---- INSTALLING DEPENDENCIES ----"
apt-get update && apt-get update

# Install necessary system packages
apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    sox --fix-missing

apt-get install -y libmtdev-dev
apt-get install -y libgl1-mesa-dev
apt-get install -y libgles2-mesa-dev
apt-get install -y libatlas-base-dev --fix-missing

# Install gstreamer for audio, video (optional)
apt-get install -y \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

# uninstall python3-numpy/scipy - will be installed from pip
apt-get remove -y python3-numpy python3-scipy

# upgrade pip3
pip3 install --upgrade pip

# add piwheels for faster install
echo "---- ADDING PIWHEELS MIRROR ----"
if [[ $(grep -c "piwheels" "/etc/pip.conf") -eq 0 ]]
then
   echo "
   [global]
   extra-index-url=https://www.piwheels.org/simple
   " >>  /etc/pip.conf
else
   echo "piwheels already added, skipping"
fi


echo "---- INSTALLING CYTHON FIRST ----"
pip3 install -r <(cat requirements.txt | grep Cython) -i https://www.piwheels.org/simple

echo "---- INSTALLING NUMPY AND SCIPY ----"
pip3 install -r <(cat requirements.txt | grep numpy) -i https://www.piwheels.org/simple
pip3 install -r <(cat requirements.txt | grep scipy) -i https://www.piwheels.org/simple

echo "---- INSTALLING AREAD FROM NEURONSW PIPY ----"
pip3 install -r <(cat requirements.txt | grep aread) -i "https://$PIP_USER:$PIP_PASSWD@docker.neuronsw.com:8082/simple/"

echo "---- INSTALLING KIVY FROM NEURONSW PIPY ----"
pip3 install -r <(cat requirements.txt | grep Kivy) -i "https://$PIP_USER:$PIP_PASSWD@docker.neuronsw.com:8082/simple/"

echo "---- INSTALLING OTHER PIP LIBRARIES ----"
pip3 install -r requirements.txt


echo "---- DISABLING JACK SERVICE ----"
systemctl stop jack-client.service
systemctl disable jack-client.service

systemctl stop jack-server-wd.service
systemctl disable jack-server-wd.service

systemctl stop jack-server.service 
systemctl disable jack-server.service 


echo "---- CREATING DB FOLDER ----"
mkdir -p "/var/local/db"
chown nsw:nsw "/var/local/db"


echo "---- START APP AUTOMATICALLY AFTER REBOOT ----"
read -r -p "Do you want to put autostart to services? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
echo "
[Unit]
Description=NSW Tag App
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/home/nsw/tag_life
ExecStart=/usr/bin/python3 /home/nsw/tag_life/tag_app/main.py
User=nsw

[Install]
WantedBy=multi-user.target
" > /lib/systemd/system/tag-life.service

chmod 644 /lib/systemd/system/tag-life.service
systemctl daemon-reload
systemctl enable tag-life.service

echo "Done adding entry to services"
else
echo "Skipping add entry to services"
fi


echo "---- CREATING SYMLINK TO KIVY LOGS ----"
ln -s /home/nsw/.kivy/logs /home/nsw/tag_life/logs

echo '
---- ALL INSTALLED SUCCESSFULLY! ----'
read -r -p "Do you want to reboot now? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
    reboot now
fi
