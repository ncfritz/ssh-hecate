#!/bin/sh

if [ "$(id -u)" != "0" ]; then
   echo "Installer must be run as root" 1>&2
   exit 1
fi

SOURCE="$0"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

pip install -r $DIR/requirements.txt > /tmp/hecate-pip.log 2>&1

if [ $? != 0 ]; then
    echo "Failed to install python dependencies" 1>&2
   exit 1
fi

HECATE_ROOT=/usr/local/hecate

if [ -d "$HECATE_ROOT" ]; then
    echo "Cleaning up previous install..."

    rm -rf $HECATE_ROOT/bin > /dev/null 2>&1
    rm -rf $HECATE_ROOT/lib > /dev/null 2>&1
fi

mkdir -p $HECATE_ROOT > /dev/null 2>&1
mkdir -p $HECATE_ROOT/bin > /dev/null 2>&1
mkdir -p $HECATE_ROOT/lib > /dev/null 2>&1
mkdir -p $HECATE_ROOT/etc > /dev/null 2>&1
mkdir -p $HECATE_ROOT/var/output/logs > /dev/null 2>&1

cp $DIR/bin/* $HECATE_ROOT/bin
cp $DIR/lib/* $HECATE_ROOT/lib

if [ ! -f $HECATE_ROOT/etc/supervisord.config ]; then
    cp $DIR/etc/supervisord.config $HECATE_ROOT/etc/supervisord.config
fi

ln -s $HECATE_ROOT/bin/hecate /usr/local/bin/hecate > /dev/null 2>&1
