# Wintab32
Basic Python wrapper for Wintab library.
It allows reading the packets from a tablet device that supports wintab library.

---

## Usage
The fastest way to start polling the tablet for packets is calling the functions:
1) getTabletInfo(), in order to verify a tablet is connected
2) OpenTabletContexts(), to create a tablet context
3) GetPackets(), to retrieve the packets from the tablet.

You can control the information the tablet returns for each packet by editing *PACKETDATA*,  
but don't forget to add the matching fields to the *PACKET* structure. Use *FULLPACKET* as a reference.

The wrapper contains a working example using a PyQt5 window. 

---
[The Wintab API documentation](https://developer-docs-legacy.wacom.com/display/DevDocs/Windows+Wintab+Documentation) is useful for expanding the usage.  
I used [Scribble Demo](https://developer-docs-legacy.wacom.com/display/DevDocs/Wintab+Sample+Code+Downloads) for a reference when writing the wrapper.

Enjoy.


