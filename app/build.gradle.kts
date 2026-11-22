plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "app.takagelokoi"
    compileSdk = 34

    defaultConfig {
        // Keep this the same as your old MyKhata APK if you want to install over it
        // and keep its data without a backup/restore. See README.
        applicationId = "app.takagelokoi"
        minSdk = 24
        targetSdk = 34
        versionCode = 3
        versionName = "3.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1") // FileProvider (share backup)
}
