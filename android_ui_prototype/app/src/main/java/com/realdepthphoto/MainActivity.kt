package com.realdepthphoto

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.realdepthphoto.ui.RealDepthPhotoApp
import com.realdepthphoto.ui.theme.RealDepthPhotoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            RealDepthPhotoTheme {
                RealDepthPhotoApp()
            }
        }
    }
}
