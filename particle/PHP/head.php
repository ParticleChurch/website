<?php
$INDEX_CSS = str_replace("//", "/", dirname($_SERVER['SCRIPT_NAME']) . "/index.css");
?>

<head>
    <base href="https://particle.church/">
    
    <!-- FONTS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400;1,500;1,600;1,700;1,800&display=swap" rel="stylesheet">

    <!-- CSS -->
    <link rel="stylesheet" type="text/css" href=<?php echo('"' . $INDEX_CSS . '"'); ?>>
    <link rel="stylesheet" type="text/css" href="CSS/theme.css">
    <link rel="stylesheet" type="text/css" href="CSS/util.css">
</head>
