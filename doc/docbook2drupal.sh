#!/bin/bash

# quick and dirty - might break anytime if docbook html output changes
function docbook_html_to_drupal () {
    title=$1; shift
    html=$1; shift
    php=$1; shift

    mkdir -p $(dirname $php)
    if [ ! -f $html ] ; then
	cat << __header_no_doc__ > $php
<?php
require_once 'plc_drupal.php';
drupal_set_title("$title - unavailable");
?>
<p class='plc-warning'> Build-time error - could not locate documentation $html</p>
__header_no_doc__
    else
	# insert header, makes sure we have a trailing eol
	(cat << __header_doc__ ; cat $html ) > $php
<?php
require_once 'plc_drupal.php';
drupal_set_title("$title");
?>
__header_doc__
	# ignore ed return status
	set +e
	# cuts off around the <body> </body>
	# preserves the 4 first lines that we just added as a header
	ed -s $php << __ed_script__
/BODY/
/>/
s,><,<,
5,-d
$
?/BODY?
s,><.*,>,
+
;d
w
q
__ed_script__
	set -e
    fi
}   

docbook_html_to_drupal "$@"
