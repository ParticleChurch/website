<?php
function dieWithError($message)
{
    error_log($message);
    http_response_code(500);
    die(); 
}

$dbLink = mysqli_connect("localhost", "ParticlePHPSite", "G6nxCFf5HdcWHdf3v26uMZzyLGvvCMqa");
if (!$dbLink) dieWithError("[" . mysqli_connect_errno() . "] " . mysqli_connect_error());
if (!mysqli_select_db($dbLink, "particle_church")) dieWithError("[" . mysqli_errno($dbLink) . "] " . mysqli_error($dbLink));

// shortcuts to common functions
function dbErrno()
{
	global $dbLink;
	return mysqli_errno($dbLink);
}

function dbError()
{
	global $dbLink;
	return mysqli_error($dbLink);
}

function dbEscape($s)
{
	global $dbLink;
	return mysqli_real_escape_string($dbLink, strval($s));
}

function dbFormatError()
{
	return sprintf("[%d]: %s", dbErrno(), dbError());
}

function dbInfo()
{
	global $dbLink;
	return mysqli_info($dbLink);
}

function dbUpdateInfo()
{
	return sscanf(dbInfo(), "Rows matched: %d Changed: %d Warnings: %d");
}

function dbQuery($sql, $mustHaveResult = false, $returnFirstRow = false, $strict = true)
{
	global $dbLink;
	$result = mysqli_query($dbLink, $sql);
	
	if ($strict && dbErrno() !== 0) dieWithError(dbFormatError());
	
	if ($mustHaveResult && (!$result || mysqli_num_rows($result) < 1)) dieWithError("[in dbQuery()] Required to find a result, but none was found.");
	
	if ($returnFirstRow && $result && mysqli_num_rows($result) >= 1)
		return mysqli_fetch_assoc($result);
	elseif ($returnFirstRow)
		return NULL;
	
	return $result;
}

function dbAutocommit($mode, $strict = true)
{
	global $dbLink;
	$result = mysqli_autocommit($dbLink, $mode);
	
	if ($result !== true && $strict)
		dieWithError("Error while setting autocommit = " . strval($mode) . ": " . dbFormatError());
	
	return $result;
}

function dbCommit($strict = true)
{
	global $dbLink;
	$result = mysqli_commit($dbLink);
	
	if ($result !== true && $strict)
		dieWithError("Error while committing: " . dbFormatError());
	
	return $result;
}
?>