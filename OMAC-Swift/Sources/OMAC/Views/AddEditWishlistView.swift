//
//  AddEditWishlistView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for adding or editing wishlist items
//

import SwiftUI

struct AddEditWishlistView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = CollectionViewModel()

    let item: WishlistItem?

    @State private var name = ""
    @State private var series = ""
    @State private var wave = ""
    @State private var manufacturer = ""
    @State private var year: Int?
    @State private var scale = ""
    @State private var targetPrice: Double?
    @State private var priority = "medium"
    @State private var notes = ""

    private var isEditing: Bool { item != nil }
    private var title: String { isEditing ? "Edit Wishlist Item" : "Add to Wishlist" }

    var body: some View {
        NavigationStack {
            Form {
                Section("Basic Information") {
                    TextField("Name", text: $name)
                        .textFieldStyle(.roundedBorder)

                    TextField("Series", text: $series)
                        .textFieldStyle(.roundedBorder)

                    TextField("Wave", text: $wave)
                        .textFieldStyle(.roundedBorder)

                    TextField("Manufacturer", text: $manufacturer)
                        .textFieldStyle(.roundedBorder)
                }

                Section("Details") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Year")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        TextField("Year", value: $year, format: .number)
                            .textFieldStyle(.roundedBorder)
                    }

                    TextField("Scale (e.g., 1/6, 1/12)", text: $scale)
                        .textFieldStyle(.roundedBorder)

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Priority")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Picker("", selection: $priority) {
                            Text("Low").tag("low")
                            Text("Medium").tag("medium")
                            Text("High").tag("high")
                        }
                        .pickerStyle(.segmented)
                    }
                }

                Section("Pricing") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Target Price")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        TextField("Target Price", value: $targetPrice, format: .currency(code: "USD"))
                            .textFieldStyle(.roundedBorder)
                    }
                }

                Section("Notes") {
                    TextEditor(text: $notes)
                        .frame(minHeight: 100)
                }
            }
            .navigationTitle(title)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button(isEditing ? "Update" : "Add") {
                        saveItem()
                    }
                    .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
        }
        .frame(minWidth: 400, minHeight: 600)
        .onAppear {
            loadItemData()
            viewModel.setModelContext(modelContext)
        }
    }

    private func loadItemData() {
        if let item = item {
            name = item.name
            series = item.series ?? ""
            wave = item.wave ?? ""
            manufacturer = item.manufacturer ?? ""
            year = item.year
            scale = item.scale ?? ""
            targetPrice = item.targetPrice
            priority = item.priority
            notes = item.notes ?? ""
        }
    }

    private func saveItem() {
        let trimmedName = name.trimmingCharacters(in: .whitespaces)

        if isEditing, let existingItem = item {
            // Update existing item
            existingItem.name = trimmedName
            existingItem.series = series.isEmpty ? nil : series
            existingItem.wave = wave.isEmpty ? nil : wave
            existingItem.manufacturer = manufacturer.isEmpty ? nil : manufacturer
            existingItem.year = year
            existingItem.scale = scale.isEmpty ? nil : scale
            existingItem.targetPrice = targetPrice
            existingItem.priority = priority
            existingItem.notes = notes.isEmpty ? nil : notes
            existingItem.updatedAt = Date()

            viewModel.updateWishlistItem(existingItem)
        } else {
            // Create new item
            let newItem = WishlistItem(
                name: trimmedName,
                series: series.isEmpty ? nil : series,
                wave: wave.isEmpty ? nil : wave,
                manufacturer: manufacturer.isEmpty ? nil : manufacturer,
                year: year,
                scale: scale.isEmpty ? nil : scale,
                targetPrice: targetPrice,
                priority: priority,
                notes: notes.isEmpty ? nil : notes
            )
            viewModel.addWishlistItem(newItem)
        }

        dismiss()
    }
}

#Preview {
    AddEditWishlistView(item: nil)
        .modelContainer(PersistenceController.preview.container)
}