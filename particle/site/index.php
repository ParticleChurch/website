<?php
require_once("/var/www/particle/PHP/user.php");
?>

<html>
    <?php
    require_once('/var/www/particle/PHP/head.php');
    require_once('/var/www/particle/PHP/header.php');
    ?>

    <body class="theme-g3-bg theme-w1-fg">
        <div id="video-container">
            <video autoplay muted loop playsinline preload="auto" id="bruh-some-browsers-dont-autoplay">
                <source src="IMG/reel.mp4" type="video/mp4" />
            </video> <script> document.getElementById("bruh-some-browsers-dont-autoplay").play(); </script>
        </div>
        <div id="overlays">
            <div id="account-modal">
                <div class="theme-g2-bg" id="login-form" <?php if ($user) echo('style="display:none;"'); ?>>
                    <h2 class="hugged">Email</h2>
                    <div class="hspacer-xsmall"></div>
                    <input class="input theme-g3-bg theme-w2-fg" name="email" type="email" autocomplete="email" id="login-email" placeholder="example@particle.church"></input>
                    
                    <div class="hspacer-large"></div>
                    
                    <h2 class="hugged">Password</h2>
                    <div class="hspacer-xsmall"></div>
                    <input class="input theme-g3-bg theme-w2-fg" name="password" type="password" autocomplete="password" id="login-password" placeholder="Password"></input>
                    
                    <div class="hspacer-xlarge"></div>
                    
                    <div id="login-submit" class="button theme-b2-bg"><span>Log In or Sign Up</span></div>
                    <div class="hspacer-xlarge"></div>
                    <a href="https://api.particle.church/dist/injector">
                        <div id="play-anonymously" class="button theme-b2-bg"><span>Play Anonymously</span></div>
                    </a>
                </div>
                
                <script>
                    function cancel_subscription() 
                    {
                        result = window.confirm("Are you sure you would like to unsubscribe? Your service will terminate immediately.");
                        if (!result) return;
                        
                        let xhr = new XMLHttpRequest();
                        xhr.onreadystatechange = function() { 
                            if (xhr.readyState != 4) return;
                            if (200 > xhr.status || xhr.status > 299)
                                alert("Something went wrong while unsibscribing. Please contact a developer at admin@particle.church or on Discord.");
                            else
                                location.reload();
                        }
                        xhr.open("GET", "https://api.particle.church/users/unsubscribe/", true);
                        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                        xhr.withCredentials = true;
                        xhr.send(null);
                    }
                </script>
                
                <div class="theme-g2-bg" id="account-info" <?php if (!$user) echo('style="display:none;"'); ?>>
                    <h2 class="hugged">User <?php if($user) echo($user->user_id); ?></h2>
                    <p class="hugged theme-text-thin theme-w3-fg"><?php if($user) echo($user->email); ?></p>
                    
                    <div class="hspacer-xlarge"></div>
                    
                    <p class="hugged theme-text">
                    <?php
                    if ($user)
                    {
                        if ($user->is_subscribed)
                        {
                            echo("Your subscription will auto-renew on ".date("F j", $user->subscription_period_end).". <a href=\"javascript:cancel_subscription()\">Unsubscribe</a>");
                        }
                        else
                        {
                            echo("Our software is completely free at the time. You do not need to subscribe, but we'd happily accept your money.");
                        }
                    }
                    ?>
                    </p>
                    
                    <div class="hspacer-xlarge"></div>
                    
                    <?php
                    if ($user && !$user->is_subscribed)
                        echo('
                            <div class="button theme-b2-bg" id="subscribe-button"><span>
                                Subscribe
                            </span></div>
                        ');
                    ?>
                    
                    <div class="hspacer-medium"></div>
                    
                    <div
                        class="button theme-b2-bg"
                        onclick="javascript:document.cookie = 'session_id=0;expires=Thu, 01 Jan 1970 00:00:01 GMT; domain=.particle.church; path=/;'; location.reload();"
                    ><span>
                        Log Out
                    </span></div>
                </div>
                
                <span id="error-toaster" class="theme-r3-fg theme-text-thick"></span>
                
                <script>
                
                (function(){
                    const loginForm = document.getElementById("login-form");
                    const loginSubmitButton = document.getElementById("login-submit");
                    const loginEmailInput = document.getElementById("login-email");
                    const loginPasswordInput = document.getElementById("login-password");
                    const loginErrorToaster = document.getElementById("error-toaster");
                    let onSubmitHandler = null;
                    let isPerformingAuthXHR = false;
                    
                    function updateSubmitButton(text, action, spinning)
                    {
                        if (spinning) 
                            loginSubmitButton.setAttribute("spinner", true);
                        else
                            loginSubmitButton.removeAttribute("spinner");
                        
                        onSubmitHandler = typeof action == "function" ? action : null;
                        
                        loginSubmitButton.innerHTML = "<span>" + text + "</span>";
                    }
                    
                    function isSpinning()
                    {
                        return !!loginSubmitButton.getAttribute("spinner");
                    }
                    
                    function setError(text)
                    {
                        loginErrorToaster.innerHTML = "<span>" + text + "</span>";
                    }
                    
                    function onClickNoEmail(e)
                    {
                        setError("Please enter an email and password first.");
                    }
                    
                    function onClickLogin(e)
                    {
                        isPerformingAuthXHR = true;
                        updateSubmitButton("Log In", null, true);
                        
                        let email = loginEmailInput.value;
                        let password = loginPasswordInput.value;
                        
                        let xhr = new XMLHttpRequest();
                        xhr.onreadystatechange = function() { 
                            if (xhr.readyState != 4) return;
                            isPerformingAuthXHR = false;
                            updateSubmitButton("Log In", onClickLogin, false);
                            
                            let data = null;
                            try {
                                data = JSON.parse(xhr.responseText);
                            } catch (error) {
                              console.error(error);
                            }
                            
                            if (xhr.status == 401) {
                                if (email != loginEmailInput.value) onEmailEntryChanged();
                                setError('Incorrect password. Would you like to <a href="password_reset/?email=' + encodeURIComponent(email) + '">Reset It<a>?');
                                return;
                            }
                            
                            if (xhr.status != 200) {
                                if (email != loginEmailInput.value) onEmailEntryChanged();
                                
                                if (data && data.detail)
                                    setError(data.detail);
                                else
                                    setError(`Something went wrong while attempting to log in. Got HTTP response code: ${xhr.status}.`);
                                
                                return;
                            }
                            
                            document.cookie = "session_id=" + data.session_id + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; domain=.particle.church; path=/";
                            location.reload();
                        }
                        xhr.open("POST", "https://api.particle.church/sessions/", true);
                        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                        xhr.send(JSON.stringify({ email: email, password: password, platform: "web" }));
                    }
                    
                    function onClickRegister(e)
                    {
                        isPerformingAuthXHR = true;
                        updateSubmitButton("Sign Up", null, true);
                        
                        let email = loginEmailInput.value;
                        let password = loginPasswordInput.value;
                        
                        let xhr = new XMLHttpRequest();
                        xhr.onreadystatechange = function() { 
                            if (xhr.readyState != 4) return;
                            isPerformingAuthXHR = false;
                            updateSubmitButton("Sign Up", onClickRegister, false);
                            
                            let data = null;
                            try {
                                data = JSON.parse(xhr.responseText);
                            } catch (error) {
                              console.error(error);
                            }
                            
                            if (xhr.status != 200) {
                                if (email != loginEmailInput.value) onEmailEntryChanged();
                                
                                if (data && data.detail)
                                    setError(data.detail);
                                else
                                    setError(`Something went wrong while attempting to log in. Got HTTP response code: ${xhr.status}.`);
                                
                                return;
                            }
                            
                            document.cookie = "session_id=" + data.session_id + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; domain=.particle.church; path=/";
                            location.reload();
                        }
                        xhr.open("POST", "https://api.particle.church/users/", true);
                        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                        xhr.send(JSON.stringify({ email: email, password: password }));
                    }
                    
                    let loginEmailChangeCounter = 0;
                    function onEmailEntryChanged()
                    {
                        loginEmailChangeCounter++;
                        let myChangeIndex = loginEmailChangeCounter;
                        if (isPerformingAuthXHR) return;
                        
                        setError("");
                        
                        if (loginEmailInput.value === "")
                        {
                            loginPasswordInput.setAttribute("autocomplete", "password");
                            return updateSubmitButton("Log In or Sign Up", onClickNoEmail, false);
                        }
                        
                        updateSubmitButton("Checking Email...", null, true);
                        
                        setTimeout(function() {
                            if (myChangeIndex != loginEmailChangeCounter) return;
                            
                            var xhr = new XMLHttpRequest();
                            xhr.onreadystatechange = function() { 
                                if (xhr.readyState != 4) return;
                                if (myChangeIndex != loginEmailChangeCounter) return;
                            
                                if (xhr.status != 200) {
                                    setError(`Something went wrong while checking if that email is already attached to an account. Got HTTP response code: ${xhr.status}.`);
                                    updateSubmitButton("Log In or Sign Up", null, false);
                                    loginEmailInput.value = "";
                                    return;
                                }
                                
                                let response = JSON.parse(xhr.responseText);
                                updateSubmitButton(
                                    response.registered ? "Log In" : "Sign Up",
                                    response.registered ? onClickLogin : onClickRegister,
                                    false
                                );
                                loginPasswordInput.setAttribute("autocomplete", response.registered ? "password" : "new-password");
                            }
                            xhr.open("GET", `https://api.particle.church/users/email/${encodeURIComponent(loginEmailInput.value)}`, true);
                            xhr.send(null);
                        }, 500);
                    }
                    
                    loginEmailInput.addEventListener("input", onEmailEntryChanged);
                    window.addEventListener('DOMContentLoaded', onEmailEntryChanged);
                    
                    loginSubmitButton.addEventListener("click", (e) => { if (onSubmitHandler) onSubmitHandler(e); } );
                
                })();
                </script>
                
                <script>
                (function(){
                    const subscribeButton = document.getElementById("subscribe-button");
                    const loginErrorToaster = document.getElementById("error-toaster");
                    
                    let subscribeDebounce = false;
                    function subscribe()
                    {
                        if (subscribeDebounce) return;
                        subscribeDebounce = true;
                        subscribeButton.setAttribute("spinner", true);
                        
                        let xhr = new XMLHttpRequest();
                        xhr.onreadystatechange = function() { 
                            if (xhr.readyState != 4) return;
                            subscribeDebounce = false;
                            subscribeButton.removeAttribute("spinner");
                            
                            if (200 > xhr.status || xhr.status > 299) {
                                loginErrorToaster.innerHTML = `Failed with status code = ${xhr.status}.`;
                                console.log(xhr.responseText);
                                return;
                            }
                            
                            window.location.href = JSON.parse(xhr.responseText).url;
                        }
                        xhr.open("GET", "https://api.particle.church/users/subscribe/", true);
                        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                        xhr.withCredentials = true;
                        xhr.send(null);
                    }
                    
                    subscribeButton.addEventListener("click", subscribe);
                })();
                </script>
                
            </div>
            <iframe src="https://discord.com/widget?id=777280297422028801&theme=dark" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"></iframe>
        </div>
    </body>
    
    
    <?php
    require_once('/var/www/particle/PHP/footer.php');
    ?>
</html>