//
//  PhotoManager.swift
//  OMAC
//
//  Created on 2025-11-27
//  Service for managing photo files and operations
//

import Foundation
import SwiftUI
import UniformTypeIdentifiers

enum PhotoError: LocalizedError {
    case invalidImage
    case saveFailed
    case directoryCreationFailed
    case fileNotFound

    var errorDescription: String? {
        switch self {
        case .invalidImage:
            return "The selected file is not a valid image."
        case .saveFailed:
            return "Failed to save the photo."
        case .directoryCreationFailed:
            return "Failed to create photos directory."
        case .fileNotFound:
            return "Photo file not found."
        }
    }
}

@MainActor
class PhotoManager: ObservableObject {
    static let shared = PhotoManager()

    private let fileManager = FileManager.default
    private var photosDirectory: URL?

    init() {
        setupPhotosDirectory()
    }

    private func setupPhotosDirectory() {
        do {
            let appSupport = try fileManager.url(for: .applicationSupportDirectory,
                                                in: .userDomainMask,
                                                appropriateFor: nil,
                                                create: true)
            let omacDir = appSupport.appendingPathComponent("OMAC")
            let photosDir = omacDir.appendingPathComponent("photos")

            try fileManager.createDirectory(at: photosDir, withIntermediateDirectories: true)
            photosDirectory = photosDir
        } catch {
            print("Failed to create photos directory: \(error)")
        }
    }

    func savePhoto(from url: URL, for figure: ActionFigure) async throws -> Photo {
        guard let photosDir = photosDirectory else {
            throw PhotoError.directoryCreationFailed
        }

        // Validate it's an image
        guard url.isImageFile else {
            throw PhotoError.invalidImage
        }

        // Generate unique filename
        let filename = "\(figure.id.uuidString)_\(UUID().uuidString).\(url.pathExtension)"
        let destinationURL = photosDir.appendingPathComponent(filename)

        // Copy file to photos directory
        try fileManager.copyItem(at: url, to: destinationURL)

        // Create Photo model
        let photo = Photo(
            filePath: destinationURL.path,
            figure: figure
        )

        return photo
    }

    func deletePhoto(_ photo: Photo) throws {
        guard fileManager.fileExists(atPath: photo.filePath) else {
            throw PhotoError.fileNotFound
        }

        try fileManager.removeItem(atPath: photo.filePath)
    }

    func setPrimaryPhoto(_ photo: Photo, for figure: ActionFigure) {
        // Unset all other primary photos for this figure
        if let photos = figure.photos {
            for existingPhoto in photos where existingPhoto.isPrimary {
                existingPhoto.isPrimary = false
            }
        }

        // Set this photo as primary
        photo.isPrimary = true
    }

    func getPhotosDirectory() -> URL? {
        return photosDirectory
    }

    func cleanupOrphanedPhotos() async {
        guard let photosDir = photosDirectory else { return }

        do {
            let photoFiles = try fileManager.contentsOfDirectory(at: photosDir,
                                                               includingPropertiesForKeys: nil)

            // Get all photo paths from database
            // This would need to be implemented with a database query
            // For now, we'll skip this cleanup
        } catch {
            print("Failed to cleanup orphaned photos: \(error)")
        }
    }
}

// MARK: - URL Extensions
extension URL {
    var isImageFile: Bool {
        let imageTypes: [UTType] = [.png, .jpeg, .gif, .bmp, .tiff, .heic]
        return imageTypes.contains { type in
            UTType(filenameExtension: self.pathExtension) == type
        }
    }
}

// MARK: - NSImage Extensions
extension NSImage {
    func resized(to targetSize: NSSize) -> NSImage? {
        let newImage = NSImage(size: targetSize)
        newImage.lockFocus()

        let fromRect = NSRect(origin: .zero, size: self.size)
        let toRect = NSRect(origin: .zero, size: targetSize)

        self.draw(in: toRect, from: fromRect, operation: .copy, fraction: 1.0)
        newImage.unlockFocus()

        return newImage
    }

    func jpegData(compressionQuality: CGFloat = 0.8) -> Data? {
        guard let tiffData = self.tiffRepresentation,
              let bitmap = NSBitmapImageRep(data: tiffData) else {
            return nil
        }

        return bitmap.representation(using: .jpeg, properties: [.compressionFactor: compressionQuality])
    }
}