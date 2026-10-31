plugins {
    alias(libs.plugins.android.application)
}

android {
    // Watch Face Format é só recursos (XML + imagens): sem código Kotlin/Java.
    enableKotlin = false
    namespace = "br.com.thiagobritoo.watchfaces.cronos"
    compileSdk = 34

    defaultConfig {
        applicationId = "br.com.thiagobritoo.watchfaces.cronos"
        // WFF v2 (Flavors, Weather) exige Wear OS 5 = API 34. O Galaxy Watch6 Classic recebe Wear OS 5+.
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
            // Para publicar na Play Store use sua própria chave; aqui assina com a de debug.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
