package ch.widmedia.swimmeter

import android.app.*
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.lifecycle.Observer
import org.altbeacon.beacon.*

class SwimMeter: Application() {
    // the region definition is a wildcard that matches all beacons regardless of identifiers.
    // if you only want to detect beacons with a specific UUID, change the id1 parameter to
    // a UUID like Identifier.parse("2F234454-CF6D-4A0F-ADF2-F4911BA9FFA6")
    // var region = Region("all-beacons", null, null, null)
    // only listening to beacons with major=30569
    var region = Region("all-beacons", null, Identifier.parse("30569"), null)

    override fun onCreate() {
        super.onCreate()

        val beaconManager = BeaconManager.getInstanceForApplication(this)
        // BeaconManager.setDebug(true) // enabling debugging will send lots of verbose debug information from the library to Logcat

        // Block the library from updating its distance model database
        BeaconManager.setDistanceModelUpdateUrl("")

        // The example shows how to find iBeacon.
        val parser = BeaconParser().
        setBeaconLayout("m:2-3=0215,i:4-19,i:20-21,i:22-23,p:24-24")
        parser.setHardwareAssistManufacturerCodes(arrayOf(0x004c).toIntArray())
        beaconManager.beaconParsers.add(
            parser)
    }
    fun setupBeaconScanning() {
        val beaconManager = BeaconManager.getInstanceForApplication(this)

        // If you want more frequent scanning (requires a foreground service on Android 8+),
        // configure that here.
        // If you want to continuously range beacons more often than every 15 minutes,
        // you can use the library's built-in foreground service to unlock this behavior on Android
        // 8+.   the method below shows how you set that up.
        try {
            setupForegroundService()
        }
        catch (e: SecurityException) {
            // On Android TIRAMISU + this security exception will happen
            // if location permission has not been granted when we start
            // a foreground service.  In this case, wait to set this up
            // until after that permission is granted
            Log.d(TAG, "Not setting up foreground service scanning until location permission granted by user")
            return
        }
        
        // These two lines set up a Live Data observer so this Activity can get beacon data from the Application class
        val regionViewModel = BeaconManager.getInstanceForApplication(this).getRegionViewModel(region)
        // observer will be called each time a new list of beacons is ranged (typically ~1 second in the foreground)
        regionViewModel.rangedBeacons.observeForever( centralRangingObserver)
    }

    private fun setupForegroundService() {
        val builder = Notification.Builder(this, "SwimMeter")
        builder.setSmallIcon(R.mipmap.ic_launcher_foreground)
        builder.setContentTitle(getString(R.string.notification))
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
                this, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT + PendingIntent.FLAG_IMMUTABLE
        )
        builder.setContentIntent(pendingIntent)
        val channel =  NotificationChannel("swimmeter-notification-id",
            "My Notification Name", NotificationManager.IMPORTANCE_DEFAULT)
        channel.description = "My Notification Channel Description"
        val notificationManager =  getSystemService(
                Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.createNotificationChannel(channel)
        builder.setChannelId(channel.id)
        Log.d(TAG, "Calling enableForegroundServiceScanning")
        BeaconManager.getInstanceForApplication(this).enableForegroundServiceScanning(builder.build(), 456)
        Log.d(TAG, "Back from  enableForegroundServiceScanning")
    }

    private val centralRangingObserver = Observer<Collection<Beacon>> { beacons ->
        val rangeAgeMillis = System.currentTimeMillis() - (beacons.firstOrNull()?.lastCycleDetectionTimestamp ?: 0)
        if (rangeAgeMillis < 10000) {
            Log.d(MainActivity.TAG, "Ranged: ${beacons.count()} beacons")
            for (beacon: Beacon in beacons) {
                Log.d(TAG, "$beacon about ${beacon.distance} meters away")
            }
        }
        else {
            Log.d(MainActivity.TAG, "Ignoring stale ranged beacons from $rangeAgeMillis millis ago")
        }
    }

    companion object {
        const val TAG = "SwimMeter"
    }

}