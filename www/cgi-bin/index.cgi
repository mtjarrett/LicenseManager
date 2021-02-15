#!/usr/bin/perl
use DBI;
use warnings;
use CGI;
use POSIX qw(strftime);


my $connection = DBI->connect('DBI:mysql:database=license_manager;host=localhost', 'root', '');
my $newCGI = new CGI;
my $date = strftime "%F %X", localtime;
my @errorCode = ("","","","");


if ($newCGI->param('updatelicense')) {
	update_license($hardware_serial_number);
}
if ($newCGI->param('addlicense')) {
	add_license($hardware_serial_number);
}
if ($newCGI->param('updatesystem')) {
	update_system($hardware_serial_number);
}


### Html pages
# Begin Html
print $newCGI->header;
print $newCGI->start_html(-title=>"Sample License Manager", -style=>{src=>"/cgi_style.css"});

# Title
print qq[<h1><a href="index.cgi">Sample License Manager</a></h1>];

if ($newCGI->param('editPage')) {
	# Edit page
	edit_page();
}
else {
	# Main Page
	system_table();
}

# End
print $newCGI->end_html;


sub system_table{
	no warnings 'uninitialized';

	# Search query will return from hardware serial numbers and notes
	my $search = $newCGI->param('search');
	my $searchResults = $connection->prepare(qq[SELECT * FROM hardware WHERE (hardware_serial_number LIKE ? OR hardware_note LIKE ?) limit 50]);
	$searchResults->execute("%$search%","%$search%");

	# Search form
	print qq[<form action="index.cgi">
	<input type="text" name="search" placeholder="Search" value="$search">
	<input type="submit" value="Search">
	</form></br>];

	# Begin System table and print column headers
	print qq[<div id="system_table"><div id="tbl-header"><table></thead><tr>
		<th class="system">Hardware S/N</th>
		<th class="platform">Platform</th>
		<th class="added">Added</th>
		<th class="lastEdit">Last Edit</th>
		<th class="editedBy">Edited By</th>
		<th class="notes">Notes</th>
	</tr></thead></table></div><div id="tbl-content"><table><tbody>\n];

	# Retrieve the values returned from executing SQL statement
	while (@data = $searchResults->fetchrow_array()) {
		my $hardware_serial_number = $data[1];
		my $hardware_platform = $data[2];
		my $hardware_note = $data[3];
		my $sys_added = $data[4];
		my $sys_changed = $data[5];
		my $sys_user_id = $data[6];

		# Print table rows
		print qq[<tr>
			<td class="system"><a href="index.cgi?editPage=$hardware_serial_number">$hardware_serial_number</a></td>
			<td class="platform">$hardware_platform</td>
			<td class="added">$sys_added</td>
			<td class="lastEdit">$sys_changed</td>
			<td class="editedBy">$sys_user_id</td>
			<td class="notes">$hardware_note</td>
		</tr>\n];

	}

	# Close table
	print qq[</tbody></table></div></div></br></br>\n];

}

sub edit_page{
	no warnings 'uninitialized';

	my $hardware_serial_number = $newCGI->param('editPage');


### Edit System content ###
	print qq[<h2>You are editing $hardware_serial_number</h2>];

	# Query returns data for selected System to edit
	my $editSystem = $connection->prepare(qq[SELECT * FROM hardware WHERE hardware_serial_number = ?]);
	$editSystem->execute("$hardware_serial_number");

	# Retrieve the values returned from executing SQL statement
	while (@data = $editSystem->fetchrow_array()) {
		our $hardware_id = $data[0];
		our $hardware_serial_number = $data[1];
		our $hardware_platform = $data[2];
		our $hardware_note = $data[3];
		our $sys_added = $data[4];
		our $sys_changed = $data[5];
		our $sys_user_id = $data[6];
	}

	# Edit System content form
	print <<"EOT";
	<span style="color:$errorCode[2]">$errorCode[0]</br><span style="color:$errorCode[3]">$errorCode[1]</span></span></br></br>
	<form id="systemEditor" action="index.cgi" method="POST">
		<input type="hidden" name="updatesystem" value="true">
		<input type="hidden" name="editPage" value="$hardware_serial_number">
		<input type="hidden" name="hardware_id" value="$hardware_id">
		<input type="hidden" name="hardware_serial_number" value="$hardware_serial_number">

		Notes:<textarea name="hardware_note" value="$hardware_note" rows="5" cols="30">$hardware_note</textarea></br></br>
		<input type="submit" value="Update Notes">
	</form></br></br><hr></br>
EOT


### Add license ###
	print qq[<div id="license_table"><form action="index.cgi" method="POST">
		<select name="products">];

		my $availableProducts = $connection->prepare(qq[SELECT service_name, service_code FROM service]);
		$availableProducts->execute();

		while (@data = $availableProducts->fetchrow_array()) {
			our $service_name = $data[0];
			our $service_code = $data[1];
			print qq[<option value="$service_code">$service_code - $service_name</option>];
		}

		print qq[</select>
		<input type="hidden" name="addlicense" value="true">
		<input type="hidden" name="editPage" value="$hardware_serial_number">
		<input type="hidden" name="hardware_id" value="$hardware_id">
		<input type="hidden" name="hardware_serial_number" value="$hardware_serial_number">
		<input type="submit" value="Add License">
	</form></br>];


### Edit Purchased Licenses ###
	# HTML for the beginning of the table
	print qq[<table border="1" width=""> \n];

		# print table column headers
		print qq[<tr>
		<th class="prodName">Product Name</th>
		<th class="licExp">License Expiration</th>
		<th class="licAdded">Added</th>
		<th class="licEdited">Edited</th>
		<th class="licEditedBy">Edited By</th>
		<th class="update">Update</th></tr>\n];

	print qq[</table>\n];

	# search query
	my $table_License = $connection->prepare(qq[SELECT * FROM license INNER JOIN hardware ON license.hardware_id=hardware.hardware_id WHERE hardware.hardware_serial_number=?]);
	$table_License->execute("$hardware_serial_number");

	# retrieve the values returned from executing SQL statement
	while (@data = $table_License->fetchrow_array()) {
		our $license_id = $data[0];
		$service_code = $data[3];
		our $license_expiry_date = $data[1];
		if ($license_expiry_date == NULL){
			$license_expiry_date = "0000-00-00 00:00:00";
		}

		$sys_added = $data[4];
		$sys_changed = $data[5];
		$sys_user_id = $data[6];

		#Display product names instead of code
		my $productName = $connection->prepare(qq[SELECT service_name FROM service INNER JOIN license ON service.service_code=license.service_code WHERE license.service_code=?]);
		$productName->execute("$service_code");

		while (@data = $productName->fetchrow_array()) {
			$service_name = $data[0];
		}

		# print your table rows
		print<<"EOT";
		<form action="index.cgi" method="POST">
			<table border="1" width="">
			<tr>
			<td class="prodName">
				<input type="hidden" name="updatelicense" value="true">
				<input type="hidden" name="editPage" value="$hardware_serial_number">
				<input type="hidden" name="hardware_id" value="$hardware_id">
				<input type="hidden" name="license_id" value="$license_id">$service_code - $service_name
			</td>
			<td class="licExp"><input type="hidden" name="hardware_serial_number" value="$hardware_serial_number"><input type="text" name="licExpiryDate" value="$license_expiry_date"></td>
			<td class="licAdded">$sys_added</td>
			<td class="licEdited">$sys_changed</td>
			<td class="licEditedBy">$sys_user_id</td>
			<td class="update"><input type="submit" value="Update License"></td>
			</tr>
EOT

			# close table
			print qq[</table></form></div>\n];

	}

}

