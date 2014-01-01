#!/bin/bash
# sends an email when external IP changes

cd /home/fft/mats-bash-scripts/ipchange/

# Put email address in email.txt
read EMAIL < email.txt

touch old_ip.dat

curl -s ifconfig.me > curr_ip.dat

read CURR < curr_ip.dat
read OLD < old_ip.dat

if [ "$CURR" = "$OLD" ]; then
    echo "`date` -- ip change script -- IP hasn't changed: $CURR -- doing \
nothing" | xargs -0 logger 
else
    echo "`date` -- ip change script -- New IP is: $CURR. Sending email" | \
        xargs -0 logger
    echo "`date` -- ip change script -- New Raspberry Pi IP is: $CURR" > temp
    mail -s "Raspberry Pi external IP has changed" $EMAIL < temp
fi

rm -f old_ip.dat temp
mv curr_ip.dat old_ip.dat


