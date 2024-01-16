package ch.widmedia.swimmeter

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.lorenzofelletti.permissions.PermissionManager
import com.lorenzofelletti.permissions.dispatcher.dsl.*
import ch.widmedia.swimmeter.BuildConfig.DEBUG
import ch.widmedia.swimmeter.blescanner.BleScanManager
import ch.widmedia.swimmeter.blescanner.adapter.BleDeviceAdapter
import ch.widmedia.swimmeter.blescanner.model.BleDevice
import ch.widmedia.swimmeter.blescanner.model.BleScanCallback

class MainActivity : AppCompatActivity() {
    private lateinit var btnStartScan: Button

    private lateinit var permissionManager: PermissionManager

    private lateinit var btManager: BluetoothManager
    private lateinit var bleScanManager: BleScanManager

    private lateinit var foundDevices: MutableList<BleDevice>
    private lateinit var foundUnnamed: MutableList<BleDevice>

    @SuppressLint("MissingPermission")
    @RequiresApi(Build.VERSION_CODES.S)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        permissionManager = PermissionManager(this)
        permissionManager buildRequestResultsDispatcher {
            withRequestCode(BLE_PERMISSION_REQUEST_CODE) {
                checkPermissions(blePermissions)
                showRationaleDialog(getString(R.string.ble_permission_rationale))
                doOnGranted { bleScanManager.scanBleDevices() }
                doOnDenied {
                    Toast.makeText(
                        this@MainActivity,
                        getString(R.string.ble_permissions_denied_message),
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }

        // RecyclerView handling
        val rvFoundDevices = findViewById<View>(R.id.rv_found_devices) as RecyclerView
        val rvFoundUnnamed = findViewById<View>(R.id.rv_found_unnamed) as RecyclerView
        foundDevices = BleDevice.createBleDevicesList()
        foundUnnamed = BleDevice.createBleDevicesList()
        val adapter = BleDeviceAdapter(foundDevices)
        val adapterUnnamed = BleDeviceAdapter(foundUnnamed)
        rvFoundDevices.adapter = adapter
        rvFoundUnnamed.adapter = adapterUnnamed

        rvFoundDevices.layoutManager = LinearLayoutManager(this)
        rvFoundUnnamed.layoutManager = LinearLayoutManager(this)

        // BleManager creation
        btManager = getSystemService(BluetoothManager::class.java)
        bleScanManager = BleScanManager(btManager, 5000, scanCallback = BleScanCallback({
            val name = it?.device?.address // not really the name, rather the MAC address
            val description = it?.device?.name
            val type = it?.device?.type // 2 = beacon
            val uuids = it?.device?.uuids // TODO: this is null somehow...
            // val rssi = it?.device?.rssi // does not exist. How to get it?
            val macNameType = "$name $description $type $uuids"
            if (name.isNullOrBlank()) return@BleScanCallback

            val device = BleDevice(macNameType)

            /* something like that...
            if (description == "widmedia.ch") {
               connectedDevice = it?.device?.connectGatt(it?.device?, true, BluetoothGattCallback())
            }
            */

            if (description.isNullOrBlank()) {
                if (!foundUnnamed.contains(device)) {
                    foundUnnamed.add(device)
                    adapterUnnamed.notifyItemInserted(foundUnnamed.size - 1)
                }
            } else {
                if (!foundDevices.contains(device)) {
                    foundDevices.add(device)
                    adapter.notifyItemInserted(foundDevices.size - 1)
                }
            }
        }))

        // Adding the actions the manager must do before and after scanning
        bleScanManager.beforeScanActions.add { btnStartScan.isEnabled = false }
        bleScanManager.beforeScanActions.add {
            foundDevices.size.let {
                foundDevices.clear()
                adapter.notifyItemRangeRemoved(0, it)
            }
            foundUnnamed.size.let {
                foundUnnamed.clear()
                adapterUnnamed.notifyItemRangeRemoved(0, it)
            }
        }
        bleScanManager.afterScanActions.add { btnStartScan.isEnabled = true }

        // Adding the onclick listener to the start scan button
        btnStartScan = findViewById(R.id.btn_start_scan)
        btnStartScan.setOnClickListener {
            if (DEBUG) Log.i(TAG, "${it.javaClass.simpleName}:${it.id} - onClick event")

            // Checks if the required permissions are granted and starts the scan if so, otherwise it requests them
            permissionManager checkRequestAndDispatch BLE_PERMISSION_REQUEST_CODE
        }
    }

    /**
     * Function that checks whether the permission was granted or not
     */
    @RequiresApi(Build.VERSION_CODES.S)
    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        permissionManager.dispatchOnRequestPermissionsResult(requestCode, grantResults)
    }

    companion object {
        private val TAG = MainActivity::class.java.simpleName

        private const val BLE_PERMISSION_REQUEST_CODE = 1
        @RequiresApi(Build.VERSION_CODES.S)
        private val blePermissions = arrayOf(
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.BLUETOOTH_CONNECT,
        )
    }
}