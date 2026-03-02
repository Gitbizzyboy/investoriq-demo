#!/bin/bash
echo "Searching for all uses of 'index' variable in map.html..."
grep -n "index" business/property-finder/platform/templates/map.html | grep -v "indexOf" | grep -v "z-index" | grep -v "data-index"