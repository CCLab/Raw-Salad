#!/bin/sh

cd ../../src/rawsalad/site_media/js/
grep -n 'TODO' * | sed 's/\ \ \+/\t/g'
