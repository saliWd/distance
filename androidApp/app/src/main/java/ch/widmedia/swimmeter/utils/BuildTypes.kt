package ch.widmedia.swimmeter.utils

import ch.widmedia.swimmeter.BuildConfig

object BuildTypes {

    fun isRelease() = BuildConfig.BUILD_TYPE.contentEquals("release")

    fun isDebug() = BuildConfig.BUILD_TYPE.contentEquals("debug")
}