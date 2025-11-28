//
//  PhotoViewerView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for displaying individual photos in full size
//

import SwiftUI

struct PhotoViewerView: View {
    let photo: Photo
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var modelContext

    @State private var caption: String
    @State private var isEditingCaption = false

    init(photo: Photo) {
        self.photo = photo
        _caption = State(initialValue: photo.caption ?? "")
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)

                VStack {
                    // Photo display
                    if let nsImage = NSImage(contentsOf: photo.fileURL) {
                        Image(nsImage: nsImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .padding()
                    } else {
                        VStack {
                            Image(systemName: "photo")
                                .font(.system(size: 64))
                                .foregroundColor(.gray)
                            Text("Photo not found")
                                .foregroundColor(.gray)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    }

                    // Photo info
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("Uploaded")
                                .foregroundColor(.secondary)
                            Spacer()
                            Text(photo.uploadDate.formatted(date: .long, time: .shortened))
                                .foregroundColor(.white)
                        }

                        HStack {
                            Text("File")
                                .foregroundColor(.secondary)
                            Spacer()
                            Text(photo.filename)
                                .foregroundColor(.white)
                                .lineLimit(1)
                        }

                        // Caption editing
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Caption")
                                .foregroundColor(.secondary)

                            if isEditingCaption {
                                TextField("Add a caption...", text: $caption, axis: .vertical)
                                    .textFieldStyle(.roundedBorder)
                                    .lineLimit(3...6)
                                    .onSubmit {
                                        saveCaption()
                                    }
                            } else {
                                if caption.isEmpty {
                                    Text("No caption")
                                        .foregroundColor(.gray)
                                        .italic()
                                        .onTapGesture {
                                            isEditingCaption = true
                                        }
                                } else {
                                    Text(caption)
                                        .foregroundColor(.white)
                                        .onTapGesture {
                                            isEditingCaption = true
                                        }
                                }
                            }
                        }
                    }
                    .padding()
                    .background(Color.black.opacity(0.8))
                }
            }
            .navigationTitle("Photo Viewer")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }

                if isEditingCaption {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") {
                            saveCaption()
                        }
                        .foregroundColor(.blue)
                    }
                }
            }
            .onChange(of: isEditingCaption) { _, newValue in
                if !newValue {
                    saveCaption()
                }
            }
        }
    }

    private func saveCaption() {
        photo.caption = caption.isEmpty ? nil : caption
        isEditingCaption = false

        do {
            try modelContext.save()
        } catch {
            print("Failed to save caption: \(error)")
        }
    }
}

#Preview {
    let previewPhoto = Photo(
        filePath: "/some/path/image.jpg",
        caption: "This is a sample photo caption",
        isPrimary: true
    )

    PhotoViewerView(photo: previewPhoto)
        .environment(\.modelContext, PersistenceController.preview.container.mainContext)
}