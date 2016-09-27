nukeToolkit
===========
- This is a repository of nuke tools collected from the internet that have an open commercial licence. (many from Nukepedia)
- Code must include : author name; dateCreated; source link; licence link.
- All nodes/code has no dependencies outside this toolkit folder. So when a script is opened in nuke in a different enviroment it will still work. (i.e. on a different machienes or the farm)
- All code has been checked for bad channels, malicious intent and privacy invasion. (lots of nuke code on the web has bad channels and on some render farm software this error out the render)
- There is a loader UI that loads all the tools inside nuke from this web repository or from local disk.

instructions for loading inside nuke
===========
Copy and paste into Nuke Script Editor and click run:

```import urllib2; exec urllib2.urlopen("https://raw.githubusercontent.com/openNuke/toolset/master/_load.py").read()```

docs
==========
http://opennuke.github.io/


licence
===========
By downloading a file from this repository you agree to the general license terms below.
Copyright (c) 2010 till present
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Nukepedia nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS / OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
