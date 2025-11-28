//
//  AddEditFigureView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for adding or editing action figures
//

import SwiftUI
import UniformTypeIdentifiers

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

    // Manufacturer and Location management
    @State private var manufacturers: [String] = []
    @State private var locations: [String] = []
    @State private var conditions: [String] = []
    @State private var showingAddManufacturer = false
    @State private var showingAddLocation = false
    @State private var showingAddCondition = false
    @State private var newManufacturerName = ""
    @State private var newLocationName = ""
    @State private var newConditionName = ""

    // Photo management
    @State private var selectedPhotoURLs: [URL] = []
    @State private var pendingPhotos: [Photo] = []  // Existing photos when editing
    @State private var newlyAddedPhotos: [Photo] = []  // New photos added during this session
    @State private var isTargeted = false

    private var allPhotos: [Photo] {
        pendingPhotos + newlyAddedPhotos
    }

    private var hasPhotosToShow: Bool {
        !pendingPhotos.isEmpty || !newlyAddedPhotos.isEmpty
    }

    private var isEditing: Bool { figure != nil }
    private var title: String { isEditing ? "Edit Figure" : "Add New Figure" }

    var body: some View {
        NavigationStack {
            Form {
                Section("Basic Information") {
                    TextField("Name", text: $name)
                    TextField("Series", text: $series)
                    TextField("Wave", text: $wave)
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

                Section {
                    TextField("Year", value: $year, format: .number.grouping(.never))
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
                    HStack {
                        Picker("Condition", selection: $condition) {
                            Text("Select condition").tag("")
                            ForEach(conditions, id: \.self) { conditionName in
                                Text(conditionName).tag(conditionName)
                            }
                        }
                        Button(action: { showingAddCondition = true }) {
                            Image(systemName: "plus")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.blue)
                                .frame(width: 24, height: 24)
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                    }
                    TextField("Purchase Price", value: $purchasePrice, format: .currency(code: "USD"))
                    HStack {
                        Picker("Location", selection: $location) {
                            Text("Select location").tag("")
                            ForEach(locations, id: \.self) { locationName in
                                Text(locationName).tag(locationName)
                            }
                        }
                        Button(action: { showingAddLocation = true }) {
                            Image(systemName: "plus")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.blue)
                                .frame(width: 24, height: 24)
                        }
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                    }
                }

                Section("Notes") {
                    TextEditor(text: $notes)
                        .frame(minHeight: 100)
                }

                Section("Photos") {
                    if hasPhotosToShow {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Photos: \(allPhotos.count)")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            ScrollView(.horizontal) {
                                HStack(spacing: 8) {
                                    ForEach(allPhotos, id: \.id) { photo in
                                        if let nsImage = NSImage(contentsOf: photo.fileURL) {
                                            ZStack(alignment: .topTrailing) {
                                                Image(nsImage: nsImage)
                                                    .resizable()
                                                    .aspectRatio(contentMode: .fill)
                                                    .frame(width: 60, height: 60)
                                                    .clipped()
                                                    .cornerRadius(4)

                                                // Only show remove button for newly added photos
                                                if newlyAddedPhotos.contains(where: { $0.id == photo.id }) {
                                                    Button(action: { removePendingPhoto(photo) }) {
                                                        Image(systemName: "xmark.circle.fill")
                                                            .foregroundColor(.red)
                                                            .background(Color.white.opacity(0.8))
                                                            .clipShape(Circle())
                                                    }
                                                    .offset(x: 5, y: -5)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    VStack(spacing: 12) {
                        // Drag and drop area
                        ZStack {
                            RoundedRectangle(cornerRadius: 8)
                                .strokeBorder(isTargeted ? Color.blue : Color.gray.opacity(0.3), lineWidth: 2)
                                .background(isTargeted ? Color.blue.opacity(0.1) : Color.gray.opacity(0.05))
                                .frame(height: 80)

                            VStack(spacing: 4) {
                                Image(systemName: "photo.on.rectangle.angled")
                                    .font(.system(size: 24))
                                    .foregroundColor(isTargeted ? .blue : .gray)
                                Text(isTargeted ? "Drop photos here" : "Drag & drop photos here")
                                    .font(.caption)
                                    .foregroundColor(isTargeted ? .blue : .gray)
                            }
                        }
                        .onDrop(of: [.fileURL], isTargeted: $isTargeted) { providers in
                            handleDrop(providers: providers)
                        }

                        // Browse files button
                        Button(action: browseFiles) {
                            Label("Browse Files", systemImage: "folder")
                        }
                        .buttonStyle(.bordered)
                    }
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
                        Task {
                            await saveFigure()
                        }
                    }
                    .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
        }
        .frame(minWidth: 450, minHeight: 600)
        .padding(.trailing, 25)
        .onAppear {
            loadFigureData()
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
        .sheet(isPresented: $showingAddLocation) {
            AddItemSheet(
                title: "Add Location",
                placeholder: "Location name",
                text: $newLocationName,
                onSave: {
                    if !newLocationName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        UserPreferences.shared.addLocation(newLocationName)
                        locations = UserPreferences.shared.getLocations()
                        location = newLocationName
                        newLocationName = ""
                    }
                    showingAddLocation = false
                },
                onCancel: {
                    newLocationName = ""
                    showingAddLocation = false
                }
            )
        }
        .sheet(isPresented: $showingAddCondition) {
            AddItemSheet(
                title: "Add Condition",
                placeholder: "Condition name",
                text: $newConditionName,
                onSave: {
                    if !newConditionName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        UserPreferences.shared.addCondition(newConditionName)
                        conditions = UserPreferences.shared.getConditions()
                        condition = newConditionName
                        newConditionName = ""
                    }
                    showingAddCondition = false
                },
                onCancel: {
                    newConditionName = ""
                    showingAddCondition = false
                }
            )
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

            // Load existing photos if editing
            if let photos = figure.photos {
                pendingPhotos = photos
                newlyAddedPhotos = []  // Start with no new photos
            }
        }
    }

    private func loadUserPreferences() {
        manufacturers = UserPreferences.shared.getManufacturers()
        locations = UserPreferences.shared.getLocations()
        conditions = UserPreferences.shared.getConditions()
    }

    private func saveFigure() async {
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

            // Save any newly added photos and add them to the figure
            for photo in newlyAddedPhotos {
                do {
                    let fileURL = URL(fileURLWithPath: photo.filePath)
                    let savedPhoto = try await PhotoManager.shared.savePhoto(from: fileURL, for: existingFigure)
                    if existingFigure.photos == nil {
                        existingFigure.photos = []
                    }
                    existingFigure.photos?.append(savedPhoto)
                } catch {
                    print("Failed to save photo for existing figure: \(error)")
                }
            }
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

            // Save pending photos and associate them with the new figure
            for photo in pendingPhotos {
                do {
                    let fileURL = URL(fileURLWithPath: photo.filePath)
                    let savedPhoto = try await PhotoManager.shared.savePhoto(from: fileURL, for: newFigure)
                    if newFigure.photos == nil {
                        newFigure.photos = []
                    }
                    newFigure.photos?.append(savedPhoto)
                } catch {
                    print("Failed to save photo for new figure: \(error)")
                }
            }

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

    private func browseFiles() {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = true
        panel.canChooseDirectories = false
        panel.canChooseFiles = true
        panel.allowedContentTypes = [.image]

        if panel.runModal() == .OK {
            addPhotos(from: panel.urls)
        }
    }

    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        var urls: [URL] = []

        for provider in providers {
            if provider.hasItemConformingToTypeIdentifier(UTType.fileURL.identifier) {
                provider.loadItem(forTypeIdentifier: UTType.fileURL.identifier, options: nil) { item, error in
                    if let data = item as? Data,
                       let url = URL(dataRepresentation: data, relativeTo: nil),
                       url.isImageFile {
                        DispatchQueue.main.async {
                            urls.append(url)
                        }
                    }
                }
            }
        }

        // Process URLs after a short delay to allow async loading to complete
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            if !urls.isEmpty {
                addPhotos(from: urls)
            }
        }

        return true
    }

    private func addPhotos(from urls: [URL]) {
        for url in urls where url.isImageFile {
            // Create a temporary Photo object with the file URL
            let photo = Photo(
                filePath: url.path,
                figure: nil  // Will be set when figure is saved
            )
            newlyAddedPhotos.append(photo)
        }
    }

    private func removePendingPhoto(_ photo: Photo) {
        newlyAddedPhotos.removeAll { $0.id == photo.id }
    }
}

struct AddItemSheet: View {
    let title: String
    let placeholder: String
    @Binding var text: String
    let onSave: () -> Void
    let onCancel: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            // Title
            Text(title)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.primary)

            // Text field
            TextField(placeholder, text: $text)
                .textFieldStyle(.roundedBorder)
                .frame(width: 250)
                .onSubmit {
                    if !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        onSave()
                    }
                }

            // Buttons
            HStack(spacing: 12) {
                Spacer()
                Button("Cancel", action: onCancel)
                    .keyboardShortcut(.cancelAction)
                Button("Add") {
                    onSave()
                }
                .keyboardShortcut(.defaultAction)
                .disabled(text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }
        }
        .padding(20)
        .frame(width: 300, height: 140)
        .background(Color(NSColor.windowBackgroundColor))
    }
}

#Preview {
    AddEditFigureView(figure: nil)
        .modelContainer(PersistenceController.preview.container)
}