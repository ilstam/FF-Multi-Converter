#!/bin/sh
# ffmulticonverter uninstall script

for i in $(sudo find /usr -path "*ffmulticonverter*")
do
	sudo rm -rf $i
done

# uncomment if you wish to remove configuration files as well
# rm -rf ~/.config/ffmulticonverter
