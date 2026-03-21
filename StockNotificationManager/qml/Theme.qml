pragma Singleton
import QtQuick 2.15

QtObject {
    // Primary colors
    readonly property color primary: "#2563eb"           // Blue
    readonly property color primaryDark: "#1e40af"
    readonly property color primaryLight: "#3b82f6"
    
    // Secondary colors
    readonly property color secondary: "#10b981"         // Green
    readonly property color secondaryDark: "#059669"
    
    // Background colors
    readonly property color background: "#f5f5f5"        // Light grey background
    readonly property color surface: "#ffffff"
    readonly property color surfaceLight: "#f9f9f9"
    readonly property color surfaceHover: "#f0f0f0"
    
    // Gradient colors
    readonly property color gradientTop: "#f5f5f5"       // Light grey
    readonly property color gradientBottom: "#e8e8e8"    // Slightly darker light grey
    
    // Text colors
    readonly property color textPrimary: "#2c2c2c"
    readonly property color textSecondary: "#5a5a5a"
    readonly property color textTertiary: "#7a7a7a"
    
    // Accent colors
    readonly property color success: "#10b981"
    readonly property color warning: "#f59e0b"
    readonly property color error: "#ef4444"
    readonly property color info: "#3b82f6"
    
    // Card colors
    readonly property color cardBackground: "#ffffff"
    readonly property color cardHover: "#f9f9f9"
    readonly property color cardBorder: "#d0d0d0"
    
    // Input colors
    readonly property color inputBackground: "#ffffff"
    readonly property color inputBorder: "#d0d0d0"
    readonly property color inputFocus: "#3b82f6"
    
    // Shadows
    readonly property color shadowLight: "#00000033"
    readonly property color shadowDark: "#00000066"
    
    // Font sizes
    readonly property int fontSizeSmall: 12
    readonly property int fontSizeNormal: 14
    readonly property int fontSizeMedium: 16
    readonly property int fontSizeLarge: 20
    readonly property int fontSizeXLarge: 24
    readonly property int fontSizeXXLarge: 32
    
    // Spacing
    readonly property int spacingXSmall: 4
    readonly property int spacingSmall: 8
    readonly property int spacingNormal: 16
    readonly property int spacingMedium: 24
    readonly property int spacingLarge: 32
    readonly property int spacingXLarge: 48
    
    // Radius
    readonly property int radiusSmall: 4
    readonly property int radiusNormal: 8
    readonly property int radiusMedium: 12
    readonly property int radiusLarge: 16
    
    // Animation
    readonly property int animationDuration: 200
    readonly property int animationDurationSlow: 300
}
