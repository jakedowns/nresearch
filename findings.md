# Project Goals:

Document how to interact with Nreal Air Device over WebUSB/WebHID Protocol

### Short-term

 1. discover how to toggle 2d/3d mode from Javascript
 2. discover how to write to left eye / right eye
 3. discover how to read brightness
 4. discover how to set brightness
 5. document Air Protocol
 6. document Light Protocol

### Long-term

- SBS/OU 3D video playback

- Enable WebXR support for Mac, Windows, Linux?
 - 3DoF head-tracking




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

If i quit the app, sometimes the device continues to fire what i can only assume are imu tracking data packets


it's endpoint 3, they're URB_ISOCHRONOUS out packets, and they're 14120 bytes long
only this time, the 64 frames (192 bytes each) are NOT full of zeros

if i unplug the device and reconnect, they cease

i'm going to run some analysis and get the min-max,avg of each of the data frames

^ this is in wireshark, meanwhile in chrome:
i'm getting messageId 0 packets, 41 bytes long (4x4f Matrix?)
they have different Status bytes... a wide distribution ranging from 0-255

![](https://cdn-std.droplr.net/files/acc_77710/QWmk25)

we also have non-41 byte packets coming in as well (same message id)

![](https://cdn-std.droplr.net/files/acc_77710/bfEC8V)

sample distribution:

```
{
  "len": {
    "4": 8,
    "5": 5,
    "6": 6,
    "14": 14,
    "16": 32,
    "22": 22,
    "24": 24,
    "25": 25,
    "33": 66,
    "34": 68
  },
  "status": {
    "15": 22,
    "19": 5,
    "36": 33,
    "46": 34,
    "53": 4,
    "151": 25,
    "220": 6,
    "229": 33,
    "230": 24,
    "235": 16,
    "240": 16,
    "243": 4,
    "245": 14,
    "253": 34
  }
}
```






