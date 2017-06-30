#!/bin/sh
### BEGIN INIT INFO
# Provides:          ciplushelper
# Required-Start:
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: ciplushelper
# Description:
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin

[ -x /usr/bin/ciplushelper ] || exit 0

case "$1" in
start)
        echo -n "Running ciplushelper..."
        ciplushelper
        echo "done."
        ;;
*)
        ;;
esac

exit 0

