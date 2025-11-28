//
//  FigureDetailView.swift
//  OMAC
//
//  Created on 2025-11-27
//  Detail view for displaying action figure information
//

import SwiftUI

struct FigureDetailView: View {
    let figure: ActionFigure

    @State private var showingEditSheet = false
    @State private var showingPhotoGallery = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header
                HStack {
                    VStack(alignment: .leading) {
                        Text(figure.name)
                            .font(.largeTitle)
                            .fontWeight(.bold)

                        if let series = figure.series {
                            Text(series)
                                .font(.title2)
                                .foregroundColor(.secondary)
                        }

                        if let wave = figure.wave {
                            Text("Wave: \(wave)")
                                .font(.title3)
                                .foregroundColor(.secondary)
                        }
                    }

                    Spacer()

                    Button(action: { showingEditSheet = true }) {
                        Label("Edit", systemImage: "pencil")
                    }
                    .buttonStyle(.bordered)
                }

                // Photo section
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Photos")
                            .font(.headline)

                        Spacer()

                        Button(action: { showingPhotoGallery = true }) {
                            Label("Manage Photos", systemImage: "photo.on.rectangle.angled")
                        }
                        .buttonStyle(.bordered)
                    }

                    if let photos = figure.photos, !photos.isEmpty {
                        // Show primary photo or first photo
                        if let primaryPhoto = figure.primaryPhoto ?? photos.first, primaryPhoto.exists {
                            ZStack(alignment: .bottomTrailing) {
                                PhotoView(photo: primaryPhoto)

                                // Photo count badge
                                if photos.count > 1 {
                                    Text("\(photos.count)")
                                        .font(.caption)
                                        .fontWeight(.bold)
                                        .foregroundColor(.white)
                                        .padding(6)
                                        .background(Color.black.opacity(0.7))
                                        .clipShape(Circle())
                                        .padding(8)
                                }
                            }
                        } else {
                            ZStack {
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.secondary.opacity(0.1))
                                    .frame(height: 200)

                                VStack {
                                    Image(systemName: "photo")
                                        .font(.largeTitle)
                                        .foregroundColor(.secondary)
                                    Text("Photos not found")
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    } else {
                        ZStack {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.secondary.opacity(0.1))
                                .frame(height: 200)

                            VStack {
                                Image(systemName: "photo")
                                    .font(.largeTitle)
                                    .foregroundColor(.secondary)
                                Text("No photos")
                                    .foregroundColor(.secondary)
                                Button("Add Photos") {
                                    showingPhotoGallery = true
                                }
                                .buttonStyle(.bordered)
                                .padding(.top, 8)
                            }
                        }
                    }
                }

                // Details grid
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                    DetailRow(label: "Manufacturer", value: figure.manufacturer ?? "Unknown")
                    DetailRow(label: "Year", value: figure.displayYear)
                    DetailRow(label: "Scale", value: figure.scale ?? "Unknown")
                    DetailRow(label: "Condition", value: figure.condition ?? "Unknown")
                    DetailRow(label: "Purchase Price", value: figure.displayPrice)
                    DetailRow(label: "Location", value: figure.location ?? "Unknown")
                }

                // Notes
                if let notes = figure.notes, !notes.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Notes")
                            .font(.headline)

                        Text(notes)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                // Metadata
                VStack(alignment: .leading, spacing: 4) {
                    Text("Added: \(figure.createdAt.formatted(date: .long, time: .shortened))")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if figure.updatedAt != figure.createdAt {
                        Text("Updated: \(figure.updatedAt.formatted(date: .long, time: .shortened))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
        }
        .navigationTitle(figure.name)
        .sheet(isPresented: $showingEditSheet) {
            AddEditFigureView(figure: figure)
        }
        .sheet(isPresented: $showingPhotoGallery) {
            PhotoGalleryView(figure: figure)
        }
    }
}

struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
                .textCase(.uppercase)

            Text(value)
                .font(.body)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct PhotoView: View {
    let photo: Photo

    var body: some View {
        if let nsImage = NSImage(contentsOf: photo.fileURL) {
            Image(nsImage: nsImage)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(maxHeight: 300)
                .cornerRadius(8)
                .shadow(radius: 2)
        } else {
            Text("Photo not found")
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    let previewFigure = ActionFigure(
        name: "Iron Man",
        series: "Marvel Legends",
        wave: "Wave 1",
        manufacturer: "Hasbro",
        year: 2023,
        condition: "Mint in Package",
        notes: "This is a detailed action figure with multiple accessories."
    )

    FigureDetailView(figure: previewFigure)
        .frame(width: 600, height: 800)
}