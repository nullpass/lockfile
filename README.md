Lock-file Management
------------------
* **locker.py** - Locker is a Python class that provides lock-file tools for your Python applications. 
This was based on [Gekitsuu](https://github.com/gekitsuu)'s [Mutex()](https://github.com/gekitsuu/mutex) and has 
expanded over the years to meet my various devops/sysadmin needs.  
* **locker.sh** - A command-line tool to manage lock files for shell scripts.  

Examples and documentation are included in each file.

#### To Do / To Discuss: 
1. Locker.check(): If the contents of self.file cannot be converted to an integer should we overwrite? 
2. Locker.*: Remove exception trapping.
