package ch.widmedia.swimmeter

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.Log
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
import org.altbeacon.beacon.Beacon
import org.altbeacon.beacon.BeaconManager
import java.io.File
import java.io.FileNotFoundException
import java.io.FileOutputStream
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream


class MainActivity : AppCompatActivity() {
    private lateinit var beaconListView: ListView
    private lateinit var beaconCountTextView: TextView
    private lateinit var monitoringButton: Button
    private lateinit var rangingButton: Button
    private lateinit var swimMeterApplication: SwimMeter

    // external write does not work, permission is declined on Android 13+
    // NB: could write anyway but not onto an existing file from a previous installation
    // private val fileName = Environment.getExternalStorageDirectory().absolutePath +"/"+ Environment.DIRECTORY_DOWNLOADS + "/SwimMeterData.csv"
    private val fileNameInternal = "SwimMeterData.csv"
    private lateinit var fileOutputStream: FileOutputStream

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        swimMeterApplication = application as SwimMeter

        // Set up a Live Data observer for beacon data
        val regionViewModel = BeaconManager.getInstanceForApplication(this).getRegionViewModel(swimMeterApplication.region)

        // observer will be called each time a new list of beacons is ranged (typically ~1 second in the foreground)
        regionViewModel.rangedBeacons.observe(this, rangingObserver)
        rangingButton = findViewById(R.id.rangingButton)
        monitoringButton = findViewById(R.id.monitoringButton)
        beaconListView = findViewById(R.id.beaconList)
        beaconCountTextView = findViewById(R.id.beaconCount)
        beaconCountTextView.text = getString(R.string.kein_beacon_gefunden)
        beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, arrayOf("--"))

        // write the header to the output file (without append mode set, so overwriting everything)
        val data = "Name, Major-Minor, RSSI, Distance\n"
        if (!BeaconScanPermissionsActivity.allPermissionsGranted(this)) {
            val intent = Intent(this, BeaconScanPermissionsActivity::class.java)
            startActivity(intent)
        }
        // All permissions are granted now
        fileOutputStream = openFileOutput(fileNameInternal, Context.MODE_PRIVATE)
        fileOutputStream.write(data.toByteArray())
        fileOutputStream = openFileOutput(fileNameInternal, Context.MODE_APPEND)
    }

    override fun onPause() {
        Log.d(TAG, "onPause")
        super.onPause()
    }
    override fun onResume() {
        Log.d(TAG, "onResume")
        super.onResume()
        // You MUST make sure the following dynamic permissions are granted by the user to detect beacons
        //    Manifest.permission.BLUETOOTH_SCAN
        //    Manifest.permission.BLUETOOTH_CONNECT
        //    Manifest.permission.ACCESS_FINE_LOCATION
        // The code needed to get these permissions has become increasingly complex, so it is in
        // its own file so as not to clutter this file focussed on how to use the library.

        if (BeaconScanPermissionsActivity.allPermissionsGranted(this)) {
            // All permissions are granted now. In the case where we are configured
            // to use a foreground service, we will not have been able to start scanning until
            // after permissions are granted. So we will do so here.
            if (BeaconManager.getInstanceForApplication(this).monitoredRegions.isEmpty()) {
                (application as SwimMeter).setupBeaconScanning()
            }
        }
    }

    private val rangingObserver = Observer<Collection<Beacon>> { beacons ->
        Log.d(TAG, "Ranged: ${beacons.count()} beacons")

        if (BeaconManager.getInstanceForApplication(this).rangedRegions.isNotEmpty()) {
            val visibleBeacons = BeaconRangingSmoother.shared.add(beacons).visibleBeacons
            beaconCountTextView.text =
                getString(R.string.suche_eingeschaltet_beacon_s_gefunden, beacons.count())
            beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1,
                visibleBeacons // when using beacons, the one beacon disappears and appears again, with the visible beacons, it's added to the list (for 5 seconds)
                    .sortedBy { it.distance }
                    // bluetoothName: widmedia                    
                    // distance: moving average (I think)
                    .map { "name: ${it.bluetoothName}\nuuid: ${it.id1}\nmajor: ${it.id2} minor: ${it.id3} rssi: ${it.rssi}\ndistance: ${it.distance} m" }.toTypedArray())
            if (beacons.isNotEmpty()) { // this does not use visibleBeacons, but beacons instead
                fileOutputStream.write(beacons
                    .map { "${it.bluetoothName}, ${it.id2}-${it.id3}, ${it.rssi}, ${it.distance}\n" }[0]
                    .toByteArray()
                )
            }
        }
    }

    fun rangingButtonTapped(@Suppress("UNUSED_PARAMETER")view: View) { // warning is wrong, this is required
        val beaconManager = BeaconManager.getInstanceForApplication(this)
        if (beaconManager.rangedRegions.isEmpty()) {
            beaconManager.startRangingBeacons(swimMeterApplication.region)
            rangingButton.text = getString(R.string.suche_ausschalten)
            beaconCountTextView.text = getString(R.string.suche_eingeschaltet_warte)
        }
        else {
            beaconManager.stopRangingBeacons(swimMeterApplication.region)
            rangingButton.text = getString(R.string.suche_einschalten)
            beaconCountTextView.text = getString(R.string.suche_ausgeschaltet)
            beaconListView.adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, arrayOf("--"))
        }
    }

    @SuppressLint("Recycle") // I do close the outputStream
    private fun saveToStorage(fileOutputStream: FileOutputStream) {
        fileOutputStream.flush()
        try {
            val inputStream: InputStream = openFileInput(fileNameInternal)

            val outputStream: OutputStream? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val values = ContentValues()
                values.put(MediaStore.Downloads.DISPLAY_NAME, "data1.csv")
                values.put(MediaStore.Downloads.MIME_TYPE, "text/csv")
                values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                val uri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                contentResolver.openOutputStream(uri!!)
            } else {
                val filePath =
                    Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                        .toString()
                val outputStream = File(filePath, "data1.csv") // NB: files are never overwritten, name might be data1(7).csv
                FileOutputStream(outputStream)
            }

            val buf = ByteArray(1024)
            var len: Int
            while (inputStream.read(buf).also { len = it } > 0) {
                outputStream!!.write(buf, 0, len)
            }
            inputStream.close()
            outputStream!!.close()
        } catch (ex: FileNotFoundException) {
            ex.printStackTrace()
        } catch (ex: IOException) {
            ex.printStackTrace()
        }
    }

    fun monitoringButtonTapped(@Suppress("UNUSED_PARAMETER")view: View) { // warning is wrong, this is required
        saveToStorage(fileOutputStream)
        monitoringButton.text = getText(R.string.speichern)

        val toast = Toast.makeText(this, getString(R.string.wurde_gespeichert), Toast.LENGTH_LONG) // in Activity
        toast.show()
    }

    companion object {
        const val TAG = "MainActivity"
    }

}
