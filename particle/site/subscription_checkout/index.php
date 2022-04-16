<?php
// no matter what happens, we will be redirecting to home page
header("Location: https://particle.church", TRUE, 302);

$result = $_GET["result"];
$checkout_id = $_GET["checkout_id"];

if (!isset($result) || !isset($checkout_id)) die();
if ($result !== "success") $result = "cancel";

require_once("/var/www/particle/PHP/db.php");


if ($result === "success")
{
    $pendingCheckout = dbQuery(
        '
        SELECT
            *
        FROM
            users_pendingcheckout
        WHERE
            checkout_id = "' . dbEscape($checkout_id) . '"
            AND
            TIMESTAMPDIFF(HOUR, CURRENT_TIMESTAMP, time_opened) <= 24
            AND
            time_closed IS NULL
        ;',
        returnFirstRow: true
    );

    dbQuery(
        '
        UPDATE
            users_user
        SET
            time_subscription_form_succeeded = CURRENT_TIMESTAMP
        WHERE
            user_id = ' . intval($pendingCheckout['user_id']) . '
        ;'
    );
}

dbQuery(
    '
    UPDATE
        users_pendingcheckout
    SET
        time_closed = CURRENT_TIMESTAMP,
        result = "' . dbEscape($result) . '"
    WHERE
        checkout_id = "' . dbEscape($checkout_id) . '"
        AND
        TIMESTAMPDIFF(HOUR, CURRENT_TIMESTAMP, time_opened) <= 24
        AND
        time_closed IS NULL
    ;'
);

?>