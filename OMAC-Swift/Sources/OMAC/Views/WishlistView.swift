//
//  WishlistView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for managing wishlist items
//

import SwiftUI

struct WishlistView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = CollectionViewModel()

    @State private var showingAddItem = false
    @State private var selectedItem: WishlistItem?

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("Wishlist")
                        .font(.title)
                        .fontWeight(.bold)

                    Spacer()

                    Button(action: { showingAddItem = true }) {
                        Label("Add Item", systemImage: "plus")
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()

                // Wishlist items list
                List(selection: $selectedItem) {
                    ForEach(viewModel.wishlistItems, id: \.id) { item in
                        WishlistItemRow(item: item)
                            .tag(item)
                            .contextMenu {
                                Button(action: { moveToCollection(item) }) {
                                    Label("Move to Collection", systemImage: "arrow.right.circle")
                                }

                                Button(role: .destructive, action: { deleteItem(item) }) {
                                    Label("Delete", systemImage: "trash")
                                }
                            }
                    }
                }
                .listStyle(.inset)

                // Empty state
                if viewModel.wishlistItems.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "heart")
                            .font(.system(size: 64))
                            .foregroundColor(.secondary)

                        Text("Your wishlist is empty")
                            .font(.title2)
                            .foregroundColor(.secondary)

                        Text("Add items you want to acquire")
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)

                        Button(action: { showingAddItem = true }) {
                            Label("Add First Item", systemImage: "plus")
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.top, 8)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }

                // Status bar
                if !viewModel.wishlistItems.isEmpty {
                    VStack(spacing: 4) {
                        HStack {
                            Text("\(viewModel.wishlistItems.count) items")
                            Spacer()
                            let totalTargetValue = viewModel.wishlistItems.compactMap { $0.targetPrice }.reduce(0, +)
                            if totalTargetValue > 0 {
                                Text("Target value: \(String(format: "$%.2f", totalTargetValue))")
                            }
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    .background(Color(.windowBackgroundColor).opacity(0.8))
                }
            }
            .navigationTitle("Wishlist Management")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showingAddItem) {
                AddEditWishlistView(item: nil)
            }
            .sheet(item: $selectedItem) { item in
                AddEditWishlistView(item: item)
            }
            .onAppear {
                viewModel.setModelContext(modelContext)
            }
        }
        .frame(minWidth: 600, minHeight: 500)
    }

    private func moveToCollection(_ item: WishlistItem) {
        if let figure = viewModel.moveWishlistToCollection(item) {
            // Could show a success message or navigate to the new figure
            print("Moved \(item.name) to collection")
        }
    }

    private func deleteItem(_ item: WishlistItem) {
        viewModel.deleteWishlistItem(item)
    }
}

struct WishlistItemRow: View {
    let item: WishlistItem

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(item.name)
                    .font(.headline)

                Spacer()

                // Priority indicator
                Circle()
                    .fill(item.priorityColor)
                    .frame(width: 12, height: 12)
                    .overlay(
                        Text(item.priority.prefix(1).uppercased())
                            .font(.caption2)
                            .foregroundColor(.white)
                    )
            }

            HStack(spacing: 12) {
                if let series = item.series {
                    Text(series)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let wave = item.wave {
                    Text("•")
                        .foregroundColor(.secondary)
                    Text(wave)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let manufacturer = item.manufacturer {
                    Text("•")
                        .foregroundColor(.secondary)
                    Text(manufacturer)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            HStack {
                Text(item.displayYear)
                    .font(.caption)
                    .foregroundColor(.secondary)

                if let targetPrice = item.targetPrice {
                    Text("•")
                        .foregroundColor(.secondary)
                    Text("Target: \(item.displayTargetPrice)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    WishlistView()
        .modelContainer(PersistenceController.preview.container)
}