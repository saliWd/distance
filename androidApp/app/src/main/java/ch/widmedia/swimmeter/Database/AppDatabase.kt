package ch.widmedia.swimmeter.Database

import androidx.room.Database
import androidx.room.RoomDatabase
import ch.widmedia.swimmeter.models.BeaconSaved

@Database(
        entities = [
            BeaconSaved::class
        ],
        version = 1,
        exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun beaconsDao() : BeaconsDao
}