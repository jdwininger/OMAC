//
//  CollectionSidebar.swift
//  OMAC
//
//  Created on 2025-11-27
//  Sidebar view showing the collection list
//

import SwiftUI

struct CollectionSidebar: View {
    @Environment(\.modelContext) private var modelContext
    @StateObject private var viewModel = CollectionViewModel()
    @Binding var selectedFigure: ActionFigure?

    @State private var showingAddFigure = false
    @State private var searchText = ""

    var body: some View {
        VStack(spacing: 0) {
            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                TextField("Search figures...", text: $searchText)
                    .textFieldStyle(.plain)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(Color(.textBackgroundColor))

            // Toolbar
            HStack {
                Button(action: { showingAddFigure = true }) {
                    Label("Add Figure", systemImage: "plus")
                }
                .buttonStyle(.borderedProminent)

                Spacer()

                Menu {
                    Picker("Sort by", selection: $viewModel.sortOption) {
                        ForEach(SortOption.allCases, id: \.self) { option in
                            Text(option.displayName).tag(option)
                        }
                    }

                    Button(action: { viewModel.sortAscending.toggle() }) {
                        Label(
                            viewModel.sortAscending ? "Ascending" : "Descending",
                            systemImage: viewModel.sortAscending ? "arrow.up" : "arrow.down"
                        )
                    }
                } label: {
                    Label("Sort", systemImage: "arrow.up.arrow.down")
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)

            // Collection list
            List(selection: $selectedFigure) {
                ForEach(Array(viewModel.filteredFigures.enumerated()), id: \.element.id) { index, figure in
                    FigureRowView(figure: figure)
                        .tag(figure)
                        .listRowBackground(
                            index % 2 == 0 ?
                                Color(.controlBackgroundColor).opacity(0.2) :
                                Color(.controlBackgroundColor).opacity(0.05)
                        )
                }
            }
            .listStyle(.sidebar)

            // Status bar
            VStack(spacing: 4) {
                HStack {
                    Text("\(viewModel.collectionStats.total) figures")
                    Spacer()
                    Text("\(viewModel.collectionStats.withPhotos) with photos")
                }
                .font(.caption)
                .foregroundColor(.secondary)

                HStack {
                    Text("\(viewModel.collectionStats.wishlistCount) wishlist")
                    Spacer()
                    if viewModel.collectionStats.totalValue > 0 {
                        Text("Total value: \(String(format: "$%.2f", viewModel.collectionStats.totalValue))")
                    }
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(Color(.windowBackgroundColor).opacity(0.8))
        }
        .sheet(isPresented: $showingAddFigure) {
            AddEditFigureView(figure: nil)
        }
        .onChange(of: showingAddFigure) { oldValue, newValue in
            if !newValue && oldValue {
                // Sheet was dismissed, refresh the data
                viewModel.loadFigures()
            }
        }
        .onAppear {
            viewModel.setModelContext(modelContext)
        }
        .onChange(of: searchText) { _, newValue in
            viewModel.searchText = newValue
        }
    }
}

struct FigureRowView: View {
    let figure: ActionFigure

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(figure.name)
                .font(.headline)

            HStack(spacing: 12) {
                if let series = figure.series {
                    Text(series)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let wave = figure.wave {
                    Text("•")
                        .foregroundColor(.secondary)
                    Text(wave)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let manufacturer = figure.manufacturer {
                    Text("•")
                        .foregroundColor(.secondary)
                    Text(manufacturer)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            HStack {
                Text(figure.displayYear)
                    .font(.caption)
                    .foregroundColor(.secondary)

                if figure.photoCount > 0 {
                    Text("•")
                        .foregroundColor(.secondary)
                    Image(systemName: "photo")
                        .font(.caption)
                    Text("\(figure.photoCount)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    CollectionSidebar(selectedFigure: .constant(nil))
        .environment(\.modelContext, PersistenceController.preview.container.mainContext)
        .frame(width: 300, height: 600)
}