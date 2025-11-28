//
//  Photo.swift
//  OMAC
//
//  Created on 2025-11-27
//  Core Data model for photos
//

import Foundation
import SwiftData

@Model
final class Photo {
    @Attribute(.unique) var id: UUID
    var filePath: String
    var caption: String?
    var isPrimary: Bool
    var uploadDate: Date

    // Relationships
    var figure: ActionFigure?

    init(
        id: UUID = UUID(),
        filePath: String,
        caption: String? = nil,
        isPrimary: Bool = false,
        uploadDate: Date = Date(),
        figure: ActionFigure? = nil
    ) {
        self.id = id
        self.filePath = filePath
        self.caption = caption
        self.isPrimary = isPrimary
        self.uploadDate = uploadDate
        self.figure = figure
    }

    // Computed properties
    var filename: String {
        URL(fileURLWithPath: filePath).lastPathComponent
    }

    var fileURL: URL {
        URL(fileURLWithPath: filePath)
    }

    var exists: Bool {
        FileManager.default.fileExists(atPath: filePath)
    }
}