//
//  ActionFigure.swift
//  OMAC
//
//  Created on 2025-11-27
//  Core Data model for action figures
//

import Foundation
import SwiftData

@Model
final class ActionFigure {
    @Attribute(.unique) var id: UUID
    var name: String
    var series: String?
    var wave: String?
    var manufacturer: String?
    var year: Int?
    var scale: String?
    var condition: String?
    var purchasePrice: Double?
    var currentValue: Double?
    var location: String?
    var notes: String?
    var createdAt: Date
    var updatedAt: Date

    // Relationships
    @Relationship(deleteRule: .cascade, inverse: \Photo.figure)
    var photos: [Photo]?

    init(
        id: UUID = UUID(),
        name: String,
        series: String? = nil,
        wave: String? = nil,
        manufacturer: String? = nil,
        year: Int? = nil,
        scale: String? = nil,
        condition: String? = nil,
        purchasePrice: Double? = nil,
        currentValue: Double? = nil,
        location: String? = nil,
        notes: String? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.name = name
        self.series = series
        self.wave = wave
        self.manufacturer = manufacturer
        self.year = year
        self.scale = scale
        self.condition = condition
        self.purchasePrice = purchasePrice
        self.currentValue = currentValue
        self.location = location
        self.notes = notes
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }

    // Computed properties
    var primaryPhoto: Photo? {
        photos?.first(where: { $0.isPrimary })
    }

    var photoCount: Int {
        photos?.count ?? 0
    }

    var displayYear: String {
        year.map { String($0) } ?? "Unknown"
    }

    var displayPrice: String {
        purchasePrice.map { String(format: "$%.2f", $0) } ?? "N/A"
    }
}