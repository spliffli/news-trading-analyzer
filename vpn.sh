#!/bin/bash

if echo 'ifconfig tun0' | grep -q "00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00"
then
echo "VPN up"
else
echo "VPN down"
fi
exit 0
