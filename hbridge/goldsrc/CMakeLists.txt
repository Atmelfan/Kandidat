CMAKE_MINIMUM_REQUIRED(VERSION 2.8.4)
SET(CMAKE_SYSTEM_NAME Generic)

#============================================================================================
PROJECT(avr-clion)

ADD_DEFINITIONS(-DARCH=XMEGA)
ADD_DEFINITIONS(-DF_USB=48000000)
ADD_DEFINITIONS(-DVID=9999)
ADD_DEFINITIONS(-DPID=ffff)



SET(DEVICE "atxmega32a4u")
SET(FREQ "32000000")

#============================================================================================

add_definitions(-DARCH=ARCH_XMEGA)
add_definitions(-DBOARD=USER)
add_definitions(-DF_USB=48000000)


include_directories(./)

include_directories(LUFA/Drivers)
include_directories(LUFA/Drivers/Board)
include_directories(LUFA/USB)



include_directories(Config)


SET(CMAKE_C_COMPILER avr-gcc)
SET(CMAKE_CXX_COMPILER avr-g++)

SET(CMAKE_C_FLAGS  "-Os -mmcu=${DEVICE} -DF_CPU=${FREQ}UL -DUSE_LUFA_CONFIG_HEADER -IConfig/ -D ARCH=ARCH_XMEGA -std=gnu99 -Wl,--gc-sections -ffunction-sections")
SET(CMAKE_CXX_FLAGS "-Os -mmcu=${DEVICE} -DF_CPU=${FREQ}UL -Wl,--gc-sections")

set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin")


#============================================================================================

set(USB_SRC_FILES
        #common
        LUFA/Drivers/USB/Core/XMEGA/USBController_XMEGA.c   
        LUFA/Drivers/USB/Core/XMEGA/USBInterrupt_XMEGA.c    
        LUFA/Drivers/USB/Core/ConfigDescriptors.c               
        LUFA/Drivers/USB/Core/Events.c                          
        LUFA/Drivers/USB/Core/USBTask.c                         
        LUFA/Drivers/USB/Class/Common/HIDParser.c   
        #host
        LUFA/Drivers/USB/Core/XMEGA/Host_XMEGA.c            
        LUFA/Drivers/USB/Core/XMEGA/Pipe_XMEGA.c            
        LUFA/Drivers/USB/Core/XMEGA/PipeStream_XMEGA.c      
        LUFA/Drivers/USB/Core/HostStandardReq.c                 
        #device
        LUFA/Drivers/USB/Core/XMEGA/Device_XMEGA.c          
        LUFA/Drivers/USB/Core/XMEGA/Endpoint_XMEGA.c       
        LUFA/Drivers/USB/Core/XMEGA/EndpointStream_XMEGA.c  
        LUFA/Drivers/USB/Core/DeviceStandardReq.c    
        #hostclass
        LUFA/Drivers/USB/Class/Device/AudioClassDevice.c        
        LUFA/Drivers/USB/Class/Device/CDCClassDevice.c          
        LUFA/Drivers/USB/Class/Device/HIDClassDevice.c          
        LUFA/Drivers/USB/Class/Device/MassStorageClassDevice.c  
        LUFA/Drivers/USB/Class/Device/MIDIClassDevice.c         
        LUFA/Drivers/USB/Class/Device/PrinterClassDevice.c      
        LUFA/Drivers/USB/Class/Device/RNDISClassDevice.c        
        #deviceclass
        LUFA/Drivers/USB/Class/Host/AndroidAccessoryClassHost.c
        LUFA/Drivers/USB/Class/Host/AudioClassHost.c
        LUFA/Drivers/USB/Class/Host/CDCClassHost.c
        LUFA/Drivers/USB/Class/Host/HIDClassHost.c
        LUFA/Drivers/USB/Class/Host/MassStorageClassHost.c
        LUFA/Drivers/USB/Class/Host/MIDIClassHost.c
        LUFA/Drivers/USB/Class/Host/PrinterClassHost.c
        LUFA/Drivers/USB/Class/Host/RNDISClassHost.c
        LUFA/Drivers/USB/Class/Host/StillImageClassHost.c
        )

set(SOURCE_FILES
            VirtualSerial.c
            Descriptors.c

            ${USB_SRC_FILES}
        )

#============================================================================================

ADD_EXECUTABLE(${PROJECT_NAME} ${SOURCE_FILES})

ADD_CUSTOM_COMMAND(TARGET ${PROJECT_NAME} POST_BUILD COMMAND avr-objcopy -O ihex -R.eeprom ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME}.hex)

ADD_CUSTOM_COMMAND(TARGET ${PROJECT_NAME} POST_BUILD COMMAND avr-objcopy -O ihex -j .eeprom --set-section-flags=.eeprom="alloc,load"  --change-section-lma .eeprom=0 ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME}.eep)

ADD_CUSTOM_COMMAND(TARGET ${PROJECT_NAME} POST_BUILD COMMAND avr-size ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME} --mcu=${DEVICE} --format=avr)

