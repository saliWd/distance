package ch.widmedia.swimmeter

import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.util.Log
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
import org.altbeacon.beacon.Beacon
import org.altbeacon.beacon.BeaconManager
import org.altbeacon.beacon.MonitorNotifier
import android.content.Intent
import android.view.View
import ch.widmedia.beacon.permissions.BeaconScanPermissionsActivity
import java.io.*


class MainActivity : AppCompatActivity() {
    private lateinit var beaconListView: ListView
    private lateinit var beaconCountTextView: TextView
    private lateinit var monitoringButton: Button
    private lateinit var rangingButton: Button
    private lateinit var beaconReferenceApplication: SwimMeter
    private var alertDialog: AlertDialog? = null

    private val file = "entries.csv"
    private lateinit var fileOutputStream: FileOutputStream

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        beaconReferenceApplication = application as SwimMeter

        // Set up a Live Data observer for beacon data
        val regionViewModel = BeaconManager.getInstanceForApplication(this).getRegionViewModel(beaconReferenceApplication.region)
        // observer will be called each time the monitored regionState changes (inside vs. outside region)
        regionViewModel.regionState.observe(this, monitoringObserver)
        // observer will be called each time a new list of beacons is ranged (typically ~1 second in the foreground)
        regionViewModel.rangedBeacons.observe(this, rangingObserver)
        rangingButton = findViewById(R.id.rangingButton)
        monitoringButton = findViewById(R.id.monitoringButton)
        beaconListView = findViewById(R.id.beaconList)
        beaconCountTextView = findViewById(R.id.beaconCount)
        beaconCountTextView.text = getString(R.string.no_beacons_detected)
        beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, arrayOf("--"))

        // write the header to the output file (without append mode set, so overwriting everything)
        val data = "Name, Major-Minor, RSSI, Distance\n"
        fileOutputStream = openFileOutput(file, Context.MODE_PRIVATE) // this one does an overwrite
        fileOutputStream.write(data.toByteArray())
        fileOutputStream = openFileOutput(file, Context.MODE_APPEND) // it's actually private OR append
    }

    override fun onPause() {
        Log.d(TAG, "onPause")
        super.onPause()
    }
    override fun onResume() {
        Log.d(TAG, "onResume")
        super.onResume()
        // You MUST make sure the following dynamic permissions are granted by the user to detect beacons
        //
        //    Manifest.permission.BLUETOOTH_SCAN
        //    Manifest.permission.BLUETOOTH_CONNECT
        //    Manifest.permission.ACCESS_FINE_LOCATION
        //    Manifest.permission.ACCESS_BACKGROUND_LOCATION // only needed to detect in background
        //
        // The code needed to get these permissions has become increasingly complex, so it is in
        // its own file so as not to clutter this file focussed on how to use the library.

        if (!BeaconScanPermissionsActivity.allPermissionsGranted(this,
                true)) {
            val intent = Intent(this, BeaconScanPermissionsActivity::class.java)
            intent.putExtra("backgroundAccessRequested", true)
            startActivity(intent)
        }
        else {
            // All permissions are granted now. In the case where we are configured
            // to use a foreground service, we will not have been able to start scanning until
            // after permissions are granted. So we will do so here.
            if (BeaconManager.getInstanceForApplication(this).monitoredRegions.isEmpty()) {
                (application as SwimMeter).setupBeaconScanning()
            }
        }
    }

    private val monitoringObserver = Observer<Int> { state ->
        var dialogTitle = "Beacons detected"
        var dialogMessage = "didEnterRegionEvent has fired"
        var stateString = "inside"
        if (state == MonitorNotifier.OUTSIDE) {
            dialogTitle = "No beacons detected"
            dialogMessage = "didExitRegionEvent has fired"
            stateString = "outside"
            beaconCountTextView.text =
                getString(R.string.outside_of_the_beacon_region_no_beacons_detected)
            beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, arrayOf("--"))
        }
        else {
            beaconCountTextView.text = getString(R.string.inside_the_beacon_region)
        }
        Log.d(TAG, "monitoring state changed to : $stateString")
        val builder =
            AlertDialog.Builder(this)
        builder.setTitle(dialogTitle)
        builder.setMessage(dialogMessage)
        builder.setPositiveButton(android.R.string.ok, null)
        alertDialog?.dismiss()
        alertDialog = builder.create()
        alertDialog?.show()
    }

    private val rangingObserver = Observer<Collection<Beacon>> { beacons ->
        Log.d(TAG, "Ranged: ${beacons.count()} beacons")

        if (BeaconManager.getInstanceForApplication(this).rangedRegions.isNotEmpty()) {
            val visibleBeacons = BeaconRangingSmoother.shared.add(beacons).visibleBeacons
            beaconCountTextView.text =
                getString(R.string.ranging_enabled_beacon_s_detected, beacons.count())
            beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1,
                visibleBeacons // when using beacons, the one beacon disappears and appears again, with the visible beacons, it's added to the list (for 5 seconds)
                    .sortedBy { it.distance }
                    // bluetoothName: widmedia                    
                    // distance: moving average (I think)
                    .map { "name: ${it.bluetoothName}\nuuid: ${it.id1}\nmajor: ${it.id2} minor: ${it.id3} rssi: ${it.rssi}\ndistance: ${it.distance} m" }.toTypedArray())
            if (beacons.isNotEmpty()) {
                fileOutputStream.write(beacons // this does not use visibleBeacons, but beacons instead
                    .sortedBy { it.distance }
                    .map { "${it.bluetoothName}, ${it.id2}-${it.id3}, ${it.rssi}, ${it.distance}\n" }
                    .toString().toByteArray()
                )
            }
        }
    }

    fun rangingButtonTapped(@Suppress("UNUSED_PARAMETER")view: View) { // warning is wrong, this is required
        val beaconManager = BeaconManager.getInstanceForApplication(this)
        if (beaconManager.rangedRegions.isEmpty()) {
            beaconManager.startRangingBeacons(beaconReferenceApplication.region)
            rangingButton.text = getString(R.string.stop_ranging)
            beaconCountTextView.text = getString(R.string.ranging_enabled_awaiting_first_callback)
        }
        else {
            beaconManager.stopRangingBeacons(beaconReferenceApplication.region)
            rangingButton.text = getString(R.string.start_ranging)
            beaconCountTextView.text = getString(R.string.ranging_disabled_no_beacons_detected)
            beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, arrayOf("--"))
        }
    }

    fun monitoringButtonTapped(@Suppress("UNUSED_PARAMETER")view: View) { // warning is wrong, this is required
        val dialogTitle: String
        val dialogMessage: String
        val beaconManager = BeaconManager.getInstanceForApplication(this)
        if (beaconManager.monitoredRegions.isEmpty()) {
            beaconManager.startMonitoring(beaconReferenceApplication.region)
            dialogTitle = "Beacon monitoring started."
            dialogMessage = "You will see a dialog if a beacon is detected, and another if beacons then stop being detected."
            monitoringButton.text = getString(R.string.stop_monitoring)
        }
        else {
            beaconManager.stopMonitoring(beaconReferenceApplication.region)
            dialogTitle = "Beacon monitoring stopped."
            dialogMessage = "You will no longer see dialogs when beacons start/stop being detected."
            monitoringButton.text = getString(R.string.start_monitoring)
        }
        val builder =
            AlertDialog.Builder(this)
        builder.setTitle(dialogTitle)
        builder.setMessage(dialogMessage)
        builder.setPositiveButton(android.R.string.ok, null)
        alertDialog?.dismiss()
        alertDialog = builder.create()
        alertDialog?.show()

    }

    companion object {
        const val TAG = "MainActivity"
    }

}
