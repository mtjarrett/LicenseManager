# LicenseManager

## Overview
LicenseManager is a project created while learning Perl. It's purpose is to... manage licenses.
This database interface is designed to run on Linux (developed on CentOS 7) and serves as a frontend for MySQL.

The scenario is that the hardware products have already been added to the database and the LicenseManager is intended to 
be used by Customer Service Representatives to add or remove upgrades to a user's system. Hence, no option to add new hardware systems.

## Setup
Getting the LicenseManager up and running is fairly straight forward but there are several steps that need to be completed:
1. Add the provided files to /var/www with appropriate permissions, likely 755.
1. Setup a new database for testing named license_manager with three tables using the schema found in schema.txt
1. Make a few edits to index.cgi
   1. Edit `my $connection = DBI->connect('DBI:mysql:database=license_manager;host=localhost', 'root', '');` to reflect the needs of your system.
   1. Replace `user123` with a way to capture a username. Originally, `$ENV{'REMOTE_USER'}` was used but, if used on a system without LDAP, breakage can occur.
1. Install Perl modules: DBI, CGI, and POSIX.

That should be everything to get you up and running.
