//
//  PhotoGalleryView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for managing photos of an action figure
//

import SwiftUI
import PhotosUI

struct PhotoGalleryView: View {
    let figure: ActionFigure
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = CollectionViewModel()

    @State private var selectedPhoto: Photo?
    @State private var showingPhotoPicker = false
    @State private var showingDeleteConfirmation = false
    @State private var photoToDelete: Photo?

    private let columns = [
        GridItem(.adaptive(minimum: 150, maximum: 200), spacing: 16)
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header
                    HStack {
                        Text("\(figure.name) - Photos")
                            .font(.title)
                            .fontWeight(.bold)

                        Spacer()

                        Button(action: { showingPhotoPicker = true }) {
                            Label("Add Photo", systemImage: "plus")
                        }
                        .buttonStyle(.borderedProminent)
                    }

                    // Photo count
                    if let photos = figure.photos, !photos.isEmpty {
                        Text("\(photos.count) photo\(photos.count == 1 ? "" : "s")")
                            .foregroundColor(.secondary)
                    }

                    // Photo grid
                    if let photos = figure.photos, !photos.isEmpty {
                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(photos.sorted(by: { $0.uploadDate > $1.uploadDate }), id: \.id) { photo in
                                PhotoGridItem(
                                    photo: photo,
                                    isPrimary: photo.isPrimary,
                                    onSelect: { selectedPhoto = photo },
                                    onSetPrimary: { setPrimaryPhoto(photo) },
                                    onDelete: {
                                        photoToDelete = photo
                                        showingDeleteConfirmation = true
                                    }
                                )
                            }
                        }
                    } else {
                        // Empty state
                        VStack(spacing: 16) {
                            Image(systemName: "photo.on.rectangle.angled")
                                .font(.system(size: 64))
                                .foregroundColor(.secondary)

                            Text("No photos yet")
                                .font(.title2)
                                .foregroundColor(.secondary)

                            Text("Add photos to document your collection")
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)

                            Button(action: { showingPhotoPicker = true }) {
                                Label("Add First Photo", systemImage: "plus")
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        .frame(maxWidth: .infinity, minHeight: 300)
                    }
                }
                .padding()
            }
            .navigationTitle("Photo Gallery")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .photosPicker(
                isPresented: $showingPhotoPicker,
                selection: .init(get: { [] }, set: { urls in
                    Task {
                        await addPhotos(from: urls)
                    }
                }),
                matching: .images
            )
            .alert("Delete Photo", isPresented: $showingDeleteConfirmation) {
                Button("Cancel", role: .cancel) {
                    photoToDelete = nil
                }
                Button("Delete", role: .destructive) {
                    if let photo = photoToDelete {
                        deletePhoto(photo)
                    }
                    photoToDelete = nil
                }
            } message: {
                Text("Are you sure you want to delete this photo? This action cannot be undone.")
            }
            .sheet(item: $selectedPhoto) { photo in
                PhotoViewerView(photo: photo)
            }
        }
        .onAppear {
            viewModel.setModelContext(modelContext)
        }
        .frame(minWidth: 600, minHeight: 500)
    }

    private func addPhotos(from urls: [PhotosPickerItem]) async {
        for item in urls {
            do {
                if let data = try await item.loadTransferable(type: Data.self),
                   let nsImage = NSImage(data: data) {
                    // Save the image data to a temporary file first
                    let tempURL = FileManager.default.temporaryDirectory
                        .appendingPathComponent(UUID().uuidString)
                        .appendingPathExtension("jpg")

                    if let jpegData = nsImage.jpegData() {
                        try jpegData.write(to: tempURL)

                        // Use PhotoManager to save the photo
                        let photo = try await PhotoManager.shared.savePhoto(from: tempURL, for: figure)

                        // Add to the figure using view model
                        viewModel.addPhoto(photo, to: figure)

                        // Clean up temp file
                        try? FileManager.default.removeItem(at: tempURL)
                    }
                }
            } catch {
                print("Failed to add photo: \(error)")
                // In a real app, you'd show an error alert
            }
        }
    }

    private func setPrimaryPhoto(_ photo: Photo) {
        viewModel.setPrimaryPhoto(photo, for: figure)
    }

    private func deletePhoto(_ photo: Photo) {
        do {
            // Remove from figure's photos array
            viewModel.removePhoto(photo, from: figure)

            // Delete the file
            try PhotoManager.shared.deletePhoto(photo)
        } catch {
            print("Failed to delete photo: \(error)")
        }
    }
}

struct PhotoGridItem: View {
    let photo: Photo
    let isPrimary: Bool
    let onSelect: () -> Void
    let onSetPrimary: () -> Void
    let onDelete: () -> Void

    @State private var showingMenu = false

    var body: some View {
        ZStack(alignment: .topTrailing) {
            // Photo thumbnail
            if let nsImage = NSImage(contentsOf: photo.fileURL) {
                Image(nsImage: nsImage)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 150)
                    .clipped()
                    .cornerRadius(8)
                    .shadow(radius: 2)
                    .onTapGesture {
                        onSelect()
                    }
            } else {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.secondary.opacity(0.2))
                        .frame(height: 150)

                    VStack {
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.secondary)
                        Text("Not found")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // Primary photo indicator
            if isPrimary {
                Image(systemName: "star.fill")
                    .foregroundColor(.yellow)
                    .padding(6)
                    .background(Color.black.opacity(0.7))
                    .clipShape(Circle())
                    .offset(x: -8, y: 8)
            }

            // Menu button
            Menu {
                if !isPrimary {
                    Button(action: onSetPrimary) {
                        Label("Set as Primary", systemImage: "star")
                    }
                }

                Button(role: .destructive, action: onDelete) {
                    Label("Delete Photo", systemImage: "trash")
                }
            } label: {
                Image(systemName: "ellipsis.circle.fill")
                    .foregroundColor(.white)
                    .padding(6)
                    .background(Color.black.opacity(0.7))
                    .clipShape(Circle())
            }
            .offset(x: -8, y: 8)
        }
    }
}

#Preview {
    let previewFigure = ActionFigure(
        name: "Iron Man",
        series: "Marvel Legends",
        manufacturer: "Hasbro"
    )

    PhotoGalleryView(figure: previewFigure)
        .modelContainer(PersistenceController.preview.container)
}