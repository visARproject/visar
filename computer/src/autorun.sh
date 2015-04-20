# configure the ad-hoc network, will need to be adjusted on each unit
ifconfig wlan1 down
iwconfig wlan1 mode ad-hoc
iwconfig wlan1 essid 'visar'
iwconfig wlan1 key 1234567890
ifconfig wlan1 192.168.1.2

# rotate the display (todo: confirm that this is needed)
DISPLAY=:0.0 xrandr -o left

# Uncomment if program displays on half of the screen, fixes resolution
DISPLAY=:0.0 xrandr --output HDMI-0 --mode 1080x1920 --rate 48.0

# start Voice control program in background (should hopefully be bundled)
(/home/ubuntu/src/python/libVisar/libVisar/visar/audio/vc &)

# start the visar program in fullscreen mode
vsr -f

# shtudown the computer when program exits (disabled for testing)
shutdown -h now
#echo Insert Shutdown Here
