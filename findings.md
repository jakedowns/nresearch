# Project Goals:

Document how to interact with Nreal Air Device over WebUSB/WebHID Protocol

### Short-term

 1. [ ] discover how to trigger mode switch between 2d/3d mode from Javascript
 2. [ ] discover how to initiate IMU / Head Tracking polling from Javascript (does this automatically start on mode switch or is it a separate request?)
    - this should be easy to do by synchronizing logs from Unity (Nebula for Mac) + Wireshark
 3. [ ] discover how to write to left eye / right eye over USB (is this possible, or does it need to go over displayport? can we use WebAssembly?)
    - could Lunatic be useful? [View Repo](https://github.com/lunatic-solutions/lunatic)
 4. [ ] discover message id for R_BRIGHTNESS
 5. [ ] discover message id + payload for W_BRIGHTNESS
 6. [x] react to hardware button presses (these are broadcasted over USB and we are able to read them :) )
 6. [ ] document Air Protocol
 7. [ ] document Light Protocol

### Long-term

- [ ] Enable WebXR support for Mac, Windows, Linux?
- [ ] Expose simple API for triggering 3DoF mode, and processing NRFrame packets to pass glasses head-tracking data over usb
 - [ ] expand IMU polling/broadcast to work over bluetooh/LAN using a simple Unity Android apk
 - [ ] test to see if we can use websockets to share IMU data from Android Phone to LAN PC
 