sub add_license{
	my $hardware_id = $newCGI->param('hardware_id');
	my $service_code = $newCGI->param('products');
	my $hardware_serial_number = $newCGI->param('hardware_serial_number');

	#Check if license already exists
	my $addLicenseCheck = $connection->prepare(qq[SELECT service_code FROM license where hardware_id='$hardware_id']);
	$addLicenseCheck->execute();

	while(@row = $addLicenseCheck->fetchrow_array){
		if($service_code == @row[0]){
			$errorCode[0] = "License already exists";
			$errorCode[2] = "red";
			return;
		}
	}

	#Create new license
	my $addLicense = $connection->prepare(qq[INSERT INTO license (service_code, hardware_id, license_added, license_expiry_date, user_id) VALUE (?,?,?,?,?)]);
	if ($addLicense->execute("$service_code", "$hardware_id", "$date", "0000-00-00 00:00:00", "user123")) {
		$errorCode[0] = "License successfully added";
		$errorCode[2] = "green";

		# Update System edit time
		my $updatesystemUpdate = $connection->prepare(qq[UPDATE hardware SET system_changed=?, user_id=? WHERE hardware_id=?]);
		if ($updatesystemUpdate->execute("$date", "user123", "$hardware_id")) {
			$errorCode[1] = "";
		}else{
			$errorCode[1] = "System update time failed to update";
			$errorCode[3] = "red";
		}

	}else{
		$errorCode[0] = "Failed to add license";
		$errorCode[2] = "red";
	}

}

sub update_license{
	#Retrieve parameters from POST
	my $hardware_id = $newCGI->param('hardware_id');
	my $hardware_serial_number = $newCGI->param('hardware_serial_number');
	my $license_id = $newCGI->param('license_id');
	my $license_expiry_date = $newCGI->param('licExpiryDate');

	my $updateLicense = $connection->prepare(qq[UPDATE license SET license_changed=?, license_expiry_date=?, user_id=? WHERE license_id=?]);
	if($updateLicense->execute("$date", "$license_expiry_date", "user123", "$license_id")){
		$errorCode[0] = "License successfully updated";
		$errorCode[2] = "green";

		#Update System edit time
		my $updateLicenseUpdate = $connection->prepare(qq[UPDATE hardware SET system_changed=?, user_id=? WHERE hardware_id=?]);
		if ($updateLicenseUpdate->execute("$date", "user123", "$hardware_id")) {
			$errorCode[1] = "";
		}else{
			$errorCode[1] = "System update time failed to update";
			$errorCode[3] = "red";
		}

	}else{
		$errorCode[0] = "License failed to update";
		$errorCode[2] = "red";
	}

}

sub update_system{
	my $hardware_id = $newCGI->param('hardware_id');
	my $hardware_serial_number = $newCGI->param('hardware_serial_number');
	my $hardware_note = $newCGI->param('hardware_note');

	my $query = qq[UPDATE hardware SET
	hardware_note=?,
	user_id=?
	WHERE hardware_serial_number=?];

	my $updatesystem = $connection->prepare($query);
	if ($updatesystem->execute("$hardware_note", "user123", "$hardware_serial_number")) {
		$errorCode[0] = "System successfully updated";
		$errorCode[2] = "green";

		# Update System edit time
		my $updatesystemUpdate = $connection->prepare(qq[UPDATE hardware SET system_changed=?, user_id=? WHERE hardware_id=?]);
		if ($updatesystemUpdate->execute("$date", "user123", "$hardware_id")) {
			$errorCode[1] = "";
		}else{
			$errorCode[1] = "System update time failed to update";
			$errorCode[3] = "red";
		}

	}else{
		$errorCode[0] = "System failed to update";
		$errorCode[2] = "red";
	}

}