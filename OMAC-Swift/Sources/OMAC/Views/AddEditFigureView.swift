//
//  AddEditFigureView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for adding or editing action figures
//

import SwiftUI

struct AddEditFigureView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss

    let figure: ActionFigure?

    @State private var name = ""
    @State private var series = ""
    @State private var wave = ""
    @State private var manufacturer = ""
    @State private var year: Int?
    @State private var scale = ""
    @State private var condition = ""
    @State private var purchasePrice: Double?
    @State private var location = ""
    @State private var notes = ""

    private var isEditing: Bool { figure != nil }
    private var title: String { isEditing ? "Edit Figure" : "Add New Figure" }

    var body: some View {
        NavigationStack {
            Form {
                Section("Basic Information") {
                    TextField("Name", text: $name)
                    TextField("Series", text: $series)
                    TextField("Wave", text: $wave)
                    Picker("Manufacturer", selection: $manufacturer) {
                        Text("Select manufacturer").tag("")
                        Text("Hot Toys").tag("Hot Toys")
                        Text("Sideshow Collectibles").tag("Sideshow Collectibles")
                        Text("Medicom").tag("Medicom")
                        Text("ThreeZero").tag("ThreeZero")
                        Text("Asmus Toys").tag("Asmus Toys")
                        Text("Enterbay").tag("Enterbay")
                        Text("Mezco").tag("Mezco")
                        Text("NECA").tag("NECA")
                        Text("McFarlane Toys").tag("McFarlane Toys")
                        Text("Hasbro").tag("Hasbro")
                        Text("Mattel").tag("Mattel")
                        Text("Bandai").tag("Bandai")
                        Text("Takara Tomy").tag("Takara Tomy")
                        Text("Good Smile Company").tag("Good Smile Company")
                        Text("Kotobukiya").tag("Kotobukiya")
                    }
                }

                Section {
                    TextField("Year", value: $year, format: .number)
                    Picker("Scale", selection: $scale) {
                        Text("Select scale").tag("")
                        Text("1/6").tag("1/6")
                        Text("1/4").tag("1/4")
                        Text("1/8").tag("1/8")
                        Text("1/10").tag("1/10")
                        Text("1/12").tag("1/12")
                        Text("1/18").tag("1/18")
                        Text("3.75\"").tag("3.75\"")
                        Text("6\"").tag("6\"")
                        Text("12\"").tag("12\"")
                    }
                    Picker("Condition", selection: $condition) {
                        Text("Select condition").tag("")
                        Text("Mint in Package").tag("Mint in Package")
                        Text("Mint in Box").tag("Mint in Box")
                        Text("Near Mint").tag("Near Mint")
                        Text("Excellent").tag("Excellent")
                        Text("Very Good").tag("Very Good")
                        Text("Good").tag("Good")
                        Text("Fair").tag("Fair")
                        Text("Poor").tag("Poor")
                    }
                    TextField("Purchase Price", value: $purchasePrice, format: .currency(code: "USD"))
                    Picker("Location", selection: $location) {
                        Text("Select location").tag("")
                        Text("Display Case").tag("Display Case")
                        Text("Shelf").tag("Shelf")
                        Text("Box").tag("Box")
                        Text("Closet").tag("Closet")
                        Text("Garage").tag("Garage")
                        Text("Storage Room").tag("Storage Room")
                        Text("Office").tag("Office")
                        Text("Living Room").tag("Living Room")
                        Text("Bedroom").tag("Bedroom")
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
                        saveFigure()
                    }
                    .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
        }
        .frame(minWidth: 450, minHeight: 600)
        .onAppear {
            loadFigureData()
        }
    }

    private func loadFigureData() {
        if let figure = figure {
            name = figure.name
            series = figure.series ?? ""
            wave = figure.wave ?? ""
            manufacturer = figure.manufacturer ?? ""
            year = figure.year
            scale = figure.scale ?? ""
            condition = figure.condition ?? ""
            purchasePrice = figure.purchasePrice
            location = figure.location ?? ""
            notes = figure.notes ?? ""
        }
    }

    private func saveFigure() {
        let trimmedName = name.trimmingCharacters(in: .whitespaces)

        if isEditing, let existingFigure = figure {
            // Update existing figure
            existingFigure.name = trimmedName
            existingFigure.series = series.isEmpty ? nil : series
            existingFigure.wave = wave.isEmpty ? nil : wave
            existingFigure.manufacturer = manufacturer.isEmpty ? nil : manufacturer
            existingFigure.year = year
            existingFigure.scale = scale.isEmpty ? nil : scale
            existingFigure.condition = condition.isEmpty ? nil : condition
            existingFigure.purchasePrice = purchasePrice
            existingFigure.location = location.isEmpty ? nil : location
            existingFigure.notes = notes.isEmpty ? nil : notes
            existingFigure.updatedAt = Date()
        } else {
            // Create new figure
            let newFigure = ActionFigure(
                name: trimmedName,
                series: series.isEmpty ? nil : series,
                wave: wave.isEmpty ? nil : wave,
                manufacturer: manufacturer.isEmpty ? nil : manufacturer,
                year: year,
                scale: scale.isEmpty ? nil : scale,
                condition: condition.isEmpty ? nil : condition,
                purchasePrice: purchasePrice,
                location: location.isEmpty ? nil : location,
                notes: notes.isEmpty ? nil : notes
            )
            modelContext.insert(newFigure)
        }

        do {
            try modelContext.save()
            dismiss()
        } catch {
            print("Error saving figure: \(error)")
            // In a real app, you'd show an error alert here
        }
    }
}

#Preview {
    AddEditFigureView(figure: nil)
        .modelContainer(PersistenceController.preview.container)
}