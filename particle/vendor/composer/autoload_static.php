<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInite4268362d53a94b144318243e172d434
{
    public static $prefixLengthsPsr4 = array (
        'S' => 
        array (
            'Stripe\\' => 7,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'Stripe\\' => 
        array (
            0 => __DIR__ . '/..' . '/stripe/stripe-php/lib',
        ),
    );

    public static $classMap = array (
        'Composer\\InstalledVersions' => __DIR__ . '/..' . '/composer/InstalledVersions.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInite4268362d53a94b144318243e172d434::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInite4268362d53a94b144318243e172d434::$prefixDirsPsr4;
            $loader->classMap = ComposerStaticInite4268362d53a94b144318243e172d434::$classMap;

        }, null, ClassLoader::class);
    }
}
