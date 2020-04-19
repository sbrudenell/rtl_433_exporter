#!/bin/sh

/usr/bin/rtl_433 -F json $RTL_433_ARGS | /usr/local/bin/rtl_433_exporter $EXPORTER_ARGS
