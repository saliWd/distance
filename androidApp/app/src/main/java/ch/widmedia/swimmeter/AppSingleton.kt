package ch.widmedia.swimmeter

import android.util.Log.ERROR
import androidx.multidex.MultiDexApplication
import ch.widmedia.swimmeter.dagger.AppComponent
import ch.widmedia.swimmeter.dagger.ContextModule
import ch.widmedia.swimmeter.dagger.DaggerAppComponent
import com.crashlytics.android.Crashlytics
import timber.log.Timber

/**
 * Created by bridou_n on 30/09/2016.
 */

class AppSingleton : MultiDexApplication() {
	
	companion object {
		lateinit var appComponent: AppComponent
	}
		
	
	override fun onCreate() {
		super.onCreate()
		
		// Dagger
		appComponent = DaggerAppComponent.builder()
			.contextModule(ContextModule(this))
				.build()
		appComponent.inject(this)
		
		// Timber
		Timber.plant(CrashReportingTree())
	}
}

/** A tree which logs important information for crash reporting.  */
class CrashReportingTree : Timber.DebugTree() {
	
	override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
		Crashlytics.log(priority, tag, message)
		
		t?.let {
			if (priority == ERROR) {
				Crashlytics.logException(t)
			}
		}
	}
}