#first step :

	#DFU tool for ReSpeaker Microphone Array
	#For ReSpeaker USB Mic Array - Far-field w/ 7 PDM Microphones. 
	#Change the Mic Array's firmware to get 8 channels raw audio. 
	#See https://github.com/respeaker/mic_array_dfu
	#On linux
		sudo apt-get install libusb-1.0-0-dev 
		git clone https://github.com/respeaker/mic_array_dfu.git
		cd mic_array_dfu
		make
		sudo ./dfu --download respeaker_mic_array_8ch_raw.bin

#Second step :
	
	
	
