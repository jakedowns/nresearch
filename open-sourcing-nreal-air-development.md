[![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F769ce0db-81da-4ff4-9ba5-a519b8809d31_682x619.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F769ce0db-81da-4ff4-9ba5-a519b8809d31_682x619.png)

I wanted to share some work I and several other developers have been working on the past several months.

It began with the simple goal of being able to develop MR apps for Nreal Air Glasses, without the official SDK which was/is still (currently) limited to Android and Unity.

Using Nreal’s Official Firmware Update website’s Javascript code we were able to connect to the device over WebHID. We also used Wireshark’s ability to record USB packets from the glasses while tracking was enabled using the Intel version of Nebula for Mac

[![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7b6195eb-c02a-4472-a635-3c114d2f39d2_3024x4032.webp)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7b6195eb-c02a-4472-a635-3c114d2f39d2_3024x4032.webp)

We were working through brute-force decoding of the IMU packets when we were blessed by a partial teardown from Jack Strider and some additional [teardown photos](https://www.reddit.com/r/nreal/comments/10swaz4/comment/j7f3fj2/?utm_source=reddit&utm_medium=web2x&context=3) from NrealAssistant on Reddit which allowed Matt to find the [data sheet](https://invensense.tdk.com/wp-content/uploads/2022/12/DS-000347-ICM-42688-P-v1.7.pdf) for the ICM-42688-P Datasheet High Precision 6-Axis MEMS MotionTrackingTM Device used in the glasses.

From there, Ed got to decoding the packets using the now-confirmed payload values:

\- two sets of three values, gyro with 19 bits and accel with 18 bits,  
\- plus, the scaling to take those signed ints to real units (degrees/sec and g's of accel)

Next up was finding an open-source approach to applying sensor fusion to reduce/eliminate drift in the tracking data.

Now that we could read and clean the tracking data, we just needed to figure out the magic packet to send to the glasses to switch them into AR mode, and initiate tracking.

With some help from Andy, aka Noot, we finally had the magic control packet to initiate AR mode and IMU tracking over usb directly without any first-party libraries!

Then, Matt packaged the work up and released it as a open-source .dll library for Windows developers: [https://github.com/MSmithDev/AirAPI\_Windows](https://github.com/MSmithDev/AirAPI_Windows)

Dan then re-packaged the code as a Mac C++ driver AND built an Objective-C implementation layer allowing developers to use Swift to develop for nreal Air.

[https://github.com/DanBurkhardt/AirAPI\_Windows](https://github.com/DanBurkhardt/AirAPI_Windows)

Amidst this work, Nreal Released their Beta firmware which finally enabled hardware-level toggling to SBS 3d mode (treating the input as one wide-screen display with half the pixels going to the left eye and the remainder going to the right eye) which immediately made a simple, standalone API that much more valuable for developers and end-users.

The coolest part is seeing people making things using the Library!

*   [PhoenixHeadTracker: Nreal Air Head Tracking for Video games](https://www.reddit.com/r/nreal/comments/12ba32a/it_works_nreal_air_heading_tracking_for_video/)
    
*   [WIP Linux Driver](https://gitlab.com/TheJackiMonster/nrealAirLinuxDriver) by Tobias Frisch \[[reddit post](https://www.reddit.com/r/nreal/comments/127laaf/wip_linux_driver_for_the_nreal_air/)\]
    
    [![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdd4cfd30-8b2f-4e6f-af06-fed5e808d2b4_1323x259.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdd4cfd30-8b2f-4e6f-af06-fed5e808d2b4_1323x259.png)
         
    
*   [Kassandra AR for Intel AND M-series macs!](https://twitter.com/HackingAtHome/status/1646373691213725697) by Dan B.
    

* * *

### Progress

Deciphered USB packets for:

1.  AR Mode Toggle (Tracking Init)
    
2.  IMU Packets
    
3.  SBS Mode Toggle \[Coming Soon to library api\]
    
4.  Brightness Control
    
5.  Hardware Button Presses
    

Repackaged as Windows and Mac libraries/apis

### Releases

Matt Smith - [https://msmithdev.com/](https://msmithdev.com/)

1.  Unofficial Firmware Changer: [https://air.msmithdev.com/](https://air.msmithdev.com/)
    
2.  Community Air Adapter Tests: [https://air.msmithdev.com/adapters/](https://air.msmithdev.com/adapters/)
    
3.  Air API Windows (.dll): [https://github.com/MSmithDev/AirAPI\_Windows](https://github.com/MSmithDev/AirAPI_Windows)
    
    1.  wiki: [https://github.com/MSmithDev/AirAPI\_Windows/wiki/Using-with-Unity](https://github.com/MSmithDev/AirAPI_Windows/wiki/Using-with-Unity)
        

* * *

Ed Watt - https://github.com/edwatt

1.  Scripts for Analyzing Packets: [https://github.com/edwatt/nresearch](https://github.com/edwatt/nresearch)
    

* * *

Dan Burkhardt - https://github.com/DanBurkhardt | [Twitter](https://twitter.com/GigabiteDan)

1.  Mac Native Library: https://github.com/DanBurkhardt/AirAPI\_Windows
    
2.  Swift Library: \[Coming Soon!\] Preview post on reddit: https://www.reddit.com/r/nreal/comments/12fa9g0/rd\_update\_this\_is\_a\_fully\_native\_scenekit\_macos/
    

* * *

Andy aka Noot - [https://github.com/abls](https://github.com/abls)

1.  IMU Inspector: https://github.com/abls/imu-inspector
    
2.  OpenGL demo program: [https://github.com/abls/real-air](https://github.com/abls/real-air)
    

### In Progress / Future Goals

1.  Packaging up a neat npm package for javascript developers
    
2.  Putting together a Three.js demo scene with nreal air support
    
3.  WebXR support
    
4.  OpenXR support
