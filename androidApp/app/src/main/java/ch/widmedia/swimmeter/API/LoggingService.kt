package ch.widmedia.swimmeter.API

import ch.widmedia.swimmeter.models.LoggingRequest
import io.reactivex.Completable
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.Url

/**
 * Created by bridou_n on 24/08/2017.
 */

interface LoggingService {
    @POST
    fun postLogs(@Url url: String, @Body beacons: LoggingRequest) : Completable
}