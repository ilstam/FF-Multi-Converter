#!/bin/sh
# ffmulticonverter uninstall script
# Usage: ./uninstall [--all]

for i in $(sudo find /usr -path "*ffmulticonverter*")
do
	sudo rm -rf $i
done

if [[ "$#" -eq 1 && "$1" = "--all" ]]; then
	# remove configuration files as well
	rm -rf ~/.config/ffmulticonverter
fi
