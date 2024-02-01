package ch.widmedia.swimmeter

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.setPadding

open class PermissionsActivity: AppCompatActivity() {

    val requestPermissionsLauncher =
        registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            // Handle Permission granted/rejected
            permissions.entries.forEach {
                val permissionName = it.key
                val isGranted = it.value
                if (isGranted) {
                    Log.d(TAG, "$permissionName permission granted: true")
                    // Permission is granted. Continue the action or workflow in your app
                } else {
                    Log.d(TAG, "$permissionName permission granted: false")
                    // Explain to the user that the feature is unavailable because the
                    // features requires a permission that the user has denied. At the
                    // same time, respect the user's decision. Don't link to system
                    // settings in an effort to convince the user to change their
                    // decision.
                }
            }
        }

    companion object {
        const val TAG = "PermissionsActivity"
    }
}

class PermissionsHelper(private val context: Context) {
    // Manifest.permission.ACCESS_FINE_LOCATION
    // Manifest.permission.BLUETOOTH_CONNECT
    // Manifest.permission.BLUETOOTH_SCAN
    fun isPermissionGranted(permissionString: String): Boolean {
        return (ContextCompat.checkSelfPermission(context, permissionString) == PackageManager.PERMISSION_GRANTED)
    }
    fun setFirstTimeAskingPermission(permissionString: String, isFirstTime: Boolean) {
        val sharedPreference = context.getSharedPreferences("ch.widmedia.swimmeter",
            AppCompatActivity.MODE_PRIVATE
        )
        sharedPreference.edit().putBoolean(permissionString,isFirstTime).apply()
    }

    fun isFirstTimeAskingPermission(permissionString: String): Boolean {
        val sharedPreference = context.getSharedPreferences(
            "ch.widmedia.swimmeter",
            AppCompatActivity.MODE_PRIVATE
        )
        return sharedPreference.getBoolean(permissionString,true)
    }
    fun beaconScanPermissionGroupsNeeded(): List<Array<String>> {
        val permissions = ArrayList<Array<String>>()

        // to save the csv with the logged rssi values (from internal to external destination)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // WRITE_EXTERNAL_STORAGE is deprecated (and is not granted) when targeting Android 13+. If you need to write to shared storage, use the `MediaStore.createWriteRequest` intent.
        } else {
            permissions.add(arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE))
        }

        // As of version M (6) we need FINE_LOCATION (or COARSE_LOCATION, but we ask for FINE)
        permissions.add(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION))

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            // As of version S (31, Android 12) we need FINE_LOCATION, BLUETOOTH_SCAN
            // Manifest.permission.BLUETOOTH_CONNECT is not absolutely required to do just scanning,
            // but it is required if you want to access some info from the scans like the device name
            // and the additional cost of requesting this access is minimal, so we just request it
            permissions.add(arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT))
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // As of version T (33, Android 13) we POST_NOTIFICATIONS permissions if using a foreground service
            permissions.add(arrayOf(Manifest.permission.POST_NOTIFICATIONS))
        }
        return permissions
    }
}



open class BeaconScanPermissionsActivity: PermissionsActivity()  {
    private lateinit var layout: LinearLayout
    private lateinit var permissionGroups: List<Array<String>>
    private lateinit var continueButton: Button
    private val scale: Float
        get() {
            return this.resources.displayMetrics.density
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        layout = LinearLayout(this)
        layout.setPadding(dp(20))
        layout.gravity = Gravity.CENTER
        layout.setBackgroundColor(Color.WHITE)
        layout.orientation = LinearLayout.VERTICAL
        val title = intent.getStringExtra("title") ?: "Berechtigungen erforderlich"
        val message = intent.getStringExtra("message") ?: "Um nach dem SwimMeter-Beacon zu suchen, braucht diese App folgende Berechtigungen. Bitte die entsprechenden Buttons antippen, um die Berechtigungen zu erteilen."
        val continueButtonTitle = intent.getStringExtra("continueButtonTitle") ?: "Weiter"
        val permissionButtonTitles = intent.getBundleExtra("permissionBundleTitles") ?: getDefaultPermissionTitlesBundle()

        permissionGroups = PermissionsHelper(this).beaconScanPermissionGroupsNeeded()

        val params = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        params.setMargins(dp(0), dp(10), dp(0), dp(10))


        val titleView = TextView(this)
        titleView.gravity = Gravity.CENTER
        titleView.textSize = dp(10).toFloat()
        titleView.text = title
        titleView.layoutParams = params

        layout.addView(titleView)
        val messageView = TextView(this)
        messageView.text = message
        messageView.gravity = Gravity.CENTER
        messageView.textSize = dp(5).toFloat()
        messageView.textAlignment = TextView.TEXT_ALIGNMENT_CENTER
        messageView.layoutParams = params
        layout.addView(messageView)

        var index = 0
        for (permissionGroup in permissionGroups) {
            val button = Button(this)
            val buttonTitle = permissionButtonTitles.getString(permissionGroup.first())
            button.id = index
            button.text = buttonTitle
            button.layoutParams = params
            button.setOnClickListener(buttonClickListener)
            layout.addView(button)
            index += 1
        }

        continueButton = Button(this)
        continueButton.text = continueButtonTitle
        continueButton.isEnabled = false
        continueButton.setOnClickListener {
            // TODO: this somehow shoves the app (whole app) into the background, user is on the Android home screen again.
            // App is still running though on the other view (and correctly displaying the beacons)
            this.finish()
        }
        continueButton.layoutParams = params
        layout.addView(continueButton)

        setContentView(layout)
    }

