package ch.widmedia.swimmeter.dagger

import ch.widmedia.swimmeter.AppSingleton
import ch.widmedia.swimmeter.features.beaconList.BeaconListActivity
import ch.widmedia.swimmeter.features.beaconList.ControlsBottomSheetDialog
import ch.widmedia.swimmeter.features.blockedList.BlockedActivity
import ch.widmedia.swimmeter.features.settings.SettingsActivity
import dagger.Component
import org.altbeacon.beacon.BeaconManager
import javax.inject.Singleton

/**
 * Created by bridou_n on 05/10/2016.
 */
@Singleton
@Component(modules = [
    ContextModule::class,
    DatabaseModule::class,
    NetworkModule::class,
    PreferencesModule::class,
    AnalyticsModule::class,
    BluetoothModule::class
])
interface AppComponent {
    fun providesBeaconManager() : BeaconManager

    fun inject(app: AppSingleton)
    fun inject(activity: BeaconListActivity)
    fun inject(activity: SettingsActivity)
    fun inject(activity: BlockedActivity)

    fun inject(bs: ControlsBottomSheetDialog)
}
