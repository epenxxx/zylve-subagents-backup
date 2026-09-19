#!/bin/bash
cp /etc/wireguard/vpnbook.conf /etc/wireguard/wg0.conf
echo 'Address = 10.104.7.232/32' >> /etc/wireguard/wg0.conf
echo 'DNS = 1.1.1.1, 8.8.8.8' >> /etc/wireguard/wg0.conf
wg-quick up wg0