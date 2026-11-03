plugins {
    alias(libs.plugins.android.application)
}

android {
    // Watch Face Format é só recursos (XML + imagens): sem código Kotlin/Java.
    enableKotlin = false
    namespace = "br.com.thiagobritoo.watchfaces.radar"
    compileSdk = 34

    defaultConfig {
        applicationId = "br.com.thiagobritoo.watchfaces.radar"
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
            isShrinkResources = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
