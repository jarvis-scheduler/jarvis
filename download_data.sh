#!/usr/bin/env bash
curl -sL https://github.com/jarvis-scheduler/data/archive/master.zip > data.zip
unzip data.zip
mv data-master data
rm data.zip