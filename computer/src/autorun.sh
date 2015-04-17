# configure the ad-hoc network, will need to be adjusted on each unit
#ifconfig wlan0 down
#iwconfig wlan0 mode ad-hoc
#iwconfig wlan0 essid 'visar'
#iwconfig wlan0 key 1234567890
#ifconfig wlan0 192.168.1.1

# rotate the display (todo: confirm that this is needed)
# DISPLAY=:0.0 xrandr -o left

# program the FPGA's distoriton data
#make -C fpga_scripts/ program

# start Voice control program in background (should hopefully be bundled)
#(/home/ubuntu/src/python/libVisar/libVisar/visar/audio/vc &)

# start the visar program in fullscreen mode
vsr -f

# shtudown the computer when program exits (disabled for testing)
#shutdown -h now
echo Insert Shutdown Here
