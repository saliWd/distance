package ch.widmedia.swimmeter

import androidx.multidex.MultiDexApplication
import ch.widmedia.swimmeter.dagger.AppComponent
import ch.widmedia.swimmeter.dagger.ContextModule
import ch.widmedia.swimmeter.dagger.DaggerAppComponent

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
	}
}