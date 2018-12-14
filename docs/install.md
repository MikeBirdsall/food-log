# Installation

## New Installation for proper basic-auth authentication

This new version of the package is intended to have three directories for the
project executables:
* Dieter:    directory under webroot with basic auth for executable and static menus.  
* Dietitian: directory under webroot optionally without basic auth
* &lt;execs&gt;:   directory outside webroot and in python sys.path 


* In addition there will be a number of locations for data:
  - &lt;staging&gt;:  Directory to download the project. This can be temporary
  - &lt;cfg&gt;:      Configuration file directory.  The configuration file is
                currently planned to be in the data directory determined by
                appdirs.user_data_dir, but I will probably plan some fallback.
  - &lt;archive&gt;:  Directory where original images will be stored
  - &lt;db-file&gt;:  Database file (end with .sqlite)
  - &lt;log-file&gt;: File with sqlite commands to recreate database file.
  - &lt;thumbs&gt;:       Directory where thumbnail images will be stored

* Determine the relative URLs for some of those:
  &lt;Uthumbs&gt; for &lt;thumbs&gt;

* Add .htaccess directives to prevent any Indexing or other options from thise directories

* Download the project from github
  git clone https://github.com/MikeBirdsall/food-log.git &lt;staging-area&gt;

* Create the configuration file paths if they don't exist.
  - `cp &lt;staging-area&gt;foodlog/foodlog.template &lt;cfg&gt;/foodlog.cfg`
  - Edit &lt;cfg&gt;/foodlog.cfg and fill in or complete:

```
THUMB_URL = <Uthumbs>
THUMB_DIR = <thumbs> ; TODO Figure out from THUMB_URL and DOCUMENT_ROOT
ARCHIVE_DIR = <archive>
DB_FILE = <db-file>
DB_LOG = <log-file>
```

  
* Copy the executables 
```
cp <staging-area>/foodlog/*.py <execs>/foodlog
cp <staging-area>/foodlog/run.py <Dieter>
cp <staging-area>/foodlog/run.py <Dietitian>
```
  
* create, update and copy the index.html files

```
cp <staging-area>/html/editpages/index.html <Dieter>
cp <staging-area>/html/viewpages/index.html <Dietitian>
```

* Create the original database and log file

```
cp <staging-area>/tables.sql <execs>/tables.sql
python create_db.py
```
   This is currently still python2.
   I need to supply an empty database and history file to replace this step.

## Old Installation

The project has to be installed into a host running a web server, with the
files set up properly for the particular web server.

I haven't automated it, and in fact I don't know enough about different web
server setups to do that. This file is currently a record of how I install
a new instance on my web server, trying to keep it as generic as I can.

* Determine a number of directories and file paths you need to run the project
  - &lt;staging-area&gt;: Directory to download the project. This can be temporary
  - &lt;execs&gt;:        Directory for cgi-bin executables for this app
  - &lt;archive&gt;:      Directory where original images will be stored
  - &lt;db-file&gt;:      Database file (end with .sqlite)
  - &lt;log-file&gt;:     File with sqlite commands to recreate database file.
  - The following have to be in directories where URLs can be served up
      + &lt;thumbs&gt;:       Directory where thumbnail images will be stored
      + &lt;editpages&gt;:    Directory for html report pages that allow editing
      + &lt;viewpages&gt;:    Directory for html report pages that don't allow editing

* Create the directories, if they don't already exist

* Determine the relative URLs for some of those:
  &lt;Uthumbs&gt; for &lt;thumbs&gt;
  &lt;Ueditpages&gt; for &lt;editpages&gt;
  &lt;Uviewpages&gt; for &lt;viewpages&gt;

* Add .htaccess directives to prevent any Indexing or other options from thise directories
  
* Download the project from github
  git clone https://github.com/MikeBirdsall/food-log.git &lt;staging-area&gt;

* Create the configuration file
  cp &lt;staging-area&gt;foodlog/foodlog.template &lt;execs&gt;/foodlog.cfg
  Edit &lt;execs&gt;/foodlog.cfg and fill in or complete
  THUMB_DIR &lt;thumbs&gt;
  THUMB_URL &lt;Uthumbs&gt;
  ARCHIVE_DIR &lt;archive&gt;
  DB_FILE &lt;db-file&gt;
  DB_LOG &lt;log-file&gt;
  MENU_URL &lt;Ueditpages&gt;
  VIEW_MENU_URL &lt;Uviewpages&gt;
  
* Copy the executables 
  cp &lt;staging-area&gt;/foodlog/*.py &lt;execs&gt;
  
* create, update and copy the index.html files
  update the pages to point to the right place
  cp &lt;staging-area&gt;/html/editpages/index.html &lt;editpages&gt;
  cp &lt;staging-area&gt;/html/viewpages/index.html &lt;viewpages&gt;

* Create the original database and log file
  cp &lt;staging-area&gt;/tables.sql &lt;execs&gt;/tables.sql
  python create_db.py
   This is currently still python2.
   I need to supply an empty database and history file to replace this step.

