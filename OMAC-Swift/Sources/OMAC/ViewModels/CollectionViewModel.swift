//
//  CollectionViewModel.swift
//  OMAC
//
//  Created on 2025-11-27
//  View model for managing the action figure collection
//

import Foundation
import SwiftData
import Combine

enum SortOption: String, CaseIterable {
    case name = "name"
    case series = "series"
    case wave = "wave"
    case manufacturer = "manufacturer"
    case year = "year"
    case condition = "condition"

    var displayName: String {
        switch self {
        case .name: return "Name"
        case .series: return "Series"
        case .wave: return "Wave"
        case .manufacturer: return "Manufacturer"
        case .year: return "Year"
        case .condition: return "Condition"
        }
    }
}

@MainActor
class CollectionViewModel: ObservableObject {
    @Published var figures: [ActionFigure] = []
    @Published var wishlistItems: [WishlistItem] = []
    @Published var searchText = ""
    @Published var sortOption: SortOption = .name
    @Published var sortAscending = true

    private var modelContext: ModelContext?

    func setModelContext(_ context: ModelContext) {
        self.modelContext = context
        loadFigures()
        loadWishlist()
    }

    func loadFigures() {
        guard let context = modelContext else { return }

        let descriptor = FetchDescriptor<ActionFigure>(
            sortBy: [SortDescriptor(\ActionFigure.name, order: .forward)]
        )

        do {
            figures = try context.fetch(descriptor)
        } catch {
            print("Error loading figures: \(error)")
            figures = []
        }
    }

    func loadWishlist() {
        guard let context = modelContext else { return }

        let descriptor = FetchDescriptor<WishlistItem>(
            sortBy: [
                SortDescriptor(\WishlistItem.priority, order: .forward),
                SortDescriptor(\WishlistItem.createdAt, order: .reverse)
            ]
        )

        do {
            wishlistItems = try context.fetch(descriptor)
        } catch {
            print("Error loading wishlist: \(error)")
            wishlistItems = []
        }
    }

    func addFigure(_ figure: ActionFigure) {
        guard let context = modelContext else { return }

        context.insert(figure)
        saveContext()
        loadFigures()
    }

    func updateFigure(_ figure: ActionFigure) {
        figure.updatedAt = Date()
        saveContext()
        loadFigures()
    }

    func deleteFigure(_ figure: ActionFigure) {
        guard let context = modelContext else { return }

        context.delete(figure)
        saveContext()
        loadFigures()
    }

    func addPhoto(_ photo: Photo, to figure: ActionFigure) {
        if figure.photos == nil {
            figure.photos = []
        }
        figure.photos?.append(photo)
        figure.updatedAt = Date()
        saveContext()
        loadFigures()
    }

    func removePhoto(_ photo: Photo, from figure: ActionFigure) {
        figure.photos?.removeAll { $0.id == photo.id }
        figure.updatedAt = Date()
        saveContext()
        loadFigures()
    }

    func setPrimaryPhoto(_ photo: Photo, for figure: ActionFigure) {
        // Unset all other primary photos
        if let photos = figure.photos {
            for existingPhoto in photos where existingPhoto.isPrimary {
                existingPhoto.isPrimary = false
            }
        }
        photo.isPrimary = true
        figure.updatedAt = Date()
        saveContext()
        loadFigures()
    }

    // Wishlist methods
    func addWishlistItem(_ item: WishlistItem) {
        guard let context = modelContext else { return }

        context.insert(item)
        saveContext()
        loadWishlist()
    }

    func updateWishlistItem(_ item: WishlistItem) {
        item.updatedAt = Date()
        saveContext()
        loadWishlist()
    }

    func deleteWishlistItem(_ item: WishlistItem) {
        guard let context = modelContext else { return }

        context.delete(item)
        saveContext()
        loadWishlist()
    }

    func moveWishlistToCollection(_ wishlistItem: WishlistItem) -> ActionFigure? {
        // Create a new ActionFigure from the wishlist item
        let figure = ActionFigure(
            name: wishlistItem.name,
            series: wishlistItem.series,
            wave: wishlistItem.wave,
            manufacturer: wishlistItem.manufacturer,
            year: wishlistItem.year,
            scale: wishlistItem.scale,
            purchasePrice: nil, // Will be set when acquired
            location: nil       // Will be set when acquired
        )

        addFigure(figure)
        deleteWishlistItem(wishlistItem)

        return figure
    }

    func searchFigures(query: String) -> [ActionFigure] {
        guard !query.isEmpty else { return figures }

        return figures.filter { figure in
            figure.name.localizedCaseInsensitiveContains(query) ||
            (figure.series?.localizedCaseInsensitiveContains(query) ?? false) ||
            (figure.manufacturer?.localizedCaseInsensitiveContains(query) ?? false) ||
            (figure.wave?.localizedCaseInsensitiveContains(query) ?? false)
        }
    }

    private func saveContext() {
        guard let context = modelContext else { return }

        do {
            try context.save()
        } catch {
            print("Error saving context: \(error)")
        }
    }

    // Computed properties for UI
    var filteredFigures: [ActionFigure] {
        let baseFigures = searchText.isEmpty ? figures : searchFigures(query: searchText)

        return baseFigures.sorted { lhs, rhs in
            let result = compareFigures(lhs, rhs, by: sortOption)
            return sortAscending ? result : !result
        }
    }

    var collectionStats: (total: Int, withPhotos: Int, totalValue: Double, wishlistCount: Int) {
        let total = figures.count
        let withPhotos = figures.filter { $0.photoCount > 0 }.count
        let totalValue = figures.compactMap { $0.purchasePrice }.reduce(0, +)
        let wishlist = wishlistItems.count

        return (total, withPhotos, totalValue, wishlist)
    }

    private func compareFigures(_ lhs: ActionFigure, _ rhs: ActionFigure, by option: SortOption) -> Bool {
        switch option {
        case .name:
            return lhs.name < rhs.name
        case .series:
            return (lhs.series ?? "") < (rhs.series ?? "")
        case .wave:
            return (lhs.wave ?? "") < (rhs.wave ?? "")
        case .manufacturer:
            return (lhs.manufacturer ?? "") < (rhs.manufacturer ?? "")
        case .year:
            return (lhs.year ?? 0) < (rhs.year ?? 0)
        case .condition:
            return (lhs.condition ?? "") < (rhs.condition ?? "")
        }
    }
}