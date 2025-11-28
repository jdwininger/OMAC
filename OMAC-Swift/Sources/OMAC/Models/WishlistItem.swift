//
//  WishlistItem.swift
//  OMAC
//
//  Created on 2025-11-27
//  Core Data model for wishlist items
//

import Foundation
import SwiftData
import SwiftUI

@Model
final class WishlistItem {
    @Attribute(.unique) var id: UUID
    var name: String
    var series: String?
    var wave: String?
    var manufacturer: String?
    var year: Int?
    var scale: String?
    var targetPrice: Double?
    var priority: String
    var notes: String?
    var createdAt: Date
    var updatedAt: Date

    init(
        id: UUID = UUID(),
        name: String,
        series: String? = nil,
        wave: String? = nil,
        manufacturer: String? = nil,
        year: Int? = nil,
        scale: String? = nil,
        targetPrice: Double? = nil,
        priority: String = "medium",
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
        self.targetPrice = targetPrice
        self.priority = priority
        self.notes = notes
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }

    // Computed properties
    var displayYear: String {
        year.map { String($0) } ?? "Unknown"
    }

    var displayTargetPrice: String {
        targetPrice.map { String(format: "$%.2f", $0) } ?? "N/A"
    }

    var priorityColor: Color {
        switch priority.lowercased() {
        case "high": return .red
        case "medium": return .orange
        case "low": return .green
        default: return .gray
        }
    }

    var prioritySortOrder: Int {
        switch priority.lowercased() {
        case "high": return 0
        case "medium": return 1
        case "low": return 2
        default: return 3
        }
    }
}