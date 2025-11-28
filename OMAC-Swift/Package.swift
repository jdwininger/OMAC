// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "OMAC",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "OMAC",
            targets: ["OMAC"]
        )
    ],
    dependencies: [
        // Add any external dependencies here
    ],
    targets: [
        .executableTarget(
            name: "OMAC",
            path: "Sources/OMAC"
        ),
        .testTarget(
            name: "OMACTests",
            dependencies: ["OMAC"],
            path: "Tests/OMACTests"
        )
    ]
)