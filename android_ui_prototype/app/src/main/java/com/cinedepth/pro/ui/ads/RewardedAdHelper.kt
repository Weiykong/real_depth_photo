package com.cinedepth.pro.ui.ads

import android.app.Activity
import android.content.Context
import android.util.Log
import com.google.android.gms.ads.AdError
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.FullScreenContentCallback
import com.google.android.gms.ads.LoadAdError
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.rewarded.RewardedAd
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback

object RewardedAdHelper {

    private const val TAG = "RewardedAd"

    // Test ad unit ID — replace with real one before publishing
    private const val AD_UNIT_ID = "ca-app-pub-3940256099942544/5224354917"

    private var rewardedAd: RewardedAd? = null
    private var isLoading = false

    fun initialize(context: Context) {
        MobileAds.initialize(context) {}
        preload(context)
    }

    fun preload(context: Context) {
        if (rewardedAd != null || isLoading) return
        isLoading = true
        val adRequest = AdRequest.Builder().build()
        RewardedAd.load(context, AD_UNIT_ID, adRequest, object : RewardedAdLoadCallback() {
            override fun onAdLoaded(ad: RewardedAd) {
                Log.d(TAG, "Ad loaded")
                rewardedAd = ad
                isLoading = false
            }

            override fun onAdFailedToLoad(error: LoadAdError) {
                Log.w(TAG, "Ad failed to load: ${error.message}")
                rewardedAd = null
                isLoading = false
            }
        })
    }

    fun isReady(): Boolean = rewardedAd != null

    /**
     * Shows a rewarded ad. Calls [onRewarded] when the user earns the reward,
     * or [onDismissed] when the ad is dismissed (regardless of reward).
     * If no ad is loaded, calls [onNotAvailable] immediately.
     */
    fun showForHighResSave(
        activity: Activity,
        onRewarded: () -> Unit,
        onDismissed: () -> Unit = {},
        onNotAvailable: () -> Unit = {}
    ) {
        val ad = rewardedAd
        if (ad == null) {
            Log.w(TAG, "No ad available, granting reward anyway")
            onNotAvailable()
            preload(activity)
            return
        }

        var rewarded = false
        ad.fullScreenContentCallback = object : FullScreenContentCallback() {
            override fun onAdDismissedFullScreenContent() {
                Log.d(TAG, "Ad dismissed, rewarded=$rewarded")
                rewardedAd = null
                preload(activity)
                if (rewarded) {
                    onRewarded()
                }
                onDismissed()
            }

            override fun onAdFailedToShowFullScreenContent(error: AdError) {
                Log.w(TAG, "Ad failed to show: ${error.message}")
                rewardedAd = null
                preload(activity)
                onNotAvailable()
            }
        }

        ad.show(activity) {
            Log.d(TAG, "User earned reward")
            rewarded = true
        }
    }
}
