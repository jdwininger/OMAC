//
//  ContentView.swift
//  OMAC
//
//  Created on 2025-11-27
//  Main application view with sidebar and detail layout
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = CollectionViewModel()
    @State private var selectedFigure: ActionFigure?
    @State private var showingWishlist = false
    @State private var showingImportExport = false

    var body: some View {
        NavigationSplitView {
            // Sidebar - Collection list
            CollectionSidebar(selectedFigure: $selectedFigure)
                .navigationTitle("OMAC Collection")
                .toolbar {
                    ToolbarItem {
                        Button(action: { showingWishlist = true }) {
                            Label("Wishlist", systemImage: "heart")
                        }
                    }
                    ToolbarItem {
                        Button(action: { showingImportExport = true }) {
                            Label("Import/Export", systemImage: "arrow.up.arrow.down")
                        }
                    }
                }
        } detail: {
            // Detail view - Figure details or welcome
            if let figure = selectedFigure {
                FigureDetailView(figure: figure)
            } else {
                WelcomeView()
            }
        }
        .sheet(isPresented: $showingWishlist) {
            WishlistView()
        }
        .sheet(isPresented: $showingImportExport) {
            ImportExportView()
        }
        .frame(minWidth: 800, minHeight: 600)
    }
}

struct WelcomeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "figure.wave")
                .font(.system(size: 64))
                .foregroundColor(.secondary)

            Text("Welcome to OMAC")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("One 'Mazing ActionFigure Catalog")
                .font(.title2)
                .foregroundColor(.secondary)

            Text("Select an action figure from the sidebar to view details, or add a new one to get started.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview {
    ContentView()
        .modelContainer(for: [ActionFigure.self, Photo.self, WishlistItem.self])
}