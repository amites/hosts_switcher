# hosts_switcher

Tools for switching hosts file under linux environment is not easy, though. [Chrome](https://www.google.com/chrome/) has [Hosts Manager](https://chrome.google.com/webstore/detail/hosts-manager/kpfmckjjpabojdhlncnccfhkfhbmnjfi) , [HostAdmin](https://chrome.google.com/webstore/detail/hostadmin/oklkidkfohahankieehkeenbillligdn) and other plug-ins; [Firefox](https://www.mozilla.org/en-US/firefox/new/) below have [HostAdmin](https://github.com/tg123/chrome-hostadmin) , but these plug-ins need to heavily rely on the browser service.


Modify `config.py.simple` to `config.py` need to configure two places:

> HOSTS_BACKUP_FOLDER point to a local folder, we recommend the use of cloud backup the folder, such as [Dropbox](https://www.dropbox.com/home)  or [nuts cloud](https://jianguoyun.com/) .
> 
> Hosts address HOSTS_FILE current server, such as / etc / hosts .


Make sure that the current user HOSTS_FILE have insufficient access rights.
_You can run with `sudo` if needed._

Run the program (supporting python 2.7)

`python hosts_switcher.py`

![Main interface](screenshots/main_window.png)