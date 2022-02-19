package ch.widmedia.swimmeter

object Utils {
    val ALL = "all"
    val EDDYSTONE = "eddystone"
    val IBEACON = "Ibeacon"
    private val HEX = "0123456789ABCDEF".toCharArray()
    fun toHexString(bytes: ByteArray): String {
        if (bytes.isEmpty()) {
            return ""
        }
        val hexChars = CharArray(bytes.size * 2)
        for (j in bytes.indices) {
            val v = (bytes[j].toInt() and 0xFF)
            hexChars[j * 2] = HEX[v ushr 4]
            hexChars[j * 2 + 1] = HEX[v and 0x0F]
        }
        return String(hexChars)
    }

    fun isZeroed(bytes: ByteArray): Boolean {
        for (b in bytes) {
            if (b.toInt() != 0x00) {
                return false
            }
        }
        return true
    }

    fun getBeaconFilterFromString(optionSelected: String): Beacon.BeaconType {
        return when (optionSelected) {
            IBEACON -> {
                Beacon.BeaconType.Ibeacon
            }
            EDDYSTONE -> {
                Beacon.BeaconType.EddystoneUID
            }
            else -> {
                Beacon.BeaconType.Any
            }
        }
    }
}