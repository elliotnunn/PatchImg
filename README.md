PatchImg
========
This script is intended to modify the Patch Partition in an Apple Partition Map-based disk image. The Classic Mac ROM would run the 68k code in this partition before booting the system, in order to fix ROM bugs or add features.

So far PatchImg just dumps the metadata from the Patch Partition.

More Info
---------
<https://www.fenestrated.net/mirrors/Apple%20Technotes%20(As%20of%202002)/tn/tn1189.html>

Usage
-----
	PatchImg.py diskimage.iso
