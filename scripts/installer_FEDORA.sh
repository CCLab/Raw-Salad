#!/bin/sh

# Get the jQuery and move it to libraries folder
wget http://code.jquery.com/jquery-1.5.min.js
mv ./jquery-1.5.min.js ../src/libs/javascript/

# Get the ProtoVis and move it to libraries folder
wget http://protovis-js.googlecode.com/files/protovis-3.2.zip
unzip protovis-3.2.zip
mv ./protovis-3.2/protovis-r3.2.js ../src/libs/javascript/
rm -r protovis-3.2.zip __MACOSX/ protovis-3.2/

# Install all the dependecies with yum
su -c 'yum install mongodb mongodb-server python pymongo python-simplejson Django'
