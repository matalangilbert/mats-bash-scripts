#!/bin/bash
if [ $# -lt 1 ] ; then
  echo "supply application name as first argument"
  exit -1
fi
application_path="Documents/RailsApps/$1"
gnome-terminal --tab --title="Redcar" -e "sh -c 'command ~/Documents/Scripts/start_redcar.sh ~/$application_path'" --tab --working-directory=$application_path --title="Server" --command "rails s" --tab --working-directory=$application_path --title="Spork" --command "bundle exec spork" --tab --working-directory=$application_path --title="Autotest" --command "autotest" --tab --working-directory=$application_path --title="Rails" 
