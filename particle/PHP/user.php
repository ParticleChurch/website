<?php

$user = NULL;
class User {
    public $user_id = NULL;
    public $email = NULL;
    public $password_hash = NULL;
    public $time_registered = NULL;
    public $is_subscribed = NULL;
    public $subscription_period_end = NULL;

    public function __construct($user_id, $email, $password_hash, $time_registered, $is_subscribed, $subscription_period_end)
    {
        $this->user_id = $user_id;
        $this->email = $email;
        $this->password_hash = $password_hash;
        $this->time_registered = $time_registered;
        $this->is_subscribed = $is_subscribed;
        $this->subscription_period_end = $subscription_period_end;
    }
}

if (isset($_COOKIE["session_id"]))
{
    $sid = $_COOKIE["session_id"];
    
    require_once("/var/www/particle/PHP/db.php");
    $sessionData = dbQuery('
        SELECT
            *
        FROM
            particle_sessions_particlesession
        WHERE
            session_id = "'.dbEscape($sid).'"
            AND
            ISNULL(time_closed)
            AND
            TIMESTAMPDIFF(DAY, CURRENT_TIMESTAMP, time_opened) < 14
        ;
    ', returnFirstRow: true);
    
    if ($sessionData && isset($sessionData["user_id"]) && is_numeric($sessionData["user_id"]))
    {
        $user_id = intval($sessionData["user_id"]);
        $userData = dbQuery('
            SELECT
                *,
                UNIX_TIMESTAMP(time_registered) as time_registered_unix,
                UNIX_TIMESTAMP(subscription_period_end) as subscription_period_end_unix,
                (
                    (
                        time_subscription_form_succeeded IS NOT NULL
                        AND
                        TIMESTAMPDIFF(MINUTE, time_subscription_form_succeeded, CURRENT_TIMESTAMP) <= 2
                    )
                    OR
                    subscription_status IN ("active")
                ) 
                AND
                (
                    subscription_period_end IS NULL
                    OR
                    TIMESTAMPDIFF(HOUR, subscription_period_end, CURRENT_TIMESTAMP) <= 48
                )
                as is_subscribed
            FROM
                users_user
            WHERE
                user_id = '.$user_id .'
            ;
        ', returnFirstRow: true);
        
        if ($userData)
        {
            $user = new User(
                user_id: $userData["user_id"],
                email: $userData["email"],
                password_hash: $userData["password_hash"],
                time_registered: $userData["time_registered_unix"],
                is_subscribed: !!$userData["is_subscribed"],
                subscription_period_end: $userData["subscription_period_end_unix"],
            );
        }
    }
}

?>