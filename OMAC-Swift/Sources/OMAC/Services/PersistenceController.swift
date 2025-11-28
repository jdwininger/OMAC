//
//  PersistenceController.swift
//  OMAC
//
//  Created on 2025-11-27
//  SwiftData persistence controller
//

import SwiftData
import Foundation

struct PersistenceController {
    static let shared = PersistenceController()

    let container: ModelContainer

    init(inMemory: Bool = false) {
        do {
            let config: ModelConfiguration
            if inMemory {
                config = ModelConfiguration(isStoredInMemoryOnly: true)
            } else {
                // Set up data directory in Application Support
                let fileManager = FileManager.default
                let appSupportURL = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
                let omacDirectory = appSupportURL.appendingPathComponent("OMAC")

                try? fileManager.createDirectory(at: omacDirectory, withIntermediateDirectories: true)

                let storeURL = omacDirectory.appendingPathComponent("OMAC.store")
                config = ModelConfiguration(url: storeURL)
            }

            container = try ModelContainer(
                for: ActionFigure.self, Photo.self, WishlistItem.self,
                configurations: config
            )
        } catch {
            fatalError("Failed to create ModelContainer: \(error.localizedDescription)")
        }
    }

    // Preview helper for SwiftUI previews
    static var preview: PersistenceController = {
        let result = PersistenceController(inMemory: true)
        let modelContext = ModelContext(result.container)

        // Create sample data for previews
        for i in 1...5 {
            let figure = ActionFigure(
                name: "Sample Figure \(i)",
                series: "Sample Series",
                wave: "Wave \(i)",
                manufacturer: "Manufacturer \(i)",
                year: 2020 + i,
                condition: "Mint"
            )
            modelContext.insert(figure)
        }

        do {
            try modelContext.save()
        } catch {
            fatalError("Failed to save preview data: \(error.localizedDescription)")
        }

        return result
    }()
}