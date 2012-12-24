# ffmulticonverter uninstall script

sudo find /usr -path "*ffmulticonverter*" > files.txt
sudo cat files.txt | sudo xargs rm -rf
rm files.txt

# uncomment if you wish to remove configuration files as well
# rm -rf ~/.config/ffmulticonverter
