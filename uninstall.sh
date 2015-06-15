#!/bin/bash
# ffmulticonverter uninstall script

for i in $(find /usr -path "*ffmulticonverter*"); do
	rm -rf $i
done
