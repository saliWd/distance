package ch.widmedia.swimmeter.models

import ch.widmedia.swimmeter.models.BeaconSaved
import com.google.gson.annotations.SerializedName

/**
 * Created by bridou_n on 26/08/2017.
 */

data class LoggingRequest(
        @SerializedName("reader")
        val deviceName: String,

        @SerializedName("beacons")
        val beacons: List<BeaconSaved>
)