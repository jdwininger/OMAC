//
//  UserPreferences.swift
//  OMAC
//
//  Service for managing user preferences like manufacturers and locations
//

import Foundation

class UserPreferences {
    static let shared = UserPreferences()

    private let manufacturersKey = "savedManufacturers"
    private let locationsKey = "savedLocations"

    // Default manufacturers
    private let defaultManufacturers = [
        "Hot Toys",
        "Sideshow Collectibles",
        "Medicom",
        "ThreeZero",
        "Asmus Toys",
        "Enterbay",
        "Mezco",
        "NECA",
        "McFarlane Toys",
        "Hasbro",
        "Mattel",
        "Bandai",
        "Takara Tomy",
        "Good Smile Company",
        "Kotobukiya",
        "Diamond Select Toys",
        "Funko",
        "Prime 1 Studio",
        "XM Studios"
    ]

    // Default locations
    private let defaultLocations = [
        "Display Case",
        "Display Shelf",
        "Closet",
        "Garage",
        "Storage Room",
        "Living Room",
        "Bedroom",
        "Jeremy's House",
        "Mike's House",
        "Storage Tub",
        "Attic",
        "Basement"
    ]

    // Default conditions
    private let defaultConditions = [
        "Unopened Packaging",
        "Open Box Complete",
        "Open Box Incomplete",
        "Loose Complete",
        "Loose Incomplete",
        "Loose Figure Only"
    ]

    private init() {}

    // MARK: - Manufacturers

    func getManufacturers() -> [String] {
        let saved = UserDefaults.standard.stringArray(forKey: manufacturersKey) ?? []
        return defaultManufacturers + saved
    }

    func addManufacturer(_ manufacturer: String) {
        var saved = UserDefaults.standard.stringArray(forKey: manufacturersKey) ?? []
        let trimmed = manufacturer.trimmingCharacters(in: .whitespacesAndNewlines)

        // Don't add if it already exists (case-insensitive)
        if !saved.contains(where: { $0.lowercased() == trimmed.lowercased() }) &&
           !defaultManufacturers.contains(where: { $0.lowercased() == trimmed.lowercased() }) {
            saved.append(trimmed)
            UserDefaults.standard.set(saved, forKey: manufacturersKey)
        }
    }

    // MARK: - Locations

    func getLocations() -> [String] {
        let saved = UserDefaults.standard.stringArray(forKey: locationsKey) ?? []
        return defaultLocations + saved
    }

    func addLocation(_ location: String) {
        var saved = UserDefaults.standard.stringArray(forKey: locationsKey) ?? []
        let trimmed = location.trimmingCharacters(in: .whitespacesAndNewlines)

        // Don't add if it already exists (case-insensitive)
        if !saved.contains(where: { $0.lowercased() == trimmed.lowercased() }) &&
           !defaultLocations.contains(where: { $0.lowercased() == trimmed.lowercased() }) {
            saved.append(trimmed)
            UserDefaults.standard.set(saved, forKey: locationsKey)
        }
    }

    // MARK: - Conditions

    func getConditions() -> [String] {
        let saved = UserDefaults.standard.stringArray(forKey: "savedConditions") ?? []
        return defaultConditions + saved
    }

    func addCondition(_ condition: String) {
        var saved = UserDefaults.standard.stringArray(forKey: "savedConditions") ?? []
        let trimmed = condition.trimmingCharacters(in: .whitespacesAndNewlines)

        // Don't add if it already exists (case-insensitive)
        if !saved.contains(where: { $0.lowercased() == trimmed.lowercased() }) &&
           !defaultConditions.contains(where: { $0.lowercased() == trimmed.lowercased() }) {
            saved.append(trimmed)
            UserDefaults.standard.set(saved, forKey: "savedConditions")
        }
    }

    // MARK: - Backup/Restore

    func exportPreferences() -> [String: [String]] {
        return [
            manufacturersKey: UserDefaults.standard.stringArray(forKey: manufacturersKey) ?? [],
            locationsKey: UserDefaults.standard.stringArray(forKey: locationsKey) ?? [],
            "savedConditions": UserDefaults.standard.stringArray(forKey: "savedConditions") ?? []
        ]
    }

    func importPreferences(_ preferences: [String: [String]]) {
        if let manufacturers = preferences[manufacturersKey] {
            UserDefaults.standard.set(manufacturers, forKey: manufacturersKey)
        }
        if let locations = preferences[locationsKey] {
            UserDefaults.standard.set(locations, forKey: locationsKey)
        }
        if let conditions = preferences["savedConditions"] {
            UserDefaults.standard.set(conditions, forKey: "savedConditions")
        }
    }
}