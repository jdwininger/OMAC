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

    // Manufacturer management
    @State private var manufacturers: [String] = []
    @State private var showingAddManufacturer = false
    @State private var newManufacturerName = ""

    private var isEditing: Bool { item != nil }
    private var title: String { isEditing ? "Edit Wishlist Item" : "Add to Wishlist" }

    var body: some View {
        VStack(spacing: 20) {
            // Title
            Text(title)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.primary)

            ScrollView {
                VStack(spacing: 20) {
                    // Basic Information Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Basic Information")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)

                        VStack(spacing: 8) {
                            TextField("Name", text: $name)
                                .textFieldStyle(.roundedBorder)

                            TextField("Series", text: $series)
                                .textFieldStyle(.roundedBorder)

                            TextField("Wave", text: $wave)
                                .textFieldStyle(.roundedBorder)

                            HStack {
                                Picker("Manufacturer", selection: $manufacturer) {
                                    Text("Select manufacturer").tag("")
                                    ForEach(manufacturers, id: \.self) { manufacturerName in
                                        Text(manufacturerName).tag(manufacturerName)
                                    }
                                }
                                Button(action: { showingAddManufacturer = true }) {
                                    Image(systemName: "plus")
                                        .font(.system(size: 16, weight: .bold))
                                        .foregroundColor(.blue)
                                        .frame(width: 24, height: 24)
                                }
                                .buttonStyle(.bordered)
                                .controlSize(.small)
                            }
                        }
                    }

                    // Details Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Details")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)

                        VStack(spacing: 8) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Year")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                TextField("Year", value: $year, format: .number.grouping(.never))
                                    .textFieldStyle(.roundedBorder)
                            }

                            TextField("Scale (e.g., 1/6, 1/12)", text: $scale)
                                .textFieldStyle(.roundedBorder)

                            VStack(alignment: .leading, spacing: 4) {
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
                    }

                    // Pricing Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Pricing")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)

                        VStack(alignment: .leading, spacing: 4) {
                            Text("Target Price")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            TextField("Target Price", value: $targetPrice, format: .currency(code: "USD"))
                                .textFieldStyle(.roundedBorder)
                        }
                    }

                    // Notes Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Notes")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)

                        TextEditor(text: $notes)
                            .frame(minHeight: 100)
                            .overlay(
                                RoundedRectangle(cornerRadius: 4)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )
                    }
                }
                .padding(.horizontal)
            }

            // Buttons
            HStack(spacing: 12) {
                Spacer()
                Button("Cancel") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
                Button(isEditing ? "Update" : "Add") {
                    saveItem()
                }
                .keyboardShortcut(.defaultAction)
                .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            }
        }
        .padding(20)
        .frame(width: 500, height: 600)
        .background(Color(NSColor.windowBackgroundColor))
        .onAppear {
            loadItemData()
            loadUserPreferences()
        }
        .sheet(isPresented: $showingAddManufacturer) {
            AddItemSheet(
                title: "Add Manufacturer",
                placeholder: "Manufacturer name",
                text: $newManufacturerName,
                onSave: {
                    if !newManufacturerName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        UserPreferences.shared.addManufacturer(newManufacturerName)
                        manufacturers = UserPreferences.shared.getManufacturers()
                        manufacturer = newManufacturerName
                        newManufacturerName = ""
                    }
                    showingAddManufacturer = false
                },
                onCancel: {
                    newManufacturerName = ""
                    showingAddManufacturer = false
                }
            )
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

    private func loadUserPreferences() {
        manufacturers = UserPreferences.shared.getManufacturers()
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