- [ ] re-broadcast head tracking data using the [CemuHook protocol](https://v1993.github.io/cemuhook-protocol/)
  - [ ] ala MotionSource apk: [Read More](https://cemuhook.sshnuke.net/padudpserver.html)
  - [ ] test with Yuzu + Breath of The Wild VR Mode
  
  
> **NOTE** If you start nebula for mac, wait for it to start 3D mode + headtracking, then force-quit the app, then connect this `127.0.0.1:8080` page, you will see the (presumably) IMU data. Just need to figure out how the 64-bytes are packed

Additional Sample Data can be found in this [Google Sheet](https://docs.google.com/spreadsheets/d/1s2V8GXcr92Jpj_znHqIXha3Ikdx1mqmsPuOA7CVHGfY/edit?usp=sharing)




## USB Device Overview (Nreal Air):

| endpointNumber | direction | type        | packetSize |
|----------------|-----------|-------------|------------|
|              3 | out       | isochronous |        192 |
|              2 | in        | isochronous |        104 |
|              4 | in        | interrupt   |         64 |
|              5 | out       | interrupt   |         64 |
|              6 | in        | interrupt   |         64 |
|              7 | out       | interrupt   |         64 |
|              8 | in        | interrupt   |         64 |
|              9 | out       | interrupt   |         64 |

## Known Commands:

todo: document known payloads for each

| MsgID_Decimal | MsgID_Hex | key                           |
|---------------|-----------|-------------------------------|
|            21 | 0x15      | R_GLASSID                     |
|            22 | 0x16      | R_DP7911_FW_VERSION           |
|            24 | 0x18      | R_DSP_VERSION                 |
|            25 | 0x19      | W_CANCEL_ACTIVATION           |
|            30 | 0x1e      | W_SLEEP_TIME                  |
|            38 | 0x26      | R_MCU_APP_FW_VERSION          |
|            41 | 0x29      | R_ACTIVATION_TIME             |
|            42 | 0x2a      | W_ACTIVATION_TIME             |
|            60 | 0x3c      | R_DP7911_FW_IS_UPDATE         |
|            61 | 0x3d      | W_UPDATE_DP                   |
|            62 | 0x3e      | W_UPDATE_MCU_APP_FW_PREPARE   |
|            63 | 0x3f      | W_UPDATE_MCU_APP_FW_START     |
|            64 | 0x40      | W_UPDATE_MCU_APP_FW_TRANSMIT  |
|            65 | 0x41      | W_UPDATE_MCU_APP_FW_FINISH    |
|            66 | 0x42      | W_BOOT_JUMP_TO_APP            |
|            68 | 0x44      | W_MCU_APP_JUMP_TO_BOOT        |
|            69 | 0x45      | W_UPDATE_DSP_APP_FW_PREPARE   |
|            70 | 0x46      | W_UPDATE_DSP_APP_FW_START     |
|            71 | 0x47      | W_UPDATE_DSP_APP_FW_TRANSMIT  |
|            72 | 0x48      | W_UPDATE_DSP_APP_FW_FINISH    |
|          4352 | 0x1100    | W_BOOT_UPDATE_MODE            |
|          4353 | 0x1101    | W_BOOT_UPDATE_CONFIRM         |
|          4354 | 0x1102    | W_BOOT_UPDATE_PREPARE         |
|          4355 | 0x1103    | W_BOOT_UPDATE_START           |
|          4356 | 0x1104    | W_BOOT_UPDATE_TRANSMIT        |
|          4357 | 0x1105    | W_BOOT_UPDATE_FINISH          |
|         27650 | 0x6c02    | P_UKNOWN_HEARTBEAT            |
|         27653 | 0x6c05    | P_BUTTON_PRESSED              |
|         27662 | 0x6c0e    | E_DSP_ONE_PACKGE_WRITE_FINISH |
|         27664 | 0x6c10    | E_DSP_UPDATE_PROGRES          |
|         27665 | 0x6c11    | E_DSP_UPDATE_ENDING           |
|         27666 | 0x6c12    | P_UKNOWN_HEARTBEAT_2          |


payloads:
endpoint 7: URB_INTERRUPT out (completed)
`fd0d2db8c41900a91800002e15400c1a000000000000535a37d3ecba0000`
```
{
	status: 53,
	msgId: 0, 		// should decode to 1a :G
	payload: [0]
}
```

---


## Wireshark USB Packet sniffing:

while connected to of nebula for mac v0.1.0
during usage i captured:


- endpoint 3 fires 2 ISO OUTs:

  1. (completed) is 14120 bytes: 64 frames of 192 bytes
	several of the frames are mostly 0s

  2. (submitted) is 1832 bytes: 64 frames of 
	{frame_number, frame_length}



- endpoint 2 repeatedly fires 2 packets: (every... 2ms?)

	1. (completed) is 288 bytes: 2 frames of 
		{frame_number, byte_length, frame_timestamp, frame_status, data}

	2. (submitted) is 96 bytes: 2 frames of
		{frame_number, byte_length}


i'm assuming OUT is the video of the screencapture
and IN is the imu sensor of the head position

1. figure out how to decode them
2. figure out how to send them

the OUTs seem like ALL zeros :G ...
so, the mac app probably is just piping unity camera straight over Apple's api for the display,
rather than feeding it over the wire manually?

If i force quit the app, sometimes the device continues to fire what i can only assume are imu tracking data packets

it's endpoint 3, they're URB_ISOCHRONOUS out packets, and they're 14120 bytes long
only this time, the 64 frames (192 bytes each) are NOT full of zeros

if i unplug the device and reconnect, they cease

i'm going to run some analysis and get the min-max,avg of each of the data frames

^ this is in wireshark, meanwhile in chrome:
i'm getting messageId 0 packets, 64 bytes long,

[here is a spreadsheet with raw captured packets](https://docs.google.com/spreadsheets/d/1s2V8GXcr92Jpj_znHqIXha3Ikdx1mqmsPuOA7CVHGfY/edit#gid=1078527089)

in [NativeHMD.cs@GetDevicePoseFromHead](https://github.com/nreal-ai/NRSDK-MRTK-Samples/blob/08c8ea1c5a7ea176ccf4f8b56bebe243b1e44627/Assets/NRSDK/Scripts/Interfaces/Wrappers/NativeHMD.cs#L69-L79) we see that the API returns a NativeMat4 (4x4 Float Matrix) 

Now we just need to figure out how to extract 16 floats from that 64-byte packet. I'm not sure how they're packed. Or whether or not they're encoded in any way (i assume not since this data needs to be available within microseconds) 

> 4x4f Matrix
> | Float Type | Bits | Bytes | Format | Total Size|
> |---|---|---|---|---|
> | Half | 16-bit | 2-bytes | 1 5 10 | 4x4f matrix = 32 bytes maybe|
> | Single | 32-bit | 4-bytes | 1 8 23 | 4x4f matrix = 64 bytes maybe |
> | Double | 64-bit | 8-bytes | 1 11 52 | 4x4f matrix = 128 bytes nope, wouldn't fit, unless it spans multiple packets/frames? |

Alternatively, they could be just sending a 3x3 rotational matrix for 3Dof mode, and just padding out the 4th row/column?

<img width="889" alt="image" src="https://user-images.githubusercontent.com/1683122/204916690-76b28fb6-65ba-4175-9f27-b58fd261825b.png">

