# food-log

A web based food-consumption logging system which allows a dieter to add
minimal input at the time they eat, enough to remind them and let them fill
in more later. It is designed to run on minimal web hosts.

## Getting Started

You can, of course, pull the source and configure it on your own web-server 
and use it. But if you don't want to go through that much work for an initial
look at it, I've placed a working copy you can share with anyone else who wants
to try it out.

There are two top level URLs to use:

Dietitian View: https://kirkbird.com/guestfoodlog/viewpages

Dieter View:    https://kirkbird.com/guestfoodlog/editpages 
[User Name:guest Password:guest]

For more information about navigating and using the application,
check out [Using the program](docs/Manual.md)

### Prerequisites

The program requires a web server which can serve up python cgi-bin produced 
pages, currently using and tested under Python 2.7.7. It uses these python
modules out of the standard library: argparse, cgi, cgitb, collections, 
ConfigParser, datetime, glob, operator, os, sys, sqlite3, tempfile.
It also requires the Python Imaging Module from Pillow.

### Installing
Follow the installation instructions in [Installation](docs/install.txt)

## Tests
There is not currently a set of automated tests for the software.

## Motivation and Philosophy

I've tried a number of online diet food logging systems, and I had pretty much 
the same problems with each of them. They each required too much information 
from me at the point where I was ready to eat. Often when I was entering
the data on my cellphone. And I'm not an expert at entering data on my phone.
Often I was at a restaurant with friends. Socializing.  I don't want to search 
around the web for nutrition information of the food at that point.  

I'm also hosting my websites on a shared host, where I don't have root access,
or control of the web server, or much control over the environment. So any
solution had to be able to work within a fairly limited environment.

### Solution
The solution that I decided on was based on the idea that a photo is a rich 
reminder for me of what I have eaten, and that a photo is always available 
when I have my smartphone with me. 
It can be a photo of the food, a nutrition label or a description on a menu. 
Or anything else that is a good reminder.

The guiding philosophy behind this food-logging system is to allow the minimal 
interaction at the meal or snack. It servers as a reminder to allow me to fill 
in more information at my leisure.


