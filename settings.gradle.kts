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
include(":faces:linha")
include(":faces:painel")
include(":faces:aviador")
include(":faces:pura")
include(":faces:regua")
include(":faces:fragmento")
include(":faces:deslizante")
include(":faces:matriz")
include(":faces:montanha")
include(":faces:mare")
include(":faces:aneis")
include(":faces:pendulo")
include(":faces:eclipse")
include(":faces:ceu")
include(":faces:gigante")
include(":faces:binario")
include(":faces:vinil")
include(":faces:bussola")
include(":faces:constelacao")
include(":faces:barras")
include(":faces:odometro")
include(":faces:radar")
include(":faces:mondrian")
include(":faces:ampulheta")
include(":faces:vintequatro")
include(":faces:aurora")
include(":faces:moire")
include(":faces:engrenagens")
include(":faces:osciloscopio")
include(":faces:topo")
