pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "watchfaces"

// Uma watchface = um módulo em faces/<nome>. Para adicionar outra, inclua aqui.
include(":faces:cronos")
include(":faces:crt")
include(":faces:lunar")
