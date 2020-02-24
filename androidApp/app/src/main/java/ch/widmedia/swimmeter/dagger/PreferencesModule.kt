package ch.widmedia.swimmeter.dagger

import android.content.Context
import ch.widmedia.swimmeter.utils.PreferencesHelper
import dagger.Module
import dagger.Provides
import javax.inject.Singleton

/**
 * Created by bridou_n on 03/04/2017.
 */

@Module
object PreferencesModule {

    @JvmStatic @Provides @Singleton
    fun providesPreferencesHelper(ctx: Context) = PreferencesHelper(ctx)
}
