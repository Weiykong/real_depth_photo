package com.cinedepth.pro.ui.billing

import android.app.Activity
import android.content.Context
import android.util.Log
import com.android.billingclient.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Manages the one-time "Lifetime Pro" in-app purchase.
 *
 * Product ID: "pro_lifetime" — create this in Google Play Console → Monetize → In-app products.
 * Type: One-time (non-consumable).
 * Price: $4.99 (or equivalent).
 */
object ProUpgradeManager {

    private const val TAG = "ProUpgrade"
    const val PRODUCT_ID = "pro_lifetime"

    private var billingClient: BillingClient? = null
    private var productDetails: ProductDetails? = null

    private val _isPro = MutableStateFlow(false)
    val isPro: StateFlow<Boolean> = _isPro.asStateFlow()

    fun initialize(context: Context) {
        val client = BillingClient.newBuilder(context)
            .setListener { billingResult, purchases ->
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
                    for (purchase in purchases) {
                        handlePurchase(purchase)
                    }
                }
            }
            .enablePendingPurchases()
            .build()

        billingClient = client

        client.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    Log.d(TAG, "Billing connected")
                    queryExistingPurchases()
                    queryProductDetails()
                }
            }

            override fun onBillingServiceDisconnected() {
                Log.w(TAG, "Billing disconnected")
            }
        })
    }

    private fun queryExistingPurchases() {
        val client = billingClient ?: return
        client.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        ) { result, purchases ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                val hasPro = purchases.any {
                    it.products.contains(PRODUCT_ID) &&
                        it.purchaseState == Purchase.PurchaseState.PURCHASED
                }
                _isPro.value = hasPro
                Log.d(TAG, "Existing purchase check: isPro=$hasPro")
                // Acknowledge any unacknowledged purchases
                purchases.filter { !it.isAcknowledged }.forEach { handlePurchase(it) }
            }
        }
    }

    private fun queryProductDetails() {
        val client = billingClient ?: return
        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(
                listOf(
                    QueryProductDetailsParams.Product.newBuilder()
                        .setProductId(PRODUCT_ID)
                        .setProductType(BillingClient.ProductType.INAPP)
                        .build()
                )
            )
            .build()

        client.queryProductDetailsAsync(params) { result, detailsList ->
            if (result.responseCode == BillingClient.BillingResponseCode.OK && detailsList.isNotEmpty()) {
                productDetails = detailsList.first()
                Log.d(TAG, "Product loaded: ${productDetails?.name}")
            }
        }
    }

    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            _isPro.value = true
            if (!purchase.isAcknowledged) {
                val params = AcknowledgePurchaseParams.newBuilder()
                    .setPurchaseToken(purchase.purchaseToken)
                    .build()
                billingClient?.acknowledgePurchase(params) { result ->
                    Log.d(TAG, "Acknowledge result: ${result.responseCode}")
                }
            }
        }
    }

    /**
     * Returns the formatted price string (e.g. "$4.99") or null if not loaded yet.
     */
    fun getFormattedPrice(): String? {
        return productDetails?.oneTimePurchaseOfferDetails?.formattedPrice
    }

    /**
     * Launches the purchase flow. Call from an Activity context.
     */
    fun launchPurchase(activity: Activity) {
        val details = productDetails
        if (details == null) {
            Log.w(TAG, "Product details not loaded yet")
            return
        }
        val flowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(
                listOf(
                    BillingFlowParams.ProductDetailsParams.newBuilder()
                        .setProductDetails(details)
                        .build()
                )
            )
            .build()
        billingClient?.launchBillingFlow(activity, flowParams)
    }
}
