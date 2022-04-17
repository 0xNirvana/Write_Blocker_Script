# Write Blocker For Host Based Forensics Project

### Initial setup - Patching
* Add couple of lines to the rules file

### Blocking a flash drive steps
1. Stopping automount service
2. Identifying the USB drive insertion
3. Mounting USB drive
4. Blocking through
	* blockdev
	* mount ro (Command in task 3 would change)

### TBD (If we have time and is feasible)
* Monitor kernel level instructions (To verify if it's working/corner cases)
* Block SCSI instructions
