# LastPass Add-on for Splunk

Collect LastPass data into Splunk via installation onto a Splunk UF or SplunkCloud IDM.

## Overview

This Add-on has been crafted for the appropriate CIM Data Models to correlate this data against your web access logs, for example.

Utilizing the Splunk Add-on Builder, several inputs are designed to collect enterprise account event reporting, user, group, and folder inventory information from LastPass.

## Requirements

You will need the following to collect reporting event data from LastPass:

1. LastPass Enterprise account with admin access

2. LastPass CustomerID

3. Provisioning hash 

4. Index name to store data 

Deploy this TA through either of two effective methods:

- Install locally to server
  1. Transfer tarball to host server. Change ownership/permissions as necessary.
  2. Install locally to Splunk instance using either method:
     - Splunk install CLI: Use `splunk install app <app tarball>`
       - *Note:* requires local account + role permissions to install app
       - Splunk restart: Unpack app tarball into `$SPLUNK_HOME/etc/apps`
         - Validate full ownership of unpacked files for splunk user
         - Restart Splunk instance
- Install using Splunk Web UI
  1. Within Splunk Web UI, navigate to the _Manage Apps_ page and install by file
     - *Note:* there may be upload restrictions or failed uploads depending on environment settings

### Setup

    *Not covered: configuration to forward data to Splunk deployment*

1. Navigate to the *Configuration* page withiin the TA lastpass namespace.

2. Click button for *Create New Input* and select among the following inputs for data collection:

   - Event Reporting

   - User inventory

   - Shared Folder inventory

3. Complete the setup form.

   * Name - label for your input

   * Interval - how often you want to collect? (Recommended: every 60 seconds or minute)

   * Index - Splunk index

   * LastPass API URL - default is already set, but if you have a separate URL, please fill-in

   * Collection Start Time - timestamp for collection. Support backfill and PST is only supported timezone (per vendor documentation, may vary depending on account)


Various CIM Data Models have been mapped to the various event and inventory data. Feel free to consider installing this TA onto both SH and HWF/UFs.


LastPass is a trademark of LastPass. Use of their API is subject to their terms of service.
https://lastpass.com/terms-of-service

Use of their copyright logos and icons is with their publicly posted permission.
See https://lastpass.com/press-room for all information.

## Use Cases

- Monitor user access to shared folders

- Monitor service-level access and changes

- Assess access control for all users per shared folder

## Credits

Henry Canivel
