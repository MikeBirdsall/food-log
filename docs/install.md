# Installation

The project has to be installed into a host running a web server, with the
files set up properly for the particular web server.

I haven't automated it, and in fact I don't know enough about different web
server setups to do that. This file is currently a record of how I install
a new instance on my web server, trying to keep it as generic as I can.

* Determine a number of directories and file paths you need to run the project
  <staging-area>: Directory to download the project. This can be temporary
  <execs>:        Directory for cgi-bin executables for this app
  <archive>:      Directory where original images will be stored
  <db-file>:      Database file (end with .sqlite)
  <log-file>:     File with sqlite commands to recreate database file.
  - The following have to be in directories where URLs can be served up
  <thumbs>:       Directory where thumbnail images will be stored
  <editpages>:    Directory for html report pages that allow editing
  <viewpages>:    Directory for html report pages that don't allow editing

* Create the directories, if they don't already exist



* Determine the relative URLs for some of those:
  <Uthumbs> for <thumbs>
  <Ueditpages> for <editpages>
  <Uviewpages> for <viewpages>
* Add .htaccess directives to prevent any Indexing or other options from thise directories
  
* Download the project from github
  git clone https://github.com/MikeBirdsall/food-log.git <staging-area>

* Create the configuration file
  cp <staging-area>foodlog/foodlog.template <execs>/foodlog.cfg
  Edit <execs>/foodlog.cfg and fill in or complete
  THUMB_DIR <thumbs>
  THUMB_URL <Uthumbs>
  ARCHIVE_DIR <archive>
  DB_FILE <db-file>
  DB_LOG <log-file>
  MENU_URL <Ueditpages>
  VIEW_MENU_URL <Uviewpages>
  
* Copy the executables 
  cp <staging-area>/foodlog/*.py <execs>
  
* create, update and copy the index.html files
  update the pages to point to the right place
  cp <staging-area>/html/editpages/index.html <editpages>
  cp <staging-area>/html/viewpages/index.html <viewpages>

* Create the original database and log file
  cp <staging-area>/tables.sql <execs>/tables.sql
  python create_db.py
   This is currently still python2.
   I need to supply an empty database and history file to replace this step.
