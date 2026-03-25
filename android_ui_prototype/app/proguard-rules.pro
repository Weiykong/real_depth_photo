# Real Depth Photo — ProGuard Rules

# TensorFlow Lite: Keep GPU delegate + interpreter classes
-keep class org.tensorflow.** { *; }
-keep class org.tensorflow.lite.** { *; }
-dontwarn org.tensorflow.lite.**
-keepclassmembers class org.tensorflow.lite.** { *; }

# TFLite GPU delegate
-keep class org.tensorflow.lite.gpu.** { *; }
-dontwarn org.tensorflow.lite.gpu.**

# Keep native methods used by TFLite
-keepclasseswithmembernames class * {
    native <methods>;
}

# Kotlin coroutines
-dontwarn kotlinx.coroutines.**
-keep class kotlinx.coroutines.** { *; }

# Compose: keep stability metadata for recomposition
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Keep data classes used for state
-keep class com.realdepthphoto.ui.BlurPreviewParams { *; }
-keep class com.realdepthphoto.ui.blur.DepthBlurRenderOutput { *; }
-keep class com.realdepthphoto.ui.blur.DepthBlurExportResult$* { *; }
-keep class com.realdepthphoto.ui.retouch.RetouchDepthUiState { *; }
-keep class com.realdepthphoto.ui.retouch.Stroke { *; }

# General: don't obfuscate for easier crash debugging
-dontobfuscate
