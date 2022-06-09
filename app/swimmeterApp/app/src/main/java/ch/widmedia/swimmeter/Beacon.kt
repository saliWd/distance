package ch.widmedia.swimmeter


class Beacon(mac: String?) {
    enum class BeaconType {
        Ibeacon, EddystoneUID, Any
    }

    val macAddress = mac
    var manufacturer: String? = null
    var type: BeaconType = BeaconType.Any
    var uuid: String? = null
    var major: Int? = null
    var minor: Int? = null
    var namespace: String? = null
    var instance: String? = null
    var rssi: Int? = null
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Beacon) return false

        if (macAddress != other.macAddress) return false

        return true
    }

    override fun hashCode(): Int {
        return macAddress?.hashCode() ?: 0
    }

}