    private fun dp(value: Int): Int {
        return (value * scale + 0.5f).toInt()
    }

    private val buttonClickListener = View.OnClickListener { button ->
        val permissionsGroup = permissionGroups[button.id]
        promptForPermissions(permissionsGroup)
    }

    @SuppressLint("InlinedApi")
    fun getDefaultPermissionTitlesBundle(): Bundle {
        val bundle = Bundle()
        bundle.putString(Manifest.permission.ACCESS_FINE_LOCATION, "Location")
        bundle.putString(Manifest.permission.BLUETOOTH_SCAN, "Bluetooth")
        bundle.putString(Manifest.permission.POST_NOTIFICATIONS, "Notifications")
        return bundle
    }


    private fun allPermissionGroupsGranted(): Boolean {
        for (permissionsGroup in permissionGroups) {
            if (!allPermissionsGranted(permissionsGroup)) {
                return false
            }
        }
        return true
    }

    private fun setButtonColors() {
        var index = 0
        for (permissionsGroup in this.permissionGroups) {
            val button = findViewById<Button>(index)
            if (allPermissionsGranted(permissionsGroup)) {
                button.setBackgroundColor(Color.parseColor("#448844"))
            }
            else {
                button.setBackgroundColor(Color.RED)
            }
            index += 1
        }
    }
    override fun onResume() {
        super.onResume()
        setButtonColors()
        if (allPermissionGroupsGranted()) {
            continueButton.isEnabled = true
        }
    }

    private fun promptForPermissions(permissionsGroup: Array<String>) {
        if (!allPermissionsGranted(permissionsGroup)) {
            val firstPermission = permissionsGroup.first()

            val showRationale: Boolean = shouldShowRequestPermissionRationale(firstPermission)
            if (showRationale ||  PermissionsHelper(this).isFirstTimeAskingPermission(firstPermission)) {
                PermissionsHelper(this).setFirstTimeAskingPermission(firstPermission, false)
                requestPermissionsLauncher.launch(permissionsGroup)
            }
            else {
                val builder = AlertDialog.Builder(this)
                builder.setTitle("Can't request permission")
                builder.setMessage("This permission has been previously denied to this app.  In order to grant it now, you must go to Android Settings to enable this permission.")
                builder.setPositiveButton("OK", null)
                builder.show()
            }
        }
    }
    private fun allPermissionsGranted(permissionsGroup: Array<String>): Boolean {
        val permissionsHelper = PermissionsHelper(this)
        for (permission in permissionsGroup) {
            if (!permissionsHelper.isPermissionGranted(permission)) {
                return false
            }
        }
        return true
    }

    companion object {
        fun allPermissionsGranted(context: Context): Boolean {
            val permissionsHelper = PermissionsHelper(context)
            val permissionsGroups = permissionsHelper.beaconScanPermissionGroupsNeeded()
            for (permissionsGroup in permissionsGroups) {
                for (permission in permissionsGroup) {
                    if (!permissionsHelper.isPermissionGranted(permission)) {
                        return false
                    }
                }
            }
            return true
        }
    }
